from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PointData(_message.Message):
    __slots__ = ("guid", "name", "x", "y", "z")
    GUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    Z_FIELD_NUMBER: _ClassVar[int]
    guid: str
    name: str
    x: float
    y: float
    z: float
    def __init__(self, guid: _Optional[str] = ..., name: _Optional[str] = ..., x: _Optional[float] = ..., y: _Optional[float] = ..., z: _Optional[float] = ...) -> None: ...

class VectorData(_message.Message):
    __slots__ = ("guid", "name", "x", "y", "z")
    GUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    Z_FIELD_NUMBER: _ClassVar[int]
    guid: str
    name: str
    x: float
    y: float
    z: float
    def __init__(self, guid: _Optional[str] = ..., name: _Optional[str] = ..., x: _Optional[float] = ..., y: _Optional[float] = ..., z: _Optional[float] = ...) -> None: ...

class FrameData(_message.Message):
    __slots__ = ("guid", "name", "point", "xaxis", "yaxis")
    GUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    POINT_FIELD_NUMBER: _ClassVar[int]
    XAXIS_FIELD_NUMBER: _ClassVar[int]
    YAXIS_FIELD_NUMBER: _ClassVar[int]
    guid: str
    name: str
    point: PointData
    xaxis: VectorData
    yaxis: VectorData
    def __init__(self, guid: _Optional[str] = ..., name: _Optional[str] = ..., point: _Optional[_Union[PointData, _Mapping]] = ..., xaxis: _Optional[_Union[VectorData, _Mapping]] = ..., yaxis: _Optional[_Union[VectorData, _Mapping]] = ...) -> None: ...

class PlaneData(_message.Message):
    __slots__ = ("guid", "name", "point", "normal")
    GUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    POINT_FIELD_NUMBER: _ClassVar[int]
    NORMAL_FIELD_NUMBER: _ClassVar[int]
    guid: str
    name: str
    point: PointData
    normal: VectorData
    def __init__(self, guid: _Optional[str] = ..., name: _Optional[str] = ..., point: _Optional[_Union[PointData, _Mapping]] = ..., normal: _Optional[_Union[VectorData, _Mapping]] = ...) -> None: ...

class QuaternionData(_message.Message):
    __slots__ = ("guid", "name", "w", "x", "y", "z")
    GUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    W_FIELD_NUMBER: _ClassVar[int]
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    Z_FIELD_NUMBER: _ClassVar[int]
    guid: str
    name: str
    w: float
    x: float
    y: float
    z: float
    def __init__(self, guid: _Optional[str] = ..., name: _Optional[str] = ..., w: _Optional[float] = ..., x: _Optional[float] = ..., y: _Optional[float] = ..., z: _Optional[float] = ...) -> None: ...

class LineData(_message.Message):
    __slots__ = ("guid", "name", "start", "end")
    GUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    guid: str
    name: str
    start: PointData
    end: PointData
    def __init__(self, guid: _Optional[str] = ..., name: _Optional[str] = ..., start: _Optional[_Union[PointData, _Mapping]] = ..., end: _Optional[_Union[PointData, _Mapping]] = ...) -> None: ...

class CircleData(_message.Message):
    __slots__ = ("guid", "name", "radius", "frame")
    GUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    RADIUS_FIELD_NUMBER: _ClassVar[int]
    FRAME_FIELD_NUMBER: _ClassVar[int]
    guid: str
    name: str
    radius: float
    frame: FrameData
    def __init__(self, guid: _Optional[str] = ..., name: _Optional[str] = ..., radius: _Optional[float] = ..., frame: _Optional[_Union[FrameData, _Mapping]] = ...) -> None: ...

class ArcData(_message.Message):
    __slots__ = ("guid", "name", "circle", "start_angle", "end_angle")
    GUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CIRCLE_FIELD_NUMBER: _ClassVar[int]
    START_ANGLE_FIELD_NUMBER: _ClassVar[int]
    END_ANGLE_FIELD_NUMBER: _ClassVar[int]
    guid: str
    name: str
    circle: CircleData
    start_angle: float
    end_angle: float
    def __init__(self, guid: _Optional[str] = ..., name: _Optional[str] = ..., circle: _Optional[_Union[CircleData, _Mapping]] = ..., start_angle: _Optional[float] = ..., end_angle: _Optional[float] = ...) -> None: ...

class EllipseData(_message.Message):
    __slots__ = ("guid", "name", "major", "minor", "frame")
    GUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    MAJOR_FIELD_NUMBER: _ClassVar[int]
    MINOR_FIELD_NUMBER: _ClassVar[int]
    FRAME_FIELD_NUMBER: _ClassVar[int]
    guid: str
    name: str
    major: float
    minor: float
    frame: FrameData
    def __init__(self, guid: _Optional[str] = ..., name: _Optional[str] = ..., major: _Optional[float] = ..., minor: _Optional[float] = ..., frame: _Optional[_Union[FrameData, _Mapping]] = ...) -> None: ...

class ParabolaData(_message.Message):
    __slots__ = ("guid", "name", "focal", "frame")
    GUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    FOCAL_FIELD_NUMBER: _ClassVar[int]
    FRAME_FIELD_NUMBER: _ClassVar[int]
    guid: str
    name: str
    focal: float
    frame: FrameData
    def __init__(self, guid: _Optional[str] = ..., name: _Optional[str] = ..., focal: _Optional[float] = ..., frame: _Optional[_Union[FrameData, _Mapping]] = ...) -> None: ...

class HyperbolaData(_message.Message):
    __slots__ = ("guid", "name", "major", "minor", "frame")
    GUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    MAJOR_FIELD_NUMBER: _ClassVar[int]
    MINOR_FIELD_NUMBER: _ClassVar[int]
    FRAME_FIELD_NUMBER: _ClassVar[int]
    guid: str
    name: str
    major: float
    minor: float
    frame: FrameData
    def __init__(self, guid: _Optional[str] = ..., name: _Optional[str] = ..., major: _Optional[float] = ..., minor: _Optional[float] = ..., frame: _Optional[_Union[FrameData, _Mapping]] = ...) -> None: ...

class BezierData(_message.Message):
    __slots__ = ("guid", "name", "points", "degree")
    GUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    POINTS_FIELD_NUMBER: _ClassVar[int]
    DEGREE_FIELD_NUMBER: _ClassVar[int]
    guid: str
    name: str
    points: _containers.RepeatedScalarFieldContainer[float]
    degree: int
    def __init__(self, guid: _Optional[str] = ..., name: _Optional[str] = ..., points: _Optional[_Iterable[float]] = ..., degree: _Optional[int] = ...) -> None: ...

class PolylineData(_message.Message):
    __slots__ = ("guid", "name", "points")
    GUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    POINTS_FIELD_NUMBER: _ClassVar[int]
    guid: str
    name: str
    points: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, guid: _Optional[str] = ..., name: _Optional[str] = ..., points: _Optional[_Iterable[float]] = ...) -> None: ...

class PolygonData(_message.Message):
    __slots__ = ("guid", "name", "points")
    GUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    POINTS_FIELD_NUMBER: _ClassVar[int]
    guid: str
    name: str
    points: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, guid: _Optional[str] = ..., name: _Optional[str] = ..., points: _Optional[_Iterable[float]] = ...) -> None: ...

class BoxData(_message.Message):
    __slots__ = ("guid", "name", "frame", "xsize", "ysize", "zsize")
    GUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    FRAME_FIELD_NUMBER: _ClassVar[int]
    XSIZE_FIELD_NUMBER: _ClassVar[int]
    YSIZE_FIELD_NUMBER: _ClassVar[int]
    ZSIZE_FIELD_NUMBER: _ClassVar[int]
    guid: str
    name: str
    frame: FrameData
    xsize: float
    ysize: float
    zsize: float
    def __init__(self, guid: _Optional[str] = ..., name: _Optional[str] = ..., frame: _Optional[_Union[FrameData, _Mapping]] = ..., xsize: _Optional[float] = ..., ysize: _Optional[float] = ..., zsize: _Optional[float] = ...) -> None: ...

class SphereData(_message.Message):
    __slots__ = ("guid", "name", "radius", "frame")
    GUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    RADIUS_FIELD_NUMBER: _ClassVar[int]
    FRAME_FIELD_NUMBER: _ClassVar[int]
    guid: str
    name: str
    radius: float
    frame: FrameData
    def __init__(self, guid: _Optional[str] = ..., name: _Optional[str] = ..., radius: _Optional[float] = ..., frame: _Optional[_Union[FrameData, _Mapping]] = ...) -> None: ...

class CylinderData(_message.Message):
    __slots__ = ("guid", "name", "radius", "height", "frame")
    GUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    RADIUS_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    FRAME_FIELD_NUMBER: _ClassVar[int]
    guid: str
    name: str
    radius: float
    height: float
    frame: FrameData
    def __init__(self, guid: _Optional[str] = ..., name: _Optional[str] = ..., radius: _Optional[float] = ..., height: _Optional[float] = ..., frame: _Optional[_Union[FrameData, _Mapping]] = ...) -> None: ...

class ConeData(_message.Message):
    __slots__ = ("guid", "name", "radius", "height", "frame")
    GUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    RADIUS_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    FRAME_FIELD_NUMBER: _ClassVar[int]
    guid: str
    name: str
    radius: float
    height: float
    frame: FrameData
    def __init__(self, guid: _Optional[str] = ..., name: _Optional[str] = ..., radius: _Optional[float] = ..., height: _Optional[float] = ..., frame: _Optional[_Union[FrameData, _Mapping]] = ...) -> None: ...

class CapsuleData(_message.Message):
    __slots__ = ("guid", "name", "radius", "height", "frame")
    GUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    RADIUS_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    FRAME_FIELD_NUMBER: _ClassVar[int]
    guid: str
    name: str
    radius: float
    height: float
    frame: FrameData
    def __init__(self, guid: _Optional[str] = ..., name: _Optional[str] = ..., radius: _Optional[float] = ..., height: _Optional[float] = ..., frame: _Optional[_Union[FrameData, _Mapping]] = ...) -> None: ...

class TorusData(_message.Message):
    __slots__ = ("guid", "name", "radius_axis", "radius_pipe", "frame")
    GUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    RADIUS_AXIS_FIELD_NUMBER: _ClassVar[int]
    RADIUS_PIPE_FIELD_NUMBER: _ClassVar[int]
    FRAME_FIELD_NUMBER: _ClassVar[int]
    guid: str
    name: str
    radius_axis: float
    radius_pipe: float
    frame: FrameData
    def __init__(self, guid: _Optional[str] = ..., name: _Optional[str] = ..., radius_axis: _Optional[float] = ..., radius_pipe: _Optional[float] = ..., frame: _Optional[_Union[FrameData, _Mapping]] = ...) -> None: ...

class PointcloudData(_message.Message):
    __slots__ = ("guid", "name", "points")
    GUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    POINTS_FIELD_NUMBER: _ClassVar[int]
    guid: str
    name: str
    points: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, guid: _Optional[str] = ..., name: _Optional[str] = ..., points: _Optional[_Iterable[float]] = ...) -> None: ...

class TransformationData(_message.Message):
    __slots__ = ("guid", "name", "matrix")
    GUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    MATRIX_FIELD_NUMBER: _ClassVar[int]
    guid: str
    name: str
    matrix: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, guid: _Optional[str] = ..., name: _Optional[str] = ..., matrix: _Optional[_Iterable[float]] = ...) -> None: ...

class TranslationData(_message.Message):
    __slots__ = ("guid", "name", "translation_vector")
    GUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TRANSLATION_VECTOR_FIELD_NUMBER: _ClassVar[int]
    guid: str
    name: str
    translation_vector: VectorData
    def __init__(self, guid: _Optional[str] = ..., name: _Optional[str] = ..., translation_vector: _Optional[_Union[VectorData, _Mapping]] = ...) -> None: ...

class RotationData(_message.Message):
    __slots__ = ("guid", "name", "matrix")
    GUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    MATRIX_FIELD_NUMBER: _ClassVar[int]
    guid: str
    name: str
    matrix: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, guid: _Optional[str] = ..., name: _Optional[str] = ..., matrix: _Optional[_Iterable[float]] = ...) -> None: ...

class ScaleData(_message.Message):
    __slots__ = ("guid", "name", "matrix")
    GUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    MATRIX_FIELD_NUMBER: _ClassVar[int]
    guid: str
    name: str
    matrix: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, guid: _Optional[str] = ..., name: _Optional[str] = ..., matrix: _Optional[_Iterable[float]] = ...) -> None: ...

class ReflectionData(_message.Message):
    __slots__ = ("guid", "name", "matrix")
    GUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    MATRIX_FIELD_NUMBER: _ClassVar[int]
    guid: str
    name: str
    matrix: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, guid: _Optional[str] = ..., name: _Optional[str] = ..., matrix: _Optional[_Iterable[float]] = ...) -> None: ...

class ShearData(_message.Message):
    __slots__ = ("guid", "name", "matrix")
    GUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    MATRIX_FIELD_NUMBER: _ClassVar[int]
    guid: str
    name: str
    matrix: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, guid: _Optional[str] = ..., name: _Optional[str] = ..., matrix: _Optional[_Iterable[float]] = ...) -> None: ...

class ProjectionData(_message.Message):
    __slots__ = ("guid", "name", "matrix")
    GUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    MATRIX_FIELD_NUMBER: _ClassVar[int]
    guid: str
    name: str
    matrix: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, guid: _Optional[str] = ..., name: _Optional[str] = ..., matrix: _Optional[_Iterable[float]] = ...) -> None: ...
