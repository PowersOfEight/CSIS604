from dataclasses import dataclass, field
from logging import getLogger
from queue import Empty, Queue
from threading import Event, Lock
from uuid import uuid4
from coordinator_pb2 import IntegerArray, TaskType
from enum import Enum
from pathlib import Path
import json


class TaskState(Enum):
    UNASSIGNED = 0
    IN_PROGRESS = 1
    COMPLETED = 2


class JobPhase(Enum):
    MAP = 0
    REDUCE = 1
    COMPLETE = 2


@dataclass
class Task:
    task_id: str
    job_id: str
    task_type: TaskType
    input: list[IntegerArray]
    results: list[int] | None
    state: TaskState = TaskState.UNASSIGNED


@dataclass
class Job:
    job_id: str
    job_result: list[int] | None
    num_items: int  # Crucial to figuring out if job is completed
    phase: JobPhase = JobPhase.MAP
    map_q: Queue[Task] = field(default_factory=Queue)
    map_results: Queue[list[int]] = field(default_factory=Queue)
    reduce_q: Queue[Task] = field(default_factory=Queue)
    reduce_buffer: Queue[list[int]] = field(default_factory=Queue)


class JobManager:
    def __init__(self, shutdown_event: Event, result_dir: str = "results") -> None:
        self.shutdown_event = shutdown_event
        self.logger = getLogger(self.__class__.__name__)
        self.lock: Lock = Lock()  # lock for the job and task objects

        # Centralize the state
        self.tasks: dict[str, Task] = {}
        self.jobs: dict[str, Job] = {}
        self.unassigned_task_q: Queue[Task] = Queue()
        self.result_dir: str = result_dir

    def get_next_unassigned_task(self, worker_id: str) -> Task | None:
        """
        Pops the next available task from the queue, marks it as IN_PROGRESS,
        and returns it. Returns `None` if no tasks are available
        """
        try:
            task: Task = self.unassigned_task_q.get_nowait()
        except Empty:
            return None

        with self.lock:
            task.state = TaskState.IN_PROGRESS
            self.logger.info(
                "Assigned task id=%s (type=%s) of job id=%s to worker id=%s",
                task.task_id,
                TaskType.Name(task.task_type),
                task.job_id,
                worker_id,
            )
            return task

    def revoke_task_assignment(self, task: Task | None) -> None:
        """
        Revokes the task assignment, setting the state to `UNASSIGNED` and
        place it back in the queue
        """
        if task is None:
            return
        with self.lock:
            task.state = TaskState.UNASSIGNED
        self.logger.warning(
            "Revoking assignment for task id=%s of job id=%s returning to queue",
            task.task_id,
            task.job_id,
        )
        self.unassigned_task_q.put(task)

    def load_job_file(self, file_path: str, chunk_size=100000):
        """
        Loads a single JSON file of integers, chunks it into MAP tasks, and queues
        them for worker assignment
        """
        path_obj = Path(file_path)
        job_id = path_obj.stem
        self.logger.info(
            "Loading job from file %s (assigned job_id=%s)", file_path, job_id
        )

        # Read the file
        try:
            with open(file_path, "r") as input_file:
                data = json.load(input_file)
        except Exception as e:
            self.logger.error("Failed to load job file %s: %s", file_path, e)
            raise

        num_items = len(data)
        self.logger.info(
            "Loaded %d integers. Slicing into chunks of %d...", num_items, chunk_size
        )

        with self.lock:
            job = Job(
                job_id=job_id, job_result=None, num_items=num_items, phase=JobPhase.MAP
            )
            self.jobs[job_id] = job

            map_task_count = 0

            for i in range(0, num_items, chunk_size):
                chunk = data[i : i + chunk_size]
                task_id = str(uuid4())

                task = Task(
                    task_id=task_id,
                    job_id=job_id,
                    task_type=TaskType.MAP,
                    input=[IntegerArray(items=chunk)],
                    results=None,
                    state=TaskState.UNASSIGNED,
                )

                self.tasks[task_id] = task

                self.unassigned_task_q.put(task)
                map_task_count += 1

            self.logger.info(
                "Successfully created and queued %d map tasks for job_id=%s",
                map_task_count,
                job_id,
            )
