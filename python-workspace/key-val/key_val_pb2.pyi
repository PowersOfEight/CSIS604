from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PutRequest(_message.Message):
    __slots__ = ("key", "value")
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    key: str
    value: str
    def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class PutResponse(_message.Message):
    __slots__ = ("message", "success")
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    message: str
    success: bool
    def __init__(self, message: _Optional[str] = ..., success: _Optional[bool] = ...) -> None: ...

class GetRequest(_message.Message):
    __slots__ = ("key",)
    KEY_FIELD_NUMBER: _ClassVar[int]
    key: str
    def __init__(self, key: _Optional[str] = ...) -> None: ...

class GetResponse(_message.Message):
    __slots__ = ("value", "state")
    VALUE_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    value: str
    state: EntryState
    def __init__(self, value: _Optional[str] = ..., state: _Optional[_Union[EntryState, _Mapping]] = ...) -> None: ...

class DeleteRequest(_message.Message):
    __slots__ = ("key",)
    KEY_FIELD_NUMBER: _ClassVar[int]
    key: str
    def __init__(self, key: _Optional[str] = ...) -> None: ...

class DeleteResponse(_message.Message):
    __slots__ = ("message", "success")
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    message: str
    success: bool
    def __init__(self, message: _Optional[str] = ..., success: _Optional[bool] = ...) -> None: ...

class WatchRequest(_message.Message):
    __slots__ = ("key",)
    KEY_FIELD_NUMBER: _ClassVar[int]
    key: str
    def __init__(self, key: _Optional[str] = ...) -> None: ...

class WatchResponse(_message.Message):
    __slots__ = ("update",)
    UPDATE_FIELD_NUMBER: _ClassVar[int]
    update: UpdateEvent
    def __init__(self, update: _Optional[_Union[UpdateEvent, _Mapping]] = ...) -> None: ...

class EntryState(_message.Message):
    __slots__ = ("exists", "key", "value")
    EXISTS_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    exists: bool
    key: str
    value: str
    def __init__(self, exists: _Optional[bool] = ..., key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class UpdateEvent(_message.Message):
    __slots__ = ("old", "new")
    OLD_FIELD_NUMBER: _ClassVar[int]
    NEW_FIELD_NUMBER: _ClassVar[int]
    old: EntryState
    new: EntryState
    def __init__(self, old: _Optional[_Union[EntryState, _Mapping]] = ..., new: _Optional[_Union[EntryState, _Mapping]] = ...) -> None: ...
