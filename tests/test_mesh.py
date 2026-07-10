import pytest

from compas.geometry import Box
from compas.datastructures import Mesh
from compas_pb import pb_dump_bts
from compas_pb import pb_load_bts


@pytest.fixture
def box_mesh():
    box = Box(1.0)
    return Mesh.from_shape(box)


def test_serialize_deserialize_box_mesh(box_mesh):
    data = pb_dump_bts(box_mesh)
    mesh2 = pb_load_bts(data)

    assert isinstance(mesh2, Mesh)
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
