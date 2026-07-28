from compas_pb.generated import message_pb2 as _message_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AttributeColumn(_message.Message):
    __slots__ = ("name", "indices", "kind", "doubles", "ints", "bools", "values")
    NAME_FIELD_NUMBER: _ClassVar[int]
    INDICES_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    DOUBLES_FIELD_NUMBER: _ClassVar[int]
    INTS_FIELD_NUMBER: _ClassVar[int]
    BOOLS_FIELD_NUMBER: _ClassVar[int]
    VALUES_FIELD_NUMBER: _ClassVar[int]
    name: str
    indices: _containers.RepeatedScalarFieldContainer[int]
    kind: int
    doubles: _containers.RepeatedScalarFieldContainer[float]
    ints: _containers.RepeatedScalarFieldContainer[int]
    bools: _containers.RepeatedScalarFieldContainer[bool]
    values: _containers.RepeatedCompositeFieldContainer[_message_pb2.AnyData]
    def __init__(self, name: _Optional[str] = ..., indices: _Optional[_Iterable[int]] = ..., kind: _Optional[int] = ..., doubles: _Optional[_Iterable[float]] = ..., ints: _Optional[_Iterable[int]] = ..., bools: _Optional[_Iterable[bool]] = ..., values: _Optional[_Iterable[_Union[_message_pb2.AnyData, _Mapping]]] = ...) -> None: ...

class MeshData(_message.Message):
    __slots__ = ("guid", "name", "vertices", "face_vertices", "face_sizes", "attributes", "vertex_attribute_columns", "face_attribute_columns", "edge_attribute_columns", "edge_keys", "default_vertex_attributes", "default_face_attributes", "default_edge_attributes")
    class AttributesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _message_pb2.AnyData
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_message_pb2.AnyData, _Mapping]] = ...) -> None: ...
    class DefaultVertexAttributesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _message_pb2.AnyData
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_message_pb2.AnyData, _Mapping]] = ...) -> None: ...
    class DefaultFaceAttributesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _message_pb2.AnyData
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_message_pb2.AnyData, _Mapping]] = ...) -> None: ...
    class DefaultEdgeAttributesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _message_pb2.AnyData
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_message_pb2.AnyData, _Mapping]] = ...) -> None: ...
    GUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    VERTICES_FIELD_NUMBER: _ClassVar[int]
    FACE_VERTICES_FIELD_NUMBER: _ClassVar[int]
    FACE_SIZES_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    VERTEX_ATTRIBUTE_COLUMNS_FIELD_NUMBER: _ClassVar[int]
    FACE_ATTRIBUTE_COLUMNS_FIELD_NUMBER: _ClassVar[int]
    EDGE_ATTRIBUTE_COLUMNS_FIELD_NUMBER: _ClassVar[int]
    EDGE_KEYS_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_VERTEX_ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_FACE_ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_EDGE_ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    guid: str
    name: str
    vertices: _containers.RepeatedScalarFieldContainer[float]
    face_vertices: _containers.RepeatedScalarFieldContainer[int]
    face_sizes: _containers.RepeatedScalarFieldContainer[int]
    attributes: _containers.MessageMap[str, _message_pb2.AnyData]
    vertex_attribute_columns: _containers.RepeatedCompositeFieldContainer[AttributeColumn]
    face_attribute_columns: _containers.RepeatedCompositeFieldContainer[AttributeColumn]
    edge_attribute_columns: _containers.RepeatedCompositeFieldContainer[AttributeColumn]
    edge_keys: _containers.RepeatedCompositeFieldContainer[_message_pb2.AnyData]
    default_vertex_attributes: _containers.MessageMap[str, _message_pb2.AnyData]
    default_face_attributes: _containers.MessageMap[str, _message_pb2.AnyData]
    default_edge_attributes: _containers.MessageMap[str, _message_pb2.AnyData]
    def __init__(self, guid: _Optional[str] = ..., name: _Optional[str] = ..., vertices: _Optional[_Iterable[float]] = ..., face_vertices: _Optional[_Iterable[int]] = ..., face_sizes: _Optional[_Iterable[int]] = ..., attributes: _Optional[_Mapping[str, _message_pb2.AnyData]] = ..., vertex_attribute_columns: _Optional[_Iterable[_Union[AttributeColumn, _Mapping]]] = ..., face_attribute_columns: _Optional[_Iterable[_Union[AttributeColumn, _Mapping]]] = ..., edge_attribute_columns: _Optional[_Iterable[_Union[AttributeColumn, _Mapping]]] = ..., edge_keys: _Optional[_Iterable[_Union[_message_pb2.AnyData, _Mapping]]] = ..., default_vertex_attributes: _Optional[_Mapping[str, _message_pb2.AnyData]] = ..., default_face_attributes: _Optional[_Mapping[str, _message_pb2.AnyData]] = ..., default_edge_attributes: _Optional[_Mapping[str, _message_pb2.AnyData]] = ...) -> None: ...

class FaceData(_message.Message):
    __slots__ = ("vertex_indices",)
    VERTEX_INDICES_FIELD_NUMBER: _ClassVar[int]
    vertex_indices: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, vertex_indices: _Optional[_Iterable[int]] = ...) -> None: ...

class PolyhedronData(_message.Message):
    __slots__ = ("guid", "name", "vertices", "faces")
    GUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    VERTICES_FIELD_NUMBER: _ClassVar[int]
    FACES_FIELD_NUMBER: _ClassVar[int]
    guid: str
    name: str
    vertices: _containers.RepeatedScalarFieldContainer[float]
    faces: _containers.RepeatedCompositeFieldContainer[FaceData]
    def __init__(self, guid: _Optional[str] = ..., name: _Optional[str] = ..., vertices: _Optional[_Iterable[float]] = ..., faces: _Optional[_Iterable[_Union[FaceData, _Mapping]]] = ...) -> None: ...

class GraphData(_message.Message):
    __slots__ = ("guid", "name", "node_keys", "node_attributes", "attributes", "default_node_attributes", "default_edge_attributes", "edge_u", "edge_v", "edge_attributes")
    class AttributesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _message_pb2.AnyData
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_message_pb2.AnyData, _Mapping]] = ...) -> None: ...
    class DefaultNodeAttributesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _message_pb2.AnyData
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_message_pb2.AnyData, _Mapping]] = ...) -> None: ...
    class DefaultEdgeAttributesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _message_pb2.AnyData
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_message_pb2.AnyData, _Mapping]] = ...) -> None: ...
    GUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_KEYS_FIELD_NUMBER: _ClassVar[int]
    NODE_ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_NODE_ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_EDGE_ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    EDGE_U_FIELD_NUMBER: _ClassVar[int]
    EDGE_V_FIELD_NUMBER: _ClassVar[int]
    EDGE_ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    guid: str
    name: str
    node_keys: _containers.RepeatedCompositeFieldContainer[_message_pb2.AnyData]
    node_attributes: _containers.RepeatedCompositeFieldContainer[AttributeColumn]
    attributes: _containers.MessageMap[str, _message_pb2.AnyData]
    default_node_attributes: _containers.MessageMap[str, _message_pb2.AnyData]
    default_edge_attributes: _containers.MessageMap[str, _message_pb2.AnyData]
    edge_u: _containers.RepeatedScalarFieldContainer[int]
    edge_v: _containers.RepeatedScalarFieldContainer[int]
    edge_attributes: _containers.RepeatedCompositeFieldContainer[AttributeColumn]
    def __init__(self, guid: _Optional[str] = ..., name: _Optional[str] = ..., node_keys: _Optional[_Iterable[_Union[_message_pb2.AnyData, _Mapping]]] = ..., node_attributes: _Optional[_Iterable[_Union[AttributeColumn, _Mapping]]] = ..., attributes: _Optional[_Mapping[str, _message_pb2.AnyData]] = ..., default_node_attributes: _Optional[_Mapping[str, _message_pb2.AnyData]] = ..., default_edge_attributes: _Optional[_Mapping[str, _message_pb2.AnyData]] = ..., edge_u: _Optional[_Iterable[int]] = ..., edge_v: _Optional[_Iterable[int]] = ..., edge_attributes: _Optional[_Iterable[_Union[AttributeColumn, _Mapping]]] = ...) -> None: ...
