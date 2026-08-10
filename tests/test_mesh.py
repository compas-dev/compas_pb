import uuid

import pytest

from compas.geometry import Box
from compas.datastructures import Mesh
from compas_pb import pb_dump_bts
from compas_pb import pb_load_bts


@pytest.fixture
def box_mesh():
    box = Box(1.0)
    mesh = Mesh.from_shape(box)
    mesh._guid = uuid.uuid4()
    return mesh


def test_serialize_deserialize_box_mesh(box_mesh):
    data = pb_dump_bts(box_mesh)
    mesh2 = pb_load_bts(data)

    assert isinstance(mesh2, Mesh)
    assert str(mesh2.guid) == str(box_mesh.guid)
    assert mesh2.number_of_vertices() == box_mesh.number_of_vertices()
    assert mesh2.number_of_faces() == box_mesh.number_of_faces()


def test_serialize_deserialize_empty_mesh():
    mesh = Mesh(name="Empty")
    data = pb_dump_bts(mesh)
    mesh2 = pb_load_bts(data)

    assert isinstance(mesh2, Mesh)
    assert mesh2.name == "Empty"
    assert mesh2.number_of_vertices() == 0
    assert mesh2.number_of_faces() == 0


def test_serialize_vertices_relying_on_default_coordinates():
    # add_vertex only stores the keys it was passed, so x/y/z can be absent from the
    # vertex dict and resolved from default_vertex_attributes instead.
    mesh = Mesh()
    a = mesh.add_vertex()
    b = mesh.add_vertex(x=1.0)
    c = mesh.add_vertex(x=1.0, y=1.0)
    d = mesh.add_vertex(y=1.0)
    mesh.add_face([a, b, c, d])

    mesh2 = pb_load_bts(pb_dump_bts(mesh))

    assert [mesh2.vertex_coordinates(v) for v in mesh2.vertices()] == [mesh.vertex_coordinates(v) for v in mesh.vertices()]


def test_serialize_vertices_with_non_zero_default_coordinates():
    mesh = Mesh()
    mesh.update_default_vertex_attributes(z=5.0)
    a = mesh.add_vertex(x=0.0, y=0.0)
    b = mesh.add_vertex(x=1.0, y=0.0)
    c = mesh.add_vertex(x=1.0, y=1.0, z=2.0)
    mesh.add_face([a, b, c])

    mesh2 = pb_load_bts(pb_dump_bts(mesh))

    assert [mesh2.vertex_coordinates(v) for v in mesh2.vertices()] == [[0.0, 0.0, 5.0], [1.0, 0.0, 5.0], [1.0, 1.0, 2.0]]


@pytest.fixture
def quad_mesh_with_defaults():
    # Non-geometry defaults on all three element types, overridden on a subset so both the
    # dense-default and explicit-value paths are exercised.
    mesh = Mesh()
    mesh.update_default_vertex_attributes(weight=1.5, tag="none")
    mesh.update_default_face_attributes(thickness=0.25)
    mesh.update_default_edge_attributes(stiffness=10.0)
    a = mesh.add_vertex(x=0.0, y=0.0, z=0.0)
    b = mesh.add_vertex(x=1.0, y=0.0, z=0.0, weight=9.0)
    c = mesh.add_vertex(x=1.0, y=1.0, z=0.0)
    d = mesh.add_vertex(x=0.0, y=1.0, z=0.0, tag="corner")
    face = mesh.add_face([a, b, c, d])
    mesh.face_attribute(face, "thickness", 0.75)
    mesh.edge_attribute((a, b), "stiffness", 99.0)
    return mesh


def test_roundtrip_preserves_non_geometry_vertex_attributes(quad_mesh_with_defaults):
    mesh2 = pb_load_bts(pb_dump_bts(quad_mesh_with_defaults))

    assert [mesh2.vertex_attribute(v, "weight") for v in mesh2.vertices()] == [1.5, 9.0, 1.5, 1.5]
    assert [mesh2.vertex_attribute(v, "tag") for v in mesh2.vertices()] == ["none", "none", "none", "corner"]


def test_roundtrip_preserves_default_attribute_maps(quad_mesh_with_defaults):
    mesh2 = pb_load_bts(pb_dump_bts(quad_mesh_with_defaults))

    assert mesh2.default_vertex_attributes["weight"] == 1.5
    assert mesh2.default_vertex_attributes["tag"] == "none"
    assert mesh2.default_face_attributes == {"thickness": 0.25}
    assert mesh2.default_edge_attributes == {"stiffness": 10.0}


def test_roundtrip_preserves_non_geometry_face_and_edge_attributes(quad_mesh_with_defaults):
    mesh2 = pb_load_bts(pb_dump_bts(quad_mesh_with_defaults))

    assert [mesh2.face_attribute(f, "thickness") for f in mesh2.faces()] == [0.75]
    assert sorted(mesh2.edge_attribute(e, "stiffness") for e in mesh2.edges()) == [10.0, 10.0, 10.0, 99.0]


def test_defaults_stay_defaults_after_roundtrip():
    # Vertices that never set the attribute must still resolve it through the defaults map,
    # rather than having the default baked into each element at serialization time.
    mesh = Mesh()
    mesh.update_default_vertex_attributes(weight=1.5)
    a = mesh.add_vertex(x=0.0, y=0.0, z=0.0)
    b = mesh.add_vertex(x=1.0, y=0.0, z=0.0)
    c = mesh.add_vertex(x=1.0, y=1.0, z=0.0)
    mesh.add_face([a, b, c])

    mesh2 = pb_load_bts(pb_dump_bts(mesh))
    mesh2.update_default_vertex_attributes(weight=7.0)

    assert [mesh2.vertex_attribute(v, "weight") for v in mesh2.vertices()] == [7.0, 7.0, 7.0]


def test_roundtrip_preserves_sparse_attribute_without_default():
    # Only one vertex carries the attribute and no default declares it, so the column is
    # stored sparsely and the others must come back as None.
    mesh = Mesh()
    a = mesh.add_vertex(x=0.0, y=0.0, z=0.0)
    b = mesh.add_vertex(x=1.0, y=0.0, z=0.0)
    c = mesh.add_vertex(x=1.0, y=1.0, z=0.0)
    mesh.add_face([a, b, c])
    mesh.vertex_attribute(b, "load", 42.0)

    mesh2 = pb_load_bts(pb_dump_bts(mesh))

    assert [mesh2.vertex_attribute(v, "load") for v in mesh2.vertices()] == [None, 42.0, None]


def test_roundtrip_preserves_non_float_attribute_types():
    mesh = Mesh()
    mesh.update_default_vertex_attributes(count=1, flag=False, label="x", ratio=0.5)
    a = mesh.add_vertex(x=0.0, y=0.0, z=0.0, count=7, flag=True, label="hi", ratio=2.5)
    b = mesh.add_vertex(x=1.0, y=0.0, z=0.0)
    c = mesh.add_vertex(x=1.0, y=1.0, z=0.0)
    mesh.add_face([a, b, c])

    mesh2 = pb_load_bts(pb_dump_bts(mesh))

    for name, expected in [("count", [7, 1, 1]), ("flag", [True, False, False]), ("label", ["hi", "x", "x"]), ("ratio", [2.5, 0.5, 0.5])]:
        values = [mesh2.vertex_attribute(v, name) for v in mesh2.vertices()]
        assert values == expected
        assert [type(v) for v in values] == [type(e) for e in expected]
