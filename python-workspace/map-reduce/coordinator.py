import logging
import signal
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from jobs import JobManager, TaskState, Task, Job
from logging import Logger, basicConfig, getLogger
from queue import Queue
from threading import Event, Lock

import grpc
from coordinator_pb2 import (
    HeartbeatAck,
    IntegerArray,
    TaskAssignment,
    TaskRequest,
    TaskType,
)
from coordinator_pb2_grpc import (
    CoordinatorServiceServicer,
    add_CoordinatorServiceServicer_to_server,
)
from grpc import RpcError


@dataclass
class WorkerInfo:
    last_seen: float
    is_active: bool = True
    assignment: Task | None = None


class CoordinatorService(CoordinatorServiceServicer):
    def __init__(self, shutdown_event: Event, heartbeat_timeout: float = 5.0) -> None:
        # Initialize logging
        self.logger: Logger = getLogger(self.__class__.__name__)
        self.logger.debug("Initializing %s", self.__class__.__name__)

        # Shudown event detection between threads
        self.shutdown_event = shutdown_event

        # This lock is for the workers
        # Mutual exclusion between threads
        self.lock: Lock = Lock()

        # Constant for the class
        self.heartbeat_timeout: float = heartbeat_timeout

        # Internal coordination state
        self.workers: dict[str, WorkerInfo] = {}
        self.job_manager = JobManager(shutdown_event=shutdown_event)

        # Start the daemon
        self.daemon = threading.Thread(target=self._worker_health_daemon, daemon=True)
        self.daemon.start()

        self.logger.info("Coordinator Initialized!")

    def AssignTask(self, request: TaskRequest, context):
        worker_id = request.worker_id
        task = self.job_manager.get_next_unassigned_task(worker_id=request.worker_id)

        if task is None:
            self.logger.debug(
                "No task found for worker id=%s.  Idling worker", request.worker_id
            )
            return TaskAssignment(
                type=TaskType.IDLE,
            )
        with self.lock:
            if worker_id in self.workers:
                self.workers[worker_id].assignment = task

        return TaskAssignment(
            task_id=task.task_id,
            job_id=task.job_id,
            type=task.task_type,
            input=task.input,
        )

    def Heartbeat(self, request_iterator, context):
        worker_id = None
        try:
            for ping in request_iterator:
                worker_id = ping.worker_id
                now = time.time()
                self.logger.debug("Recieved ping from worker id=%s", worker_id)

                # Critical Section: obtain lock
                with self.lock:
                    if worker_id not in self.workers:
                        self.workers[worker_id] = WorkerInfo(last_seen=now)
                        self.logger.info(
                            "Worker id=%s registered via heartbeat", worker_id
                        )

                    self.workers[worker_id].last_seen = now
                    self.workers[worker_id].is_active = True

                # Lock released
                yield HeartbeatAck(acknowledged=True)

                self.logger.debug(
                    "Heartbeat acknowledged for worker with id=%s at time %.3f (timestamp=%d)",
                    worker_id,
                    now,
                    ping.timestamp,
                )
                if self.shutdown_event.is_set():
                    break

        except RpcError as e:
            self.logger.error("Error in heartbeat detection: %s", e)
        finally:
            if worker_id:
                self.logger.warning(
                    "Heartbeat stream closed for worker id=%s", worker_id
                )

    def _worker_health_daemon(self):
        self.logger.debug("Starting health daemon")
        while not self.shutdown_event.is_set():
            now = time.time()

            with self.lock:
                for worker_id, info in list(self.workers.items()):
                    if self.shutdown_event.is_set():
                        break
                    if info.is_active and (
                        now - info.last_seen > self.heartbeat_timeout
                    ):
                        self.logger.warning(
                            "Timeout detected in worker id=%s: took more than %.2f seconds to respond",
                            worker_id,
                            now - info.last_seen,
                        )
                        info.is_active = False
                        if info.assignment is not None:
                            self.job_manager.revoke_task_assignment(info.assignment)
                            info.assignment = None
                        self.workers.pop(worker_id, None)
                        self.logger.warning("Worker id=%s removed", worker_id)
            if not self.shutdown_event.is_set():
                # sleep for 1 second
                self.shutdown_event.wait(1.0)


def serve():
    port = "50051"
    shutdown_event = Event()

    server = grpc.server(ThreadPoolExecutor(max_workers=10))

    add_CoordinatorServiceServicer_to_server(
        CoordinatorService(shutdown_event=shutdown_event), server
    )
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"Server listening on port {port}")

    def shutdown_handler(signum, frame):
        shutdown_event.set()

        cleanup = server.stop(grace=10.0)
        cleanup.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)
    server.wait_for_termination()


if __name__ == "__main__":
    basicConfig(level=logging.DEBUG)
    serve()
