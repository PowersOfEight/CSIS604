from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TaskType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    IDLE: _ClassVar[TaskType]
    MAP: _ClassVar[TaskType]
    REDUCE: _ClassVar[TaskType]
IDLE: TaskType
MAP: TaskType
REDUCE: TaskType

class TaskRequest(_message.Message):
    __slots__ = ("worker_id",)
    WORKER_ID_FIELD_NUMBER: _ClassVar[int]
    worker_id: str
    def __init__(self, worker_id: _Optional[str] = ...) -> None: ...

class IntegerArray(_message.Message):
    __slots__ = ("items",)
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, items: _Optional[_Iterable[int]] = ...) -> None: ...

class TaskAssignment(_message.Message):
    __slots__ = ("task_id", "job_id", "type", "input")
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    INPUT_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    job_id: str
    type: TaskType
    input: _containers.RepeatedCompositeFieldContainer[IntegerArray]
    def __init__(self, task_id: _Optional[str] = ..., job_id: _Optional[str] = ..., type: _Optional[_Union[TaskType, str]] = ..., input: _Optional[_Iterable[_Union[IntegerArray, _Mapping]]] = ...) -> None: ...

class TaskStatusReport(_message.Message):
    __slots__ = ("task_id", "worker_id", "success", "result")
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    WORKER_ID_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    worker_id: str
    success: bool
    result: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, task_id: _Optional[str] = ..., worker_id: _Optional[str] = ..., success: _Optional[bool] = ..., result: _Optional[_Iterable[int]] = ...) -> None: ...

class TaskStatusAck(_message.Message):
    __slots__ = ("acknowledged",)
    ACKNOWLEDGED_FIELD_NUMBER: _ClassVar[int]
    acknowledged: bool
    def __init__(self, acknowledged: _Optional[bool] = ...) -> None: ...

class HeartbeatPing(_message.Message):
    __slots__ = ("worker_id", "timestamp")
    WORKER_ID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    worker_id: str
    timestamp: int
    def __init__(self, worker_id: _Optional[str] = ..., timestamp: _Optional[int] = ...) -> None: ...

class HeartbeatAck(_message.Message):
    __slots__ = ("acknowledged",)
    ACKNOWLEDGED_FIELD_NUMBER: _ClassVar[int]
    acknowledged: bool
    def __init__(self, acknowledged: _Optional[bool] = ...) -> None: ...
