from collections.abc import Iterator
from logging import Logger, getLogger
import logging
from signal import SIGINT, SIGTERM, signal
from threading import Event, Thread
from time import sleep, time
from uuid import uuid4
from heapq import merge

from coordinator_pb2 import (
    HeartbeatAck,
    HeartbeatPing,
    TaskAssignment,
    TaskRequest,
    TaskStatusAck,
    TaskStatusReport,
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
        self._task_thread = Thread(target=self._task_daemon, daemon=True)

    def start(self):
        """
        Starts the worker and enters the main polling loop
        """
        self.logger.info("Starting up heartbeat thread for worker id=%s", self.id)
        self._heartbeat_thread.start()
        self.logger.info("Starting up task thread for worker id=%s", self.id)
        self._task_thread.start()

    def do_log_task_ack(self, ack: bool, task_id, job_id):
        if ack:
            self.logger.info(
                "Coordinator acknowledged worker id=%s completed task id=%s, job id=%s",
                self.id,
                task_id,
                job_id,
            )
        else:
            self.logger.warning(
                "No acknowledgement for task id=%s, job id=%s, worker %s",
                task_id,
                job_id,
                self.id,
            )

    def do_log_task_start(self, task_id: str, job_id: str) -> None:
        self.logger.info(
            "Worker id=%s commencing sorting task id=%s, job id=%s",
            self.id,
            task_id,
            job_id,
        )

    def do_map(self, input_data: list[int], task_id: str, job_id: str) -> None:
        self.do_log_task_start(task_id, job_id)
        result: list[int] = sorted(input_data)
        response: TaskStatusAck = self.stub.ReportTaskStatus(
            TaskStatusReport(
                task_id=task_id, worker_id=self.id, success=True, result=result
            )
        )
        self.do_log_task_ack(response.acknowledged, task_id, job_id)

    def do_reduce(self, left: list[int], right: list[int], task_id: str, job_id: str):
        self.do_log_task_start(task_id, job_id)
        result: list[int] = list(merge(left, right))
        response: TaskStatusAck = self.stub.ReportTaskStatus(
            TaskStatusReport(
                task_id=task_id, worker_id=self.id, success=True, result=result
            )
        )
        self.do_log_task_ack(response.acknowledged, task_id, job_id)

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
                type: TaskType = task_response.type
                job_id: str = task_response.job_id
                task_id: str = task_response.task_id
                match type:
                    case TaskType.MAP:
                        input_data = list(task_response.input[0].items)
                        self.do_map(
                            input_data=input_data, task_id=task_id, job_id=job_id
                        )
                    case TaskType.REDUCE:
                        left = list(task_response.input[0].items)
                        right = list(task_response.input[1].items)
                        self.do_reduce(
                            left=left, right=right, task_id=task_id, job_id=job_id
                        )
                    case TaskType.IDLE | None:
                        self.logger.info(
                            "No task assigned for worker id=%s, idling before next poll",
                            self.id,
                        )
                        self.shutdown_event.wait(1.0)

            except RpcError as e:
                if not self.shutdown_event.is_set():
                    self.logger.error(
                        "Disconnected from Coordinator Service: %s", e.details()
                    )
                    self.shutdown_event.wait(2.0)

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
    max_message_size = 100 * 1024 * 1024
    channel = insecure_channel(
        "localhost:50051",
        options=[
            ("grpc.max_send_message_length", max_message_size),
            ("grpc.max_receive_message_length", max_message_size),
        ],
    )
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
