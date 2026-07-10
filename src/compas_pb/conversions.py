from ast import literal_eval
from uuid import UUID

from compas.datastructures import Graph
from compas.datastructures import Mesh
from compas.geometry import Arc
from compas.geometry import Bezier
from compas.geometry import Box
from compas.geometry import Capsule
from compas.geometry import Circle
from compas.geometry import Cone
from compas.geometry import Cylinder
from compas.geometry import Ellipse
from compas.geometry import Frame
from compas.geometry import Hyperbola
from compas.geometry import Line
from compas.geometry import Parabola
from compas.geometry import Plane
from compas.geometry import Point
from compas.geometry import Pointcloud
from compas.geometry import Polygon
from compas.geometry import Polyhedron
from compas.geometry import Polyline
from compas.geometry import Projection
from compas.geometry import Quaternion
from compas.geometry import Reflection
from compas.geometry import Rotation
from compas.geometry import Scale
from compas.geometry import Shear
from compas.geometry import Sphere
from compas.geometry import Torus
from compas.geometry import Transformation
from compas.geometry import Translation
from compas.geometry import Vector

from compas_pb.core import _deserialize_any
from compas_pb.core import _deserialize_dict
from compas_pb.core import _serialize_dict
from compas_pb.core import _serializer_any
from compas_pb.generated import datastructures_pb2
from compas_pb.generated import geometry_pb2
from compas_pb.generated import message_pb2


def _fill_attr_map(dest_map, data_dict):
    """Populate a ``map<string, AnyData>`` proto field from a Python dict.

    Empty dicts are skipped, so absent/empty attribute maps cost zero bytes on the wire.
    """
    if data_dict:
        dest_map.MergeFrom(_serialize_dict(data_dict).items)


def _read_attr_map(src_map):
    """Read a ``map<string, AnyData>`` proto field back into a Python dict."""
    wrapper = message_pb2.DictData()
    wrapper.items.MergeFrom(src_map)
    return _deserialize_dict(wrapper)


def _extend_flat_points(dest_field, points):
    """Append points to a flat ``repeated double`` field as consecutive x, y, z triplets.

    This replaces a full ``PointData`` message per point (which also carried a per-point
    UUID/name) with three packed doubles, the dominant size/speed win for point-heavy types.
    """
    for pt in points:
        x, y, z = pt
        dest_field.extend((x, y, z))


def _flat_points_to_lists(flat):
    """Read a flat ``repeated double`` field back into a list of ``[x, y, z]`` lists."""
    return [[flat[i], flat[i + 1], flat[i + 2]] for i in range(0, len(flat), 3)]


_COORD_KEYS = ("x", "y", "z")


def _fill_attribute_columns(dest, element_attrs, index_map, count):
    """Write per-element attribute dicts column-wise into a repeated ``AttributeColumn`` field.

    Instead of a dict (and repeated attribute-name string) per element, each attribute name is
    stored once with a packed value array. Numeric columns use packed ``double``/``int``/``bool``
    arrays (no per-value framing, bulk-decodable); mixed columns fall back to ``AnyData``. A
    dense column (every element in order) stores no ``indices``.
    """
    columns = {}  # name -> list of (index, value), in element order
    for key, attr in element_attrs.items():
        idx = index_map[key]
        for name, value in attr.items():
            if name in _COORD_KEYS:
                continue
            columns.setdefault(name, []).append((idx, value))

    for name, pairs in columns.items():
        pairs.sort(key=lambda p: p[0])
        indices = [i for i, _ in pairs]
        values = [v for _, v in pairs]
        col = dest.add()
        col.name = name
        if indices != list(range(count)):  # sparse: record which elements carry the attribute
            col.indices.extend(indices)
        if values and all(type(v) is float for v in values):
            col.kind = 0
            col.doubles.extend(values)
        elif values and all(type(v) is int for v in values):  # type() is int excludes bool
            col.kind = 1
            col.ints.extend(values)
        elif values and all(type(v) is bool for v in values):
            col.kind = 2
            col.bools.extend(values)
        else:
            col.kind = 3
            for v in values:
                col.values.append(_serializer_any(v))


def _read_attribute_columns(columns, index_to_key, target):
    """Apply column-wise attributes back onto per-element attribute dicts.

    ``index_to_key`` maps an integer index to the element key; ``target`` maps element key to
    the mutable attribute dict to update.
    """
    for col in columns:
        if col.kind == 0:
            values = list(col.doubles)
        elif col.kind == 1:
            values = list(col.ints)
        elif col.kind == 2:
            values = list(col.bools)
        else:
            values = [_deserialize_any(v) for v in col.values]
        indices = list(col.indices) if col.indices else range(len(values))
        for idx, value in zip(indices, values):
            target[index_to_key[idx]][col.name] = value

from .registry import pb_deserializer
from .registry import pb_serializer

# =============================================================================
# Point
# =============================================================================


@pb_serializer(Point)
def point_to_pb(obj: Point) -> geometry_pb2.PointData:
    """
    Convert a COMPAS Point to protobuf message.

    Parameters
    ----------
    obj : Point
        The COMPAS Point object to serialize.

    Returns
    -------
    geometry_pb2.PointData
        The protobuf message representing the Point.
    """
    proto_data = geometry_pb2.PointData()
    if obj._guid is not None:
        proto_data.guid = str(obj._guid)
    if obj._name is not None:
        proto_data.name = obj.name
    proto_data.x = obj.x
    proto_data.y = obj.y
    proto_data.z = obj.z
    return proto_data


@pb_deserializer(geometry_pb2.PointData)
def point_from_pb(proto_data: geometry_pb2.PointData) -> Point:
    """
    Convert a protobuf message to COMPAS Point.

    Parameters
    ----------
    proto_data : geometry_pb2.PointData
        The protobuf message representing a Point.

    Returns
    -------
    Point
        The deserialized COMPAS Point object.
    """
    result = Point(x=proto_data.x, y=proto_data.y, z=proto_data.z, name=(proto_data.name or None))
    if proto_data.guid:
        result._guid = UUID(proto_data.guid)
    return result


# =============================================================================
# Line
# =============================================================================


@pb_serializer(Line)
def line_to_pb(line_obj: Line) -> geometry_pb2.LineData:
    """
    Convert a COMPAS Line to protobuf message.

    Parameters
    ----------
    line_obj : Line
        The COMPAS Line object to serialize.

    Returns
    -------
    geometry_pb2.LineData
        The protobuf message representing the Line.
    """
    proto_data = geometry_pb2.LineData()
    if line_obj._guid is not None:
        proto_data.guid = str(line_obj._guid)
    if line_obj._name is not None:
        proto_data.name = line_obj.name

    start = point_to_pb(line_obj.start)
    end = point_to_pb(line_obj.end)

    proto_data.start.CopyFrom(start)
    proto_data.end.CopyFrom(end)

    return proto_data


@pb_deserializer(geometry_pb2.LineData)
def line_from_pb(proto_data: geometry_pb2.LineData) -> Line:
    """
    Convert a protobuf message to COMPAS Line.

    Parameters
    ----------
    proto_data : geometry_pb2.LineData
        The protobuf message representing a Line.

    Returns
    -------
    Line
        The deserialized COMPAS Line object.
    """
    start = point_from_pb(proto_data.start)
    end = point_from_pb(proto_data.end)

    result = Line(start=start, end=end, name=(proto_data.name or None))
    if proto_data.guid:
        result._guid = UUID(proto_data.guid)
    return result


# =============================================================================
# Vector
# =============================================================================


@pb_serializer(Vector)
def vector_to_pb(obj: Vector) -> geometry_pb2.VectorData:
    """
    Convert a COMPAS Vector to protobuf message.

    Parameters
    ----------
    obj : Vector
        The COMPAS Vector object to serialize.

    Returns
    -------
    geometry_pb2.VectorData
        The protobuf message representing the Vector.
    """
    proto_data = geometry_pb2.VectorData()
    if obj._name is not None:
        proto_data.name = obj.name
    if obj._guid is not None:
        proto_data.guid = str(obj._guid)
    proto_data.x = obj.x
    proto_data.y = obj.y
    proto_data.z = obj.z
    return proto_data


@pb_deserializer(geometry_pb2.VectorData)
def vector_from_pb(proto_data: geometry_pb2.VectorData) -> Vector:
    """
    Convert a protobuf message to COMPAS Vector.

    Parameters
    ----------
    proto_data : geometry_pb2.VectorData
        The protobuf message representing a Vector.

    Returns
    -------
    Vector
        The deserialized COMPAS Vector object.
    """
    result = Vector(x=proto_data.x, y=proto_data.y, z=proto_data.z, name=(proto_data.name or None))
    if proto_data.guid:
        result._guid = UUID(proto_data.guid)
    return result


# =============================================================================
# Frame
# =============================================================================


@pb_serializer(Frame)
def frame_to_pb(frame_obj: Frame) -> geometry_pb2.FrameData:
    """
    Convert a COMPAS Frame to protobuf message.

    Parameters
    ----------
    frame_obj : Frame
        The COMPAS Frame object to serialize.

    Returns
    -------
    geometry_pb2.FrameData
        The protobuf message representing the Frame.
    """
    proto_data = geometry_pb2.FrameData()
    if frame_obj._guid is not None:
        proto_data.guid = str(frame_obj._guid)
    if frame_obj._name is not None:
        proto_data.name = frame_obj.name

    origin = point_to_pb(frame_obj.point)
    xaxis = vector_to_pb(frame_obj.xaxis)
    yaxis = vector_to_pb(frame_obj.yaxis)

    proto_data.point.CopyFrom(origin)
    proto_data.xaxis.CopyFrom(xaxis)
    proto_data.yaxis.CopyFrom(yaxis)

    return proto_data


@pb_deserializer(geometry_pb2.FrameData)
def frame_from_pb(proto_data: geometry_pb2.FrameData) -> Frame:
    """
    Convert a protobuf message to COMPAS Frame.

    Parameters
    ----------
    proto_data : geometry_pb2.FrameData
        The protobuf message representing a Frame.

    Returns
    -------
    Frame
        The deserialized COMPAS Frame object.
    """
    origin = point_from_pb(proto_data.point)
    xaxis = vector_from_pb(proto_data.xaxis)
    yaxis = vector_from_pb(proto_data.yaxis)
    result = Frame(point=origin, xaxis=xaxis, yaxis=yaxis, name=(proto_data.name or None))
    if proto_data.guid:
        result._guid = UUID(proto_data.guid)
    return result


# =============================================================================
# Mesh
# =============================================================================


@pb_serializer(Mesh)
def mesh_to_pb(mesh: Mesh) -> datastructures_pb2.MeshData:
    """Convert a COMPAS Mesh to protobuf message.

    Parameters
    ----------
    mesh
        The COMPAS Mesh object to serialize.

    Returns
    -------
    datastructures_pb2.MeshData
        The protobuf message representing the Mesh.
    """
    proto_data = datastructures_pb2.MeshData()
    if mesh._guid is not None:
        proto_data.guid = str(mesh._guid)
    if mesh._name is not None:
        proto_data.name = mesh.name or "Mesh"

    # Vertices as a flat coordinate array (3 doubles per vertex) instead of a message per vertex.
    index_map = {}  # vertex_key → index
    for index, key in enumerate(mesh.vertices()):
        x, y, z = mesh.vertex_coordinates(key)
        proto_data.vertices.extend((x, y, z))
        index_map[key] = index

    # Faces in CSR form: concatenated indices + per-face vertex counts.
    for fkey in mesh.faces():
        indices = [index_map[vkey] for vkey in mesh.face_vertices(fkey)]
        proto_data.face_vertices.extend(indices)
        proto_data.face_sizes.append(len(indices))

    # Attributes as inline maps; only non-empty entries are written (empty/default maps -> 0 bytes).
    _fill_attr_map(proto_data.attributes, mesh.attributes)
    _fill_attr_map(proto_data.default_edge_attributes, mesh.default_edge_attributes)
    _fill_attr_map(proto_data.default_face_attributes, mesh.default_face_attributes)
    _fill_attr_map(proto_data.default_vertex_attributes, mesh.default_vertex_attributes)
    _fill_attr_map(proto_data.edge_attributes, mesh.edgedata)
    _fill_attr_map(proto_data.face_attributes, {str(k): v for k, v in mesh.facedata.items() if v})

    _fill_attribute_columns(proto_data.vertex_attribute_columns, mesh.vertex, index_map, len(index_map))

    return proto_data


@pb_deserializer(datastructures_pb2.MeshData)
def mesh_from_pb(proto_data: datastructures_pb2.MeshData) -> Mesh:
    """
    Convert a protobuf message to COMPAS Mesh.

    Parameters
    ----------
    proto_data : datastructures_pb2.MeshData
        The protobuf message representing a Mesh.

    Returns
    -------
    Mesh
        The deserialized COMPAS Mesh object.
    """
    mesh = Mesh(name=(proto_data.name or None))
    vertex_map = []

    # Flat coordinate array: consume 3 doubles (x, y, z) per vertex.
    coords = proto_data.vertices
    for i in range(0, len(coords), 3):
        key = mesh.add_vertex(x=coords[i], y=coords[i + 1], z=coords[i + 2])
        vertex_map.append(key)

    offset = 0
    for size in proto_data.face_sizes:
        indices = [vertex_map[i] for i in proto_data.face_vertices[offset:offset + size]]
        mesh.add_face(indices)
        offset += size

    if proto_data.guid:
        mesh._guid = UUID(proto_data.guid)
    mesh.default_edge_attributes.update(_read_attr_map(proto_data.default_edge_attributes))
    mesh.default_face_attributes.update(_read_attr_map(proto_data.default_face_attributes))
    mesh.default_vertex_attributes.update(_read_attr_map(proto_data.default_vertex_attributes))
    mesh.attributes.update(_read_attr_map(proto_data.attributes))
    mesh.edgedata.update(_read_attr_map(proto_data.edge_attributes))
    mesh.facedata.update({int(k): v for k, v in _read_attr_map(proto_data.face_attributes).items()})
    _read_attribute_columns(proto_data.vertex_attribute_columns, vertex_map, mesh.vertex)

    return mesh


# =============================================================================
# Circle
# =============================================================================


@pb_serializer(Circle)
def circle_to_pb(circle: Circle) -> geometry_pb2.CircleData:
    """
    Convert a COMPAS Circle to protobuf message.

    Parameters
    ----------
    circle : Circle
        The COMPAS Circle object to serialize.

    Returns
    -------
    geometry_pb2.CircleData
        The protobuf message representing the Circle.
    """
    result = geometry_pb2.CircleData()
    result.guid = str(circle.guid)
    result.name = circle.name or "Circle"
    result.radius = circle.radius
    result.frame.CopyFrom(frame_to_pb(circle.frame))
    return result


@pb_deserializer(geometry_pb2.CircleData)
def circle_from_pb(proto_data: geometry_pb2.CircleData) -> Circle:
    """
    Convert a protobuf message to COMPAS Circle.

    Parameters
    ----------
    proto_data : geometry_pb2.CircleData
        The protobuf message representing a Circle.

    Returns
    -------
    Circle
        The deserialized COMPAS Circle object.
    """
    frame = frame_from_pb(proto_data.frame)
    result = Circle(radius=proto_data.radius, frame=frame, name=(proto_data.name or None))
    if proto_data.guid:
        result._guid = UUID(proto_data.guid)
    return result


# =============================================================================
# Plane
# =============================================================================


@pb_serializer(Plane)
def plane_to_pb(plane: Plane) -> geometry_pb2.PlaneData:
    """
    Convert a COMPAS Plane to protobuf message.

    Parameters
    ----------
    plane : Plane
        The COMPAS Plane object to serialize.

    Returns
    -------
    geometry_pb2.PlaneData
        The protobuf message representing the Plane.
    """
    proto_data = geometry_pb2.PlaneData()
    if plane._guid is not None:
        proto_data.guid = str(plane._guid)
    if plane._name is not None:
        proto_data.name = plane.name

    point = point_to_pb(plane.point)
    normal = vector_to_pb(plane.normal)

    proto_data.point.CopyFrom(point)
    proto_data.normal.CopyFrom(normal)

    return proto_data


@pb_deserializer(geometry_pb2.PlaneData)
def plane_from_pb(proto_data: geometry_pb2.PlaneData) -> Plane:
    """
    Convert a protobuf message to COMPAS Plane.

    Parameters
    ----------
    proto_data : geometry_pb2.PlaneData
        The protobuf message representing a Plane.

    Returns
    -------
    Plane
        The deserialized COMPAS Plane object.
    """
    point = point_from_pb(proto_data.point)
    normal = vector_from_pb(proto_data.normal)
    result = Plane(point=point, normal=normal, name=(proto_data.name or None))
    if proto_data.guid:
        result._guid = UUID(proto_data.guid)
    return result


# =============================================================================
# Polygon
# =============================================================================


@pb_serializer(Polygon)
def polygon_to_pb(polygon: Polygon) -> geometry_pb2.PolygonData:
    """
    Convert a COMPAS Polygon to protobuf message.

    Parameters
    ----------
    polygon : Polygon
        The COMPAS Polygon object to serialize.

    Returns
    -------
    geometry_pb2.PolygonData
        The protobuf message representing the Polygon.
    """
    proto_data = geometry_pb2.PolygonData()
    if polygon._guid is not None:
        proto_data.guid = str(polygon._guid)
    if polygon._name is not None:
        proto_data.name = polygon.name

    _extend_flat_points(proto_data.points, polygon.points)

    return proto_data


@pb_deserializer(geometry_pb2.PolygonData)
def polygon_from_pb(proto_data: geometry_pb2.PolygonData) -> Polygon:
    """
    Convert a protobuf message to COMPAS Polygon.

    Parameters
    ----------
    proto_data : geometry_pb2.PolygonData
        The protobuf message representing a Polygon.

    Returns
    -------
    Polygon
        The deserialized COMPAS Polygon object.
    """
    points = _flat_points_to_lists(proto_data.points)
    result = Polygon(points=points, name=(proto_data.name or None))
    if proto_data.guid:
        result._guid = UUID(proto_data.guid)
    return result


# =============================================================================
# Box
# =============================================================================


@pb_serializer(Box)
def box_to_pb(box: Box) -> geometry_pb2.BoxData:
    """
    Convert a COMPAS Box to protobuf message.

    Parameters
    ----------
    box : Box
        The COMPAS Box object to serialize.

    Returns
    -------
    geometry_pb2.BoxData
        The protobuf message representing the Box.
    """
    proto_data = geometry_pb2.BoxData()
    if box._guid is not None:
        proto_data.guid = str(box._guid)
    if box._name is not None:
        proto_data.name = box.name
    proto_data.xsize = box.xsize
    proto_data.ysize = box.ysize
    proto_data.zsize = box.zsize

    frame = frame_to_pb(box.frame)
    proto_data.frame.CopyFrom(frame)

    return proto_data


@pb_deserializer(geometry_pb2.BoxData)
def box_from_pb(proto_data: geometry_pb2.BoxData) -> Box:
    """
    Convert a protobuf message to COMPAS Box.

    Parameters
    ----------
    proto_data : geometry_pb2.BoxData
        The protobuf message representing a Box.

    Returns
    -------
    Box
        The deserialized COMPAS Box object.
    """
    frame = frame_from_pb(proto_data.frame)
    result = Box(frame=frame, xsize=proto_data.xsize, ysize=proto_data.ysize, zsize=proto_data.zsize, name=(proto_data.name or None))
    if proto_data.guid:
        result._guid = UUID(proto_data.guid)
    return result


# =============================================================================
# Arc
# =============================================================================


@pb_serializer(Arc)
def arc_to_pb(arc: Arc) -> geometry_pb2.ArcData:
    """
    Convert a COMPAS Arc to protobuf message.

    Parameters
    ----------
    arc : Arc
        The COMPAS Arc object to serialize.

    Returns
    -------
    geometry_pb2.ArcData
        The protobuf message representing the Arc.
    """
    proto_data = geometry_pb2.ArcData()
    if arc._guid is not None:
        proto_data.guid = str(arc._guid)
    if arc._name is not None:
        proto_data.name = arc.name
    proto_data.start_angle = arc.start_angle
    proto_data.end_angle = arc.end_angle

    circle = circle_to_pb(arc.circle)
    proto_data.circle.CopyFrom(circle)

    return proto_data


@pb_deserializer(geometry_pb2.ArcData)
def arc_from_pb(proto_data: geometry_pb2.ArcData) -> Arc:
    """
    Convert a protobuf message to COMPAS Arc.

    Parameters
    ----------
    proto_data : geometry_pb2.ArcData
        The protobuf message representing an Arc.

    Returns
    -------
    Arc
        The deserialized COMPAS Arc object.
    """
    circle = circle_from_pb(proto_data.circle)
    result = Arc.from_circle(circle, proto_data.start_angle, proto_data.end_angle)
    result.name = proto_data.name
    if proto_data.guid:
        result._guid = UUID(proto_data.guid)
    return result


# =============================================================================
# Sphere
# =============================================================================


@pb_serializer(Sphere)
def sphere_to_pb(sphere: Sphere) -> geometry_pb2.SphereData:
    """
    Convert a COMPAS Sphere to protobuf message.

    Parameters
    ----------
    sphere : Sphere
        The COMPAS Sphere object to serialize.

    Returns
    -------
    geometry_pb2.SphereData
        The protobuf message representing the Sphere.
    """
    proto_data = geometry_pb2.SphereData()
    if sphere._guid is not None:
        proto_data.guid = str(sphere._guid)
    if sphere._name is not None:
        proto_data.name = sphere.name
    proto_data.radius = sphere.radius

    frame = frame_to_pb(sphere.frame)
    proto_data.frame.CopyFrom(frame)

    return proto_data


@pb_deserializer(geometry_pb2.SphereData)
def sphere_from_pb(proto_data: geometry_pb2.SphereData) -> Sphere:
    """
    Convert a protobuf message to COMPAS Sphere.

    Parameters
    ----------
    proto_data : geometry_pb2.SphereData
        The protobuf message representing a Sphere.

    Returns
    -------
    Sphere
        The deserialized COMPAS Sphere object.
    """
    frame = frame_from_pb(proto_data.frame)
    result = Sphere(radius=proto_data.radius, frame=frame, name=(proto_data.name or None))
    if proto_data.guid:
        result._guid = UUID(proto_data.guid)
    return result


# =============================================================================
# Cylinder
# =============================================================================


@pb_serializer(Cylinder)
def cylinder_to_pb(cylinder: Cylinder) -> geometry_pb2.CylinderData:
    """
    Convert a COMPAS Cylinder to protobuf message.

    Parameters
    ----------
    cylinder : Cylinder
        The COMPAS Cylinder object to serialize.

    Returns
    -------
    geometry_pb2.CylinderData
        The protobuf message representing the Cylinder.
    """
    proto_data = geometry_pb2.CylinderData()
    if cylinder._guid is not None:
        proto_data.guid = str(cylinder._guid)
    if cylinder._name is not None:
        proto_data.name = cylinder.name
    proto_data.radius = cylinder.radius
    proto_data.height = cylinder.height

    frame = frame_to_pb(cylinder.frame)
    proto_data.frame.CopyFrom(frame)

    return proto_data


@pb_deserializer(geometry_pb2.CylinderData)
def cylinder_from_pb(proto_data: geometry_pb2.CylinderData) -> Cylinder:
    """
    Convert a protobuf message to COMPAS Cylinder.

    Parameters
    ----------
    proto_data : geometry_pb2.CylinderData
        The protobuf message representing a Cylinder.

    Returns
    -------
    Cylinder
        The deserialized COMPAS Cylinder object.
    """
    frame = frame_from_pb(proto_data.frame)
    result = Cylinder(radius=proto_data.radius, height=proto_data.height, frame=frame, name=(proto_data.name or None))
    if proto_data.guid:
        result._guid = UUID(proto_data.guid)
    return result


# =============================================================================
# Cone
# =============================================================================


@pb_serializer(Cone)
def cone_to_pb(cone: Cone) -> geometry_pb2.ConeData:
    """
    Convert a COMPAS Cone to protobuf message.

    Parameters
    ----------
    cone : Cone
        The COMPAS Cone object to serialize.

    Returns
    -------
    geometry_pb2.ConeData
        The protobuf message representing the Cone.
    """
    proto_data = geometry_pb2.ConeData()
    if cone._guid is not None:
        proto_data.guid = str(cone._guid)
    if cone._name is not None:
        proto_data.name = cone.name
    proto_data.radius = cone.radius
    proto_data.height = cone.height

    frame = frame_to_pb(cone.frame)
    proto_data.frame.CopyFrom(frame)

    return proto_data


@pb_deserializer(geometry_pb2.ConeData)
def cone_from_pb(proto_data: geometry_pb2.ConeData) -> Cone:
    """
    Convert a protobuf message to COMPAS Cone.

    Parameters
    ----------
    proto_data : geometry_pb2.ConeData
        The protobuf message representing a Cone.

    Returns
    -------
    Cone
        The deserialized COMPAS Cone object.
    """
    frame = frame_from_pb(proto_data.frame)
    result = Cone(radius=proto_data.radius, height=proto_data.height, frame=frame, name=(proto_data.name or None))
    if proto_data.guid:
        result._guid = UUID(proto_data.guid)
    return result


# =============================================================================
# Torus
# =============================================================================


@pb_serializer(Torus)
def torus_to_pb(torus: Torus) -> geometry_pb2.TorusData:
    """
    Convert a COMPAS Torus to protobuf message.

    Parameters
    ----------
    torus : Torus
        The COMPAS Torus object to serialize.

    Returns
    -------
    geometry_pb2.TorusData
        The protobuf message representing the Torus.
    """
    proto_data = geometry_pb2.TorusData()
    if torus._guid is not None:
        proto_data.guid = str(torus._guid)
    if torus._name is not None:
        proto_data.name = torus.name
    proto_data.radius_axis = torus.radius_axis
    proto_data.radius_pipe = torus.radius_pipe

    frame = frame_to_pb(torus.frame)
    proto_data.frame.CopyFrom(frame)

    return proto_data


@pb_deserializer(geometry_pb2.TorusData)
def torus_from_pb(proto_data: geometry_pb2.TorusData) -> Torus:
    """
    Convert a protobuf message to COMPAS Torus.

    Parameters
    ----------
    proto_data : geometry_pb2.TorusData
        The protobuf message representing a Torus.

    Returns
    -------
    Torus
        The deserialized COMPAS Torus object.
    """
    frame = frame_from_pb(proto_data.frame)
    result = Torus(radius_axis=proto_data.radius_axis, radius_pipe=proto_data.radius_pipe, frame=frame, name=(proto_data.name or None))
    if proto_data.guid:
        result._guid = UUID(proto_data.guid)
    return result


# =============================================================================
# Ellipse
# =============================================================================


@pb_serializer(Ellipse)
def ellipse_to_pb(ellipse: Ellipse) -> geometry_pb2.EllipseData:
    """
    Convert a COMPAS Ellipse to protobuf message.

    Parameters
    ----------
    ellipse : Ellipse
        The COMPAS Ellipse object to serialize.

    Returns
    -------
    geometry_pb2.EllipseData
        The protobuf message representing the Ellipse.
    """
    proto_data = geometry_pb2.EllipseData()
    if ellipse._guid is not None:
        proto_data.guid = str(ellipse._guid)
    if ellipse._name is not None:
        proto_data.name = ellipse.name
    proto_data.major = ellipse.major
    proto_data.minor = ellipse.minor

    frame = frame_to_pb(ellipse.frame)
    proto_data.frame.CopyFrom(frame)

    return proto_data


@pb_deserializer(geometry_pb2.EllipseData)
def ellipse_from_pb(proto_data: geometry_pb2.EllipseData) -> Ellipse:
    """
    Convert a protobuf message to COMPAS Ellipse.

    Parameters
    ----------
    proto_data : geometry_pb2.EllipseData
        The protobuf message representing an Ellipse.

    Returns
    -------
    Ellipse
        The deserialized COMPAS Ellipse object.
    """
    frame = frame_from_pb(proto_data.frame)
    result = Ellipse(major=proto_data.major, minor=proto_data.minor, frame=frame, name=(proto_data.name or None))
    if proto_data.guid:
        result._guid = UUID(proto_data.guid)
    return result


# =============================================================================
# Polyline
# =============================================================================


@pb_serializer(Polyline)
def polyline_to_pb(polyline: Polyline) -> geometry_pb2.PolylineData:
    """
    Convert a COMPAS Polyline to protobuf message.

    Parameters
    ----------
    polyline : Polyline
        The COMPAS Polyline object to serialize.

    Returns
    -------
    geometry_pb2.PolylineData
        The protobuf message representing the Polyline.
    """
    proto_data = geometry_pb2.PolylineData()
    if polyline._guid is not None:
        proto_data.guid = str(polyline._guid)
    if polyline._name is not None:
        proto_data.name = polyline.name

    _extend_flat_points(proto_data.points, polyline.points)

    return proto_data


@pb_deserializer(geometry_pb2.PolylineData)
def polyline_from_pb(proto_data: geometry_pb2.PolylineData) -> Polyline:
    """
    Convert a protobuf message to COMPAS Polyline.

    Parameters
    ----------
    proto_data : geometry_pb2.PolylineData
        The protobuf message representing a Polyline.

    Returns
    -------
    Polyline
        The deserialized COMPAS Polyline object.
    """
    points = _flat_points_to_lists(proto_data.points)
    result = Polyline(points=points, name=(proto_data.name or None))
    if proto_data.guid:
        result._guid = UUID(proto_data.guid)
    return result


# =============================================================================
# Pointcloud
# =============================================================================


@pb_serializer(Pointcloud)
def pointcloud_to_pb(pointcloud: Pointcloud) -> geometry_pb2.PointcloudData:
    """
    Convert a COMPAS Pointcloud to protobuf message.

    Parameters
    ----------
    pointcloud : Pointcloud
        The COMPAS Pointcloud object to serialize.

    Returns
    -------
    geometry_pb2.PointcloudData
        The protobuf message representing the Pointcloud.
    """
    proto_data = geometry_pb2.PointcloudData()
    if pointcloud._guid is not None:
        proto_data.guid = str(pointcloud._guid)
    if pointcloud._name is not None:
        proto_data.name = pointcloud.name

    _extend_flat_points(proto_data.points, pointcloud.points)

    return proto_data


@pb_deserializer(geometry_pb2.PointcloudData)
def pointcloud_from_pb(proto_data: geometry_pb2.PointcloudData) -> Pointcloud:
    """
    Convert a protobuf message to COMPAS Pointcloud.

    Parameters
    ----------
    proto_data : geometry_pb2.PointcloudData
        The protobuf message representing a Pointcloud.

    Returns
    -------
    Pointcloud
        The deserialized COMPAS Pointcloud object.
    """
    points = _flat_points_to_lists(proto_data.points)
    result = Pointcloud(points=points, name=(proto_data.name or None))
    if proto_data.guid:
        result._guid = UUID(proto_data.guid)
    return result


# =============================================================================
# Transformation
# =============================================================================


@pb_serializer(Transformation)
def transformation_to_pb(transformation: Transformation) -> geometry_pb2.TransformationData:
    """
    Convert a COMPAS Transformation to protobuf message.

    Parameters
    ----------
    transformation : Transformation
        The COMPAS Transformation object to serialize.

    Returns
    -------
    geometry_pb2.TransformationData
        The protobuf message representing the Transformation.
    """
    proto_data = geometry_pb2.TransformationData()
    if transformation._guid is not None:
        proto_data.guid = str(transformation._guid)
    if transformation._name is not None:
        proto_data.name = transformation.name

    # Flatten 4x4 matrix to list of 16 floats
    matrix = transformation.matrix
    for row in matrix:
        for value in row:
            proto_data.matrix.append(value)

    return proto_data


@pb_deserializer(geometry_pb2.TransformationData)
def transformation_from_pb(proto_data: geometry_pb2.TransformationData) -> Transformation:
    """
    Convert a protobuf message to COMPAS Transformation.

    Parameters
    ----------
    proto_data : geometry_pb2.TransformationData
        The protobuf message representing a Transformation.

    Returns
    -------
    Transformation
        The deserialized COMPAS Transformation object.
    """
    # Convert flat list of 16 floats back to 4x4 matrix
    matrix_flat = list(proto_data.matrix)
    matrix = []
    for i in range(4):
        row = []
        for j in range(4):
            row.append(matrix_flat[i * 4 + j])
        matrix.append(row)

    result = Transformation.from_matrix(matrix)
    result.name = proto_data.name
    if proto_data.guid:
        result._guid = UUID(proto_data.guid)
    return result


# =============================================================================
# Translation
# =============================================================================


@pb_serializer(Translation)
def translation_to_pb(translation: Translation) -> geometry_pb2.TranslationData:
    """
    Convert a COMPAS Translation to protobuf message.

    Parameters
    ----------
    translation : Translation
        The COMPAS Translation object to serialize.

    Returns
    -------
    geometry_pb2.TranslationData
        The protobuf message representing the Translation.
    """
    proto_data = geometry_pb2.TranslationData()
    if translation._guid is not None:
        proto_data.guid = str(translation._guid)
    if translation._name is not None:
        proto_data.name = translation.name

    vector = vector_to_pb(translation.translation_vector)
    proto_data.translation_vector.CopyFrom(vector)

    return proto_data


@pb_deserializer(geometry_pb2.TranslationData)
def translation_from_pb(proto_data: geometry_pb2.TranslationData) -> Translation:
    """
    Convert a protobuf message to COMPAS Translation.

    Parameters
    ----------
    proto_data : geometry_pb2.TranslationData
        The protobuf message representing a Translation.

    Returns
    -------
    Translation
        The deserialized COMPAS Translation object.
    """
    vector = vector_from_pb(proto_data.translation_vector)
    result = Translation.from_vector(vector)
    result.name = proto_data.name
    if proto_data.guid:
        result._guid = UUID(proto_data.guid)
    return result


# =============================================================================
# Rotation
# =============================================================================


@pb_serializer(Rotation)
def rotation_to_pb(rotation: Rotation) -> geometry_pb2.RotationData:
    """
    Convert a COMPAS Rotation to protobuf message.

    Parameters
    ----------
    rotation : Rotation
        The COMPAS Rotation object to serialize.

    Returns
    -------
    geometry_pb2.RotationData
        The protobuf message representing the Rotation.
    """
    proto_data = geometry_pb2.RotationData()
    if rotation._guid is not None:
        proto_data.guid = str(rotation._guid)
    if rotation._name is not None:
        proto_data.name = rotation.name

    # Get axis and angle from the rotation
    axis_angle = rotation.axis_and_angle
    axis = axis_angle[0]
    angle = axis_angle[1]

    proto_axis = vector_to_pb(axis)
    proto_data.axis.CopyFrom(proto_axis)
    proto_data.angle = angle

    # Use origin as the default point of rotation
    from compas.geometry import Point

    point = Point(0, 0, 0)
    proto_point = point_to_pb(point)
    proto_data.point.CopyFrom(proto_point)

    return proto_data


@pb_deserializer(geometry_pb2.RotationData)
def rotation_from_pb(proto_data: geometry_pb2.RotationData) -> Rotation:
    """
    Convert a protobuf message to COMPAS Rotation.

    Parameters
    ----------
    proto_data : geometry_pb2.RotationData
        The protobuf message representing a Rotation.

    Returns
    -------
    Rotation
        The deserialized COMPAS Rotation object.
    """
    axis = vector_from_pb(proto_data.axis)
    angle = proto_data.angle

    result = Rotation.from_axis_and_angle(axis, angle)
    result.name = proto_data.name
    if proto_data.guid:
        result._guid = UUID(proto_data.guid)
    return result


# =============================================================================
# Capsule
# =============================================================================


@pb_serializer(Capsule)
def capsule_to_pb(capsule: Capsule) -> geometry_pb2.CapsuleData:
    """
    Convert a COMPAS Capsule to protobuf message.

    Parameters
    ----------
    capsule : Capsule
        The COMPAS Capsule object to serialize.

    Returns
    -------
    geometry_pb2.CapsuleData
        The protobuf message representing the Capsule.
    """
    proto_data = geometry_pb2.CapsuleData()
    if capsule._guid is not None:
        proto_data.guid = str(capsule._guid)
    if capsule._name is not None:
        proto_data.name = capsule.name
    proto_data.radius = capsule.radius
    proto_data.height = capsule.height

    frame = frame_to_pb(capsule.frame)
    proto_data.frame.CopyFrom(frame)

    return proto_data


@pb_deserializer(geometry_pb2.CapsuleData)
def capsule_from_pb(proto_data: geometry_pb2.CapsuleData) -> Capsule:
    """
    Convert a protobuf message to COMPAS Capsule.

    Parameters
    ----------
    proto_data : geometry_pb2.CapsuleData
        The protobuf message representing a Capsule.

    Returns
    -------
    Capsule
        The deserialized COMPAS Capsule object.
    """
    frame = frame_from_pb(proto_data.frame)
    result = Capsule(radius=proto_data.radius, height=proto_data.height, frame=frame, name=(proto_data.name or None))
    if proto_data.guid:
        result._guid = UUID(proto_data.guid)
    return result


# =============================================================================
# Quaternion
# =============================================================================


@pb_serializer(Quaternion)
def quaternion_to_pb(quaternion: Quaternion) -> geometry_pb2.QuaternionData:
    """
    Convert a COMPAS Quaternion to protobuf message.

    Parameters
    ----------
    quaternion : Quaternion
        The COMPAS Quaternion object to serialize.

    Returns
    -------
    geometry_pb2.QuaternionData
        The protobuf message representing the Quaternion.
    """
    proto_data = geometry_pb2.QuaternionData()
    if quaternion._guid is not None:
        proto_data.guid = str(quaternion._guid)
    if quaternion._name is not None:
        proto_data.name = quaternion.name
    proto_data.w = quaternion.w
    proto_data.x = quaternion.x
    proto_data.y = quaternion.y
    proto_data.z = quaternion.z

    return proto_data


@pb_deserializer(geometry_pb2.QuaternionData)
def quaternion_from_pb(proto_data: geometry_pb2.QuaternionData) -> Quaternion:
    """
    Convert a protobuf message to COMPAS Quaternion.

    Parameters
    ----------
    proto_data : geometry_pb2.QuaternionData
        The protobuf message representing a Quaternion.

    Returns
    -------
    Quaternion
        The deserialized COMPAS Quaternion object.
    """
    result = Quaternion(w=proto_data.w, x=proto_data.x, y=proto_data.y, z=proto_data.z, name=(proto_data.name or None))
    if proto_data.guid:
        result._guid = UUID(proto_data.guid)
    return result


# =============================================================================
# Scale
# =============================================================================


@pb_serializer(Scale)
def scale_to_pb(scale: Scale) -> geometry_pb2.ScaleData:
    """
    Convert a COMPAS Scale to protobuf message.

    Parameters
    ----------
    scale : Scale
        The COMPAS Scale object to serialize.

    Returns
    -------
    geometry_pb2.ScaleData
        The protobuf message representing the Scale.
    """
    proto_data = geometry_pb2.ScaleData()
    if scale._guid is not None:
        proto_data.guid = str(scale._guid)
    if scale._name is not None:
        proto_data.name = scale.name

    # Flatten 4x4 matrix to list of 16 floats
    matrix = scale.matrix
    for row in matrix:
        for value in row:
            proto_data.matrix.append(value)

    return proto_data


@pb_deserializer(geometry_pb2.ScaleData)
def scale_from_pb(proto_data: geometry_pb2.ScaleData) -> Scale:
    """
    Convert a protobuf message to COMPAS Scale.

    Parameters
    ----------
    proto_data : geometry_pb2.ScaleData
        The protobuf message representing a Scale.

    Returns
    -------
    Scale
        The deserialized COMPAS Scale object.
    """
    # Convert flat list of 16 floats back to 4x4 matrix
    matrix_flat = list(proto_data.matrix)
    matrix = []
    for i in range(4):
        row = []
        for j in range(4):
            row.append(matrix_flat[i * 4 + j])
        matrix.append(row)

    result = Scale.from_matrix(matrix)
    result.name = proto_data.name
    if proto_data.guid:
        result._guid = UUID(proto_data.guid)
    return result


# =============================================================================
# Reflection
# =============================================================================


@pb_serializer(Reflection)
def reflection_to_pb(reflection: Reflection) -> geometry_pb2.ReflectionData:
    """
    Convert a COMPAS Reflection to protobuf message.

    Parameters
    ----------
    reflection : Reflection
        The COMPAS Reflection object to serialize.

    Returns
    -------
    geometry_pb2.ReflectionData
        The protobuf message representing the Reflection.
    """
    proto_data = geometry_pb2.ReflectionData()
    if reflection._guid is not None:
        proto_data.guid = str(reflection._guid)
    if reflection._name is not None:
        proto_data.name = reflection.name

    # Flatten 4x4 matrix to list of 16 floats
    matrix = reflection.matrix
    for row in matrix:
        for value in row:
            proto_data.matrix.append(value)

    return proto_data


@pb_deserializer(geometry_pb2.ReflectionData)
def reflection_from_pb(proto_data: geometry_pb2.ReflectionData) -> Reflection:
    """
    Convert a protobuf message to COMPAS Reflection.

    Parameters
    ----------
    proto_data : geometry_pb2.ReflectionData
        The protobuf message representing a Reflection.

    Returns
    -------
    Reflection
        The deserialized COMPAS Reflection object.
    """
    # Convert flat list of 16 floats back to 4x4 matrix
    matrix_flat = list(proto_data.matrix)
    matrix = []
    for i in range(4):
        row = []
        for j in range(4):
            row.append(matrix_flat[i * 4 + j])
        matrix.append(row)

    result = Reflection.from_matrix(matrix)
    result.name = proto_data.name
    if proto_data.guid:
        result._guid = UUID(proto_data.guid)
    return result


# =============================================================================
# Shear
# =============================================================================


@pb_serializer(Shear)
def shear_to_pb(shear: Shear) -> geometry_pb2.ShearData:
    """
    Convert a COMPAS Shear to protobuf message.

    Parameters
    ----------
    shear : Shear
        The COMPAS Shear object to serialize.

    Returns
    -------
    geometry_pb2.ShearData
        The protobuf message representing the Shear.
    """
    proto_data = geometry_pb2.ShearData()
    if shear._guid is not None:
        proto_data.guid = str(shear._guid)
    if shear._name is not None:
        proto_data.name = shear.name

    # Flatten 4x4 matrix to list of 16 floats
    matrix = shear.matrix
    for row in matrix:
        for value in row:
            proto_data.matrix.append(value)

    return proto_data


@pb_deserializer(geometry_pb2.ShearData)
def shear_from_pb(proto_data: geometry_pb2.ShearData) -> Shear:
    """
    Convert a protobuf message to COMPAS Shear.

    Parameters
    ----------
    proto_data : geometry_pb2.ShearData
        The protobuf message representing a Shear.

    Returns
    -------
    Shear
        The deserialized COMPAS Shear object.
    """
    # Convert flat list of 16 floats back to 4x4 matrix
    matrix_flat = list(proto_data.matrix)
    matrix = []
    for i in range(4):
        row = []
        for j in range(4):
            row.append(matrix_flat[i * 4 + j])
        matrix.append(row)

    result = Shear.from_matrix(matrix)
    result.name = proto_data.name
    if proto_data.guid:
        result._guid = UUID(proto_data.guid)
    return result


# =============================================================================
# Projection
# =============================================================================


@pb_serializer(Projection)
def projection_to_pb(projection: Projection) -> geometry_pb2.ProjectionData:
    """
    Convert a COMPAS Projection to protobuf message.

    Parameters
    ----------
    projection : Projection
        The COMPAS Projection object to serialize.

    Returns
    -------
    geometry_pb2.ProjectionData
        The protobuf message representing the Projection.
    """
    proto_data = geometry_pb2.ProjectionData()
    if projection._guid is not None:
        proto_data.guid = str(projection._guid)
    if projection._name is not None:
        proto_data.name = projection.name

    # Flatten 4x4 matrix to list of 16 floats
    matrix = projection.matrix
    for row in matrix:
        for value in row:
            proto_data.matrix.append(value)

    return proto_data


@pb_deserializer(geometry_pb2.ProjectionData)
def projection_from_pb(proto_data: geometry_pb2.ProjectionData) -> Projection:
    """
    Convert a protobuf message to COMPAS Projection.

    Parameters
    ----------
    proto_data : geometry_pb2.ProjectionData
        The protobuf message representing a Projection.

    Returns
    -------
    Projection
        The deserialized COMPAS Projection object.
    """
    # Convert flat list of 16 floats back to 4x4 matrix
    matrix_flat = list(proto_data.matrix)
    matrix = []
    for i in range(4):
        row = []
        for j in range(4):
            row.append(matrix_flat[i * 4 + j])
        matrix.append(row)

    result = Projection.from_matrix(matrix)
    result.name = proto_data.name
    if proto_data.guid:
        result._guid = UUID(proto_data.guid)
    return result


# =============================================================================
# Bezier
# =============================================================================


@pb_serializer(Bezier)
def bezier_to_pb(bezier: Bezier) -> geometry_pb2.BezierData:
    """
    Convert a COMPAS Bezier to protobuf message.

    Parameters
    ----------
    bezier : Bezier
        The COMPAS Bezier object to serialize.

    Returns
    -------
    geometry_pb2.BezierData
        The protobuf message representing the Bezier.
    """
    proto_data = geometry_pb2.BezierData()
    if bezier._guid is not None:
        proto_data.guid = str(bezier._guid)
    if bezier._name is not None:
        proto_data.name = bezier.name
    proto_data.degree = bezier.degree

    _extend_flat_points(proto_data.points, bezier.points)

    return proto_data


@pb_deserializer(geometry_pb2.BezierData)
def bezier_from_pb(proto_data: geometry_pb2.BezierData) -> Bezier:
    """
    Convert a protobuf message to COMPAS Bezier.

    Parameters
    ----------
    proto_data : geometry_pb2.BezierData
        The protobuf message representing a Bezier.

    Returns
    -------
    Bezier
        The deserialized COMPAS Bezier object.
    """
    points = _flat_points_to_lists(proto_data.points)
    result = Bezier(points=points, name=(proto_data.name or None))
    if proto_data.guid:
        result._guid = UUID(proto_data.guid)
    return result


# =============================================================================
# Hyperbola
# =============================================================================


@pb_serializer(Hyperbola)
def hyperbola_to_pb(hyperbola: Hyperbola) -> geometry_pb2.HyperbolaData:
    """
    Convert a COMPAS Hyperbola to protobuf message.

    Parameters
    ----------
    hyperbola : Hyperbola
        The COMPAS Hyperbola object to serialize.

    Returns
    -------
    geometry_pb2.HyperbolaData
        The protobuf message representing the Hyperbola.
    """
    proto_data = geometry_pb2.HyperbolaData()
    if hyperbola._guid is not None:
        proto_data.guid = str(hyperbola._guid)
    if hyperbola._name is not None:
        proto_data.name = hyperbola.name
    proto_data.major = hyperbola.major
    proto_data.minor = hyperbola.minor

    frame = frame_to_pb(hyperbola.frame)
    proto_data.frame.CopyFrom(frame)

    return proto_data


@pb_deserializer(geometry_pb2.HyperbolaData)
def hyperbola_from_pb(proto_data: geometry_pb2.HyperbolaData) -> Hyperbola:
    """
    Convert a protobuf message to COMPAS Hyperbola.

    Parameters
    ----------
    proto_data : geometry_pb2.HyperbolaData
        The protobuf message representing a Hyperbola.

    Returns
    -------
    Hyperbola
        The deserialized COMPAS Hyperbola object.
    """
    frame = frame_from_pb(proto_data.frame)
    result = Hyperbola(major=proto_data.major, minor=proto_data.minor, frame=frame, name=(proto_data.name or None))
    if proto_data.guid:
        result._guid = UUID(proto_data.guid)
    return result


# =============================================================================
# Parabola
# =============================================================================


@pb_serializer(Parabola)
def parabola_to_pb(parabola: Parabola) -> geometry_pb2.ParabolaData:
    """
    Convert a COMPAS Parabola to protobuf message.

    Parameters
    ----------
    parabola : Parabola
        The COMPAS Parabola object to serialize.

    Returns
    -------
    geometry_pb2.ParabolaData
        The protobuf message representing the Parabola.
    """
    proto_data = geometry_pb2.ParabolaData()
    if parabola._guid is not None:
        proto_data.guid = str(parabola._guid)
    if parabola._name is not None:
        proto_data.name = parabola.name
    proto_data.focal = parabola.focal

    frame = frame_to_pb(parabola.frame)
    proto_data.frame.CopyFrom(frame)

    return proto_data


@pb_deserializer(geometry_pb2.ParabolaData)
def parabola_from_pb(proto_data: geometry_pb2.ParabolaData) -> Parabola:
    """
    Convert a protobuf message to COMPAS Parabola.

    Parameters
    ----------
    proto_data : geometry_pb2.ParabolaData
        The protobuf message representing a Parabola.

    Returns
    -------
    Parabola
        The deserialized COMPAS Parabola object.
    """
    frame = frame_from_pb(proto_data.frame)
    result = Parabola(focal=proto_data.focal, frame=frame, name=(proto_data.name or None))
    if proto_data.guid:
        result._guid = UUID(proto_data.guid)
    return result


# =============================================================================
# Polyhedron
# =============================================================================


@pb_serializer(Polyhedron)
def polyhedron_to_pb(polyhedron: Polyhedron) -> datastructures_pb2.PolyhedronData:
    """
    Convert a COMPAS Polyhedron to protobuf message.

    Parameters
    ----------
    polyhedron : Polyhedron
        The COMPAS Polyhedron object to serialize.

    Returns
    -------
    datastructures_pb2.PolyhedronData
        The protobuf message representing the Polyhedron.
    """
    proto_data = datastructures_pb2.PolyhedronData()
    if polyhedron._guid is not None:
        proto_data.guid = str(polyhedron._guid)
    if polyhedron._name is not None:
        proto_data.name = polyhedron.name

    # Add vertices as a flat coordinate array (3 doubles per vertex)
    _extend_flat_points(proto_data.vertices, polyhedron.vertices)

    # Add faces
    for face in polyhedron.faces:
        proto_face = datastructures_pb2.FaceData()
        for vertex_index in face:
            proto_face.vertex_indices.append(vertex_index)
        proto_data.faces.append(proto_face)

    return proto_data


@pb_deserializer(datastructures_pb2.PolyhedronData)
def polyhedron_from_pb(proto_data: datastructures_pb2.PolyhedronData) -> Polyhedron:
    """
    Convert a protobuf message to COMPAS Polyhedron.

    Parameters
    ----------
    proto_data : datastructures_pb2.PolyhedronData
        The protobuf message representing a Polyhedron.

    Returns
    -------
    Polyhedron
        The deserialized COMPAS Polyhedron object.
    """
    vertices = _flat_points_to_lists(proto_data.vertices)
    faces = []
    for proto_face in proto_data.faces:
        face = list(proto_face.vertex_indices)
        faces.append(face)

    result = Polyhedron(vertices=vertices, faces=faces, name=(proto_data.name or None))
    if proto_data.guid:
        result._guid = UUID(proto_data.guid)
    return result


# =============================================================================
# Graph
# =============================================================================


@pb_serializer(Graph)
def graph_to_pb(graph: Graph) -> datastructures_pb2.GraphData:
    """
    Convert a COMPAS Graph to protobuf message.

    Parameters
    ----------
    graph : Graph
        The COMPAS Graph object to serialize.

    Returns
    -------
    datastructures_pb2.GraphData
        The protobuf message representing the Graph.
    """
    proto_data = datastructures_pb2.GraphData()
    if graph._guid is not None:
        proto_data.guid = str(graph._guid)
    if graph._name is not None:
        proto_data.name = graph.name or "Graph"

    nodes = {repr(key): attr for key, attr in graph.node.items()}
    edges = {repr(u): {repr(v): attr for v, attr in nbrs.items()} for u, nbrs in graph.edge.items()}

    _fill_attr_map(proto_data.nodes, nodes)
    _fill_attr_map(proto_data.edges, edges)
    _fill_attr_map(proto_data.attributes, graph.attributes)
    _fill_attr_map(proto_data.default_node_attributes, graph.default_node_attributes)
    _fill_attr_map(proto_data.default_edge_attributes, graph.default_edge_attributes)

    return proto_data


@pb_deserializer(datastructures_pb2.GraphData)
def graph_from_pb(proto_data: datastructures_pb2.GraphData) -> Graph:
    """
    Convert a protobuf message to COMPAS Graph.

    Parameters
    ----------
    proto_data : datastructures_pb2.GraphData
        The protobuf message representing a Graph.

    Returns
    -------
    Graph
        The deserialized COMPAS Graph object.
    """
    graph = Graph(
        default_node_attributes=_read_attr_map(proto_data.default_node_attributes),
        default_edge_attributes=_read_attr_map(proto_data.default_edge_attributes),
        name=(proto_data.name or None),
    )
    graph.attributes.update(_read_attr_map(proto_data.attributes))

    for node_key, attr in _read_attr_map(proto_data.nodes).items():
        graph.add_node(key=literal_eval(node_key), attr_dict=attr)
    for u, nbrs in _read_attr_map(proto_data.edges).items():
        for v, attr in nbrs.items():
            graph.add_edge(literal_eval(u), literal_eval(v), attr_dict=attr)

    if proto_data.guid:
        graph._guid = UUID(proto_data.guid)
    return graph
