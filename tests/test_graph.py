from compas.datastructures import Graph
import compas_pb


def test_graph_serialization():
    g = Graph(name="TestGraph")
    g.update_default_node_attributes({"test": 123})
    g.add_node(x=1, y=2, z=3, my_attr="hello")
    g.add_node(x=4, y=5, z=6)
    g.add_edge(0, 1, weight=5.5)

    pb_data = compas_pb.pb_dump_bts(g)
    g_restored: Graph = compas_pb.pb_load_bts(pb_data)

    assert g_restored.name == "TestGraph"
    assert g_restored.number_of_nodes() == 2
    assert g_restored.number_of_edges() == 1

    # check default attr
    assert g_restored.default_node_attributes["test"] == 123

    # check specific node attr
    assert g_restored.node_attribute(0, "my_attr") == "hello"

    # check edge attr
    assert g_restored.edge_attribute((0, 1), "weight") == 5.5
