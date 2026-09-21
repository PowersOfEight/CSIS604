# Author: James Daniel Johnson
# CWID: 20183229
# Course: CSIS 604 - Distributed Systems
# Assignment: 2.2 - Mini Map Reduce
import json
from dataclasses import dataclass, field
from enum import Enum
from json.decoder import JSONDecodeError
from logging import getLogger
from pathlib import Path
from queue import Empty, Queue
from threading import Event, Lock, Thread
from uuid import uuid4

from coordinator_pb2 import IntegerArray, TaskType


class TaskState(Enum):
    """
    The state of a task as it
    relates to assignment
    """

    UNASSIGNED = 0
    IN_PROGRESS = 1
    COMPLETED = 2


class JobPhase(Enum):
    """
    The phase of a job, determined
    by the collection of tasks
    """

    MAP = 0
    REDUCE = 1
    COMPLETE = 2


@dataclass
class Task:
    """
    The data-view representation of a Task
    """

    task_id: str
    job_id: str
    task_type: TaskType
    input: list[IntegerArray]
    results: list[int] | None
    state: TaskState = TaskState.UNASSIGNED


@dataclass
class Job:
    """
    The data-view representation of a Job
    """

    job_id: str
    job_result: list[int] | None
    num_items: int  # Crucial to figuring out if job is completed
    phase: JobPhase = JobPhase.MAP
    map_results: Queue[list[int]] = field(default_factory=Queue)
    reduce_buffer: Queue[list[int]] = field(default_factory=Queue)


def is_valid_integer_list_json_file(file_path: Path) -> bool:
    """
    Helper method to check whether the input file is
    a valid JSON-encoded list file.
    """
    try:
        with file_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            return False

        return all(
            isinstance(item, int) and not isinstance(item, bool) for item in data
        )

    except (OSError, JSONDecodeError):
        return False


class JobManager:
    """
    Manages incoming job and task lifetimes for the `MiniMapReduce`
    service. This promotes a separation of concerns by drawing a
    firm boundary between `Job` and `Task` management versus
    the coordination of task assignemnts to workers.
    ---
    """

    def __init__(
        self,
        shutdown_event: Event,
        input_dir: str = "jobs",
        result_dir: str = "results",
        chunk_size: int = 100000,
        poll_thread_wait: float = 5.0,
    ) -> None:
        self.shutdown_event = shutdown_event
        self.logger = getLogger(self.__class__.__name__)
        self.lock: Lock = Lock()  # lock for the job and task objects

        # Centralize the state
        self.tasks: dict[str, Task] = {}
        self.jobs: dict[str, Job] = {}
        self.unassigned_task_q: Queue[Task] = Queue()
        self.input_dir_path: Path = Path(input_dir)
        self.result_dir_path: Path = Path(result_dir)
        self.chunk_size: int = chunk_size
        self.poll_thread_wait = poll_thread_wait
        self._input_daemon_thread = Thread(target=self._input_poll_daemon, daemon=True)
        self._input_daemon_thread.start()

    def _input_poll_daemon(self) -> None:
        """
        Polls the input directory for new jobs.
        This daemon is intended to run on a separate thread
        """
        while not self.shutdown_event.is_set():
            self.logger.info(
                "JobManager scanning directory at %s...", self.input_dir_path
            )
            # Create the path to the dir
            self.input_dir_path.mkdir(parents=True, exist_ok=True, mode=0o755)

            # scan the directory
            for item in self.input_dir_path.glob("*.json"):
                # exit quickly if a shutdown signal is issued
                if self.shutdown_event.is_set():
                    break

                if is_valid_integer_list_json_file(item):
                    try:
                        self.load_job_file(item, chunk_size=self.chunk_size)
                        # Remove job file so that we don't load it again
                        item.unlink(missing_ok=True)
                        self.logger.info(
                            "Successfully removed job file %s after loading", item.name
                        )

                    except (OSError, JSONDecodeError) as e:
                        self.logger.error(
                            "Encountered error trying to load file %s: %s", item, e
                        )
                        continue

            if not self.shutdown_event.is_set():
                self.shutdown_event.wait(self.poll_thread_wait)

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

    def complete_task(self, task_id: str, results: list[int]) -> None:
        with self.lock:
            task: Task = self.tasks[task_id]
            task.results = results
            task.state = TaskState.COMPLETED
            job_id = task.job_id

            job: Job = self.jobs[job_id]

            # Push the completed chunk/result into the reduce buffer
            job.reduce_buffer.put(results)

            # Gather all tasks for this job to check overall progress
            job_tasks = [t for t in self.tasks.values() if t.job_id == job_id]
            all_tasks_completed = all(t.state == TaskState.COMPLETED for t in job_tasks)

            if job.phase == JobPhase.MAP:
                # Check if all MAP tasks are done
                map_tasks = [t for t in job_tasks if t.task_type == TaskType.MAP]
                if all(t.state == TaskState.COMPLETED for t in map_tasks):
                    job.phase = JobPhase.REDUCE
                    self.logger.info(
                        "Job id=%s finished MAP phase, transitioning to REDUCE phase",
                        job_id,
                    )
                    self._spawn_reduce_tasks(job)
                else:
                    # Still waiting on other map tasks to finish
                    pass

            elif job.phase == JobPhase.REDUCE:
                # Check if we are completely done (all tasks finished and only 1 master sorted list remains)
                if all_tasks_completed and job.reduce_buffer.qsize() == 1:
                    job.job_result = job.reduce_buffer.get()
                    job.phase = JobPhase.COMPLETE
                    self.logger.info(
                        "Job id=%s completed sorting successfully!", job_id
                    )
                    self._save_job_result(job)
                else:
                    # Try to spawn more reduce tasks from available buffer pairs
                    self._spawn_reduce_tasks(job)

    def _spawn_reduce_tasks(self, job: Job):
        """
        Packs pairs of sorted lists from the reduce buffer into new REDUCE tasks
        """
        while job.reduce_buffer.qsize() >= 2:
            try:
                left = job.reduce_buffer.get_nowait()
                right = job.reduce_buffer.get_nowait()
            except Empty:
                break

            task_id = str(uuid4())
            task = Task(
                task_id=task_id,
                job_id=job.job_id,
                task_type=TaskType.REDUCE,
                input=[IntegerArray(items=left), IntegerArray(items=right)],
                results=None,
                state=TaskState.UNASSIGNED,
            )

            self.tasks[task_id] = task
            self.unassigned_task_q.put(task)
            self.logger.info(
                "Created REDUCE task id=%s for job id=%s", task_id, job.job_id
            )

    def _save_job_result(self, job: Job):
        """
        Saves the final sorted integer list to the results directory
        """
        self.result_dir_path.mkdir(parents=True, exist_ok=True, mode=0o755)
        out_path = self.result_dir_path / f"{job.job_id}_sorted.json"
        try:
            with open(out_path, "w") as f:
                json.dump(job.job_result, f)
            self.logger.info(
                "Saved final sorted result for job id=%s to %s", job.job_id, out_path
            )
        except Exception as e:
            self.logger.error("Failed to save result for job id=%s: %s", job.job_id, e)

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

    def load_job_file(self, file_path: str | Path, chunk_size=100000):
        """
        Loads a single JSON file of integers, chunks it into MAP tasks, and queues
        them for worker assignment. Uses the `stem`ed file_path as the job id
        """
        path_obj = file_path if isinstance(file_path, Path) else Path(file_path)
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
            if job_id not in self.jobs:
                job = Job(
                    job_id=job_id,
                    job_result=None,
                    num_items=num_items,
                    phase=JobPhase.MAP,
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
