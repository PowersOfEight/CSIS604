from dataclasses import dataclass
from coordinator_pb2 import IntegerArray, TaskType
from enum import Enum


class TaskState(Enum):
    UNASSIGNED = 0
    IN_PROGRESS = 1
    COMPLETED = 2


@dataclass
class Task:
    task_id: str
    task_type: TaskType
    input: list[IntegerArray]
    state: TaskState = TaskState.UNASSIGNED
