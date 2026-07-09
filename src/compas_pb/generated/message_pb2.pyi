from google.protobuf import any_pb2 as _any_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AnyData(_message.Message):
    __slots__ = ("message", "value", "fallback", "int_value", "double_value", "dict_value", "list_value")
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    FALLBACK_FIELD_NUMBER: _ClassVar[int]
    INT_VALUE_FIELD_NUMBER: _ClassVar[int]
    DOUBLE_VALUE_FIELD_NUMBER: _ClassVar[int]
    DICT_VALUE_FIELD_NUMBER: _ClassVar[int]
    LIST_VALUE_FIELD_NUMBER: _ClassVar[int]
    message: _any_pb2.Any
    value: _struct_pb2.Value
    fallback: FallbackData
    int_value: int
    double_value: float
    dict_value: DictData
    list_value: ListData
    def __init__(self, message: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., value: _Optional[_Union[_struct_pb2.Value, _Mapping]] = ..., fallback: _Optional[_Union[FallbackData, _Mapping]] = ..., int_value: _Optional[int] = ..., double_value: _Optional[float] = ..., dict_value: _Optional[_Union[DictData, _Mapping]] = ..., list_value: _Optional[_Union[ListData, _Mapping]] = ...) -> None: ...

class FallbackData(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: DictData
    def __init__(self, data: _Optional[_Union[DictData, _Mapping]] = ...) -> None: ...

class ListData(_message.Message):
    __slots__ = ("items",)
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[AnyData]
    def __init__(self, items: _Optional[_Iterable[_Union[AnyData, _Mapping]]] = ...) -> None: ...

class DictData(_message.Message):
    __slots__ = ("items",)
    class ItemsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: AnyData
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[AnyData, _Mapping]] = ...) -> None: ...
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    items: _containers.MessageMap[str, AnyData]
    def __init__(self, items: _Optional[_Mapping[str, AnyData]] = ...) -> None: ...

class MessageData(_message.Message):
    __slots__ = ("data", "version")
    DATA_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    data: AnyData
    version: str
    def __init__(self, data: _Optional[_Union[AnyData, _Mapping]] = ..., version: _Optional[str] = ...) -> None: ...
