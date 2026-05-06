from compas_pb.generated import geometry_pb2 as _geometry_pb2
from compas_pb.generated import message_pb2 as _message_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FaceList(_message.Message):
    __slots__ = ("indices",)
    INDICES_FIELD_NUMBER: _ClassVar[int]
    indices: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, indices: _Optional[_Iterable[int]] = ...) -> None: ...

class MeshData(_message.Message):
    __slots__ = ("guid", "name", "vertices", "faces", "attributes", "vertex_attributes", "face_attributes", "edge_attributes", "default_vertex_attributes", "default_face_attributes", "default_edge_attributes")
    GUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    VERTICES_FIELD_NUMBER: _ClassVar[int]
    FACES_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    VERTEX_ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    FACE_ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    EDGE_ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_VERTEX_ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_FACE_ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_EDGE_ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    guid: str
    name: str
    vertices: _containers.RepeatedCompositeFieldContainer[_geometry_pb2.PointData]
    faces: _containers.RepeatedCompositeFieldContainer[FaceList]
    attributes: _message_pb2.DictData
    vertex_attributes: _message_pb2.DictData
    face_attributes: _message_pb2.DictData
    edge_attributes: _message_pb2.DictData
    default_vertex_attributes: _message_pb2.DictData
    default_face_attributes: _message_pb2.DictData
    default_edge_attributes: _message_pb2.DictData
    def __init__(self, guid: _Optional[str] = ..., name: _Optional[str] = ..., vertices: _Optional[_Iterable[_Union[_geometry_pb2.PointData, _Mapping]]] = ..., faces: _Optional[_Iterable[_Union[FaceList, _Mapping]]] = ..., attributes: _Optional[_Union[_message_pb2.DictData, _Mapping]] = ..., vertex_attributes: _Optional[_Union[_message_pb2.DictData, _Mapping]] = ..., face_attributes: _Optional[_Union[_message_pb2.DictData, _Mapping]] = ..., edge_attributes: _Optional[_Union[_message_pb2.DictData, _Mapping]] = ..., default_vertex_attributes: _Optional[_Union[_message_pb2.DictData, _Mapping]] = ..., default_face_attributes: _Optional[_Union[_message_pb2.DictData, _Mapping]] = ..., default_edge_attributes: _Optional[_Union[_message_pb2.DictData, _Mapping]] = ...) -> None: ...

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
    vertices: _containers.RepeatedCompositeFieldContainer[_geometry_pb2.PointData]
    faces: _containers.RepeatedCompositeFieldContainer[FaceData]
    def __init__(self, guid: _Optional[str] = ..., name: _Optional[str] = ..., vertices: _Optional[_Iterable[_Union[_geometry_pb2.PointData, _Mapping]]] = ..., faces: _Optional[_Iterable[_Union[FaceData, _Mapping]]] = ...) -> None: ...

class GraphData(_message.Message):
    __slots__ = ("guid", "name", "nodes", "edges", "attributes", "default_node_attributes", "default_edge_attributes")
    GUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NODES_FIELD_NUMBER: _ClassVar[int]
    EDGES_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_NODE_ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_EDGE_ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    guid: str
    name: str
    nodes: _message_pb2.DictData
    edges: _message_pb2.DictData
    attributes: _message_pb2.DictData
    default_node_attributes: _message_pb2.DictData
    default_edge_attributes: _message_pb2.DictData
    def __init__(self, guid: _Optional[str] = ..., name: _Optional[str] = ..., nodes: _Optional[_Union[_message_pb2.DictData, _Mapping]] = ..., edges: _Optional[_Union[_message_pb2.DictData, _Mapping]] = ..., attributes: _Optional[_Union[_message_pb2.DictData, _Mapping]] = ..., default_node_attributes: _Optional[_Union[_message_pb2.DictData, _Mapping]] = ..., default_edge_attributes: _Optional[_Union[_message_pb2.DictData, _Mapping]] = ...) -> None: ...
