from compas.datastructures import Mesh
import compas_pb


def test_mesh_attributes_serialization():
    m = Mesh(name="TestMesh")
    m.attributes["mesh_attr"] = "mesh_level"

    m.update_default_vertex_attributes({"v_def": 123})
    m.update_default_face_attributes({"f_def": 456})
    m.update_default_edge_attributes({"e_def": 789})

    m.add_vertex(x=1, y=2, z=3, v_attr="v_val")
    m.add_vertex(x=4, y=5, z=6)
    m.add_vertex(x=7, y=8, z=9)
    m.add_face([0, 1, 2], f_attr="f_val")
    m.edge_attribute((0, 1), name="e_attr", value="e_val")

    pb_data = compas_pb.pb_dump_bts(m)
    m_restored: Mesh = compas_pb.pb_load_bts(pb_data)

    assert m_restored.name == "TestMesh"
    assert m_restored.attributes["mesh_attr"] == "mesh_level"
    assert m_restored.default_vertex_attributes["v_def"] == 123
    assert m_restored.default_face_attributes["f_def"] == 456
    assert m_restored.default_edge_attributes["e_def"] == 789
    assert m_restored.vertex_attribute(0, "v_attr") == "v_val"
    assert m_restored.face_attribute(0, "f_attr") == "f_val"
    assert m_restored.edge_attribute((0, 1), "e_attr") == "e_val"
    assert m_restored.vertex_point(0) == [1, 2, 3]
    assert m_restored.vertex_point(1) == [4, 5, 6]
    assert m_restored.vertex_point(2) == [7, 8, 9]
