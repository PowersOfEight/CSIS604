from collections.abc import Iterator
from logging import Logger, getLogger
import logging
from signal import SIGINT, SIGTERM, signal
import sys
from threading import Event, Thread
from time import sleep, time
from uuid import uuid4

from coordinator_pb2 import (
    IDLE,
    HeartbeatAck,
    HeartbeatPing,
    TaskAssignment,
    TaskRequest,
    TaskType,
)
from coordinator_pb2_grpc import CoordinatorServiceStub
from grpc import RpcError, insecure_channel


class Worker:
    def __init__(self, shutdown_event: Event, stub: CoordinatorServiceStub):
        self.id = str(uuid4())
        self.shutdown_event = shutdown_event
        self.stub = stub
        self.logger: Logger = getLogger(self.__class__.__name__)
        self._heartbeat_thread = Thread(target=self._heartbeat_daemon, daemon=True)

    def start(self):
        """
        Starts the worker and enters the main polling loop
        """
        self.logger.info("Starting up heartbeat thread for worker id=%s", self.id)
        self._heartbeat_thread.start()
        # self._task_daemon()  # Runs continuously
        # TODO: implement a class-level signal handler

    def _task_daemon(self):
        """
        Handles the task assignment, task completion, and task reporting
        loop for the worker
        """
        self.logger.info("Starting up task polling for worker id=%s", self.id)
        while not self.shutdown_event.is_set():
            try:
                task_response: TaskAssignment = self.stub.AssignTask(
                    TaskRequest(worker_id=self.id)
                )

                if task_response.type != IDLE:
                    # TODO: deal with task logic here
                    pass
                else:
                    # for now, just sleep and run again
                    self.shutdown_event.wait(1.0)
                    continue

            except RpcError as e:
                if not self.shutdown_event.is_set():
                    self.logger.error(
                        "Disconnected from Coordinator Service: %s", e.details()
                    )
                    sleep(2.0)

    def _heartbeat_daemon(self):
        """Continuous hearbeat daemon"""

        def heartbeat_generator() -> Iterator[HeartbeatPing]:
            while not self.shutdown_event.is_set():
                yield HeartbeatPing(worker_id=self.id, timestamp=int(time() * 1000))
                sleep(2.0)

        while not self.shutdown_event.is_set():
            try:
                self.logger.debug(
                    "Attempting heartbeat ping with Coordinator, worker id=%s",
                    self.id,
                )
                response_iterator: Iterator[HeartbeatAck] = self.stub.Heartbeat(
                    heartbeat_generator()
                )

                for response in response_iterator:
                    if not response.acknowledged:
                        self.logger.warning(
                            "Heartbeat not acknowledged by coordinator, worker id=%s",
                            self.id,
                        )
                    else:
                        self.logger.debug(
                            "Hearbeat acknowledged for worker %s", self.id
                        )

            except RpcError as e:
                self.logger.error("Heartbeat Stream Disconnected: %s", e.details())

            if not self.shutdown_event.is_set():
                self.logger.info(
                    "Worker id=%s waiting 2 seconds before attempting reconnection...",
                    self.id,
                )
                self.shutdown_event.wait(2.0)


def run():
    channel = insecure_channel("localhost:50051")
    stub = CoordinatorServiceStub(channel=channel)
    logging.basicConfig(level=logging.DEBUG)

    shutdown_event: Event = Event()

    def signal_handler(sig, frame):
        print("\nCommencing graceful shutdown")
        shutdown_event.set()

    signal(SIGINT, signal_handler)
    signal(SIGTERM, signal_handler)

    worker = Worker(shutdown_event=shutdown_event, stub=stub)

    try:
        worker.start()
        while not shutdown_event.is_set():
            sleep(1.0)
    finally:
        shutdown_event.set()
        print(f"Worker with id={worker.id} stopped")


if __name__ == "__main__":
    run()
