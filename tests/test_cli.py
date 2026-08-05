import pytest

from compas_pb import pb_load_bts
from compas_pb.cli import detect_wire_version
from compas_pb.cli import main
from compas_pb.cli import migrate_bytes


@pytest.fixture
def legacy_blob():
    # Genuinely written by compas_pb 0.5.0, not synthesized: a mesh with mesh-level and
    # vertex-level attributes plus a pointcloud, so it uses the pre-1.0 per-point message and
    # map-based attribute layouts that this build can no longer parse. Regenerate with:
    #   uv run --no-project --with compas_pb==0.5.0 python -c "..."
    with open("tests/test_data/mesh_v0.5.0.data", "rb") as f:
        return f.read()


@pytest.fixture
def current_blob():
    with open("tests/test_data/frame.data", "rb") as f:
        return f.read()


def test_detect_wire_version(legacy_blob, current_blob):
    assert detect_wire_version(legacy_blob) == "0.5.0"
    assert detect_wire_version(current_blob) == "1.0.0"


def test_detect_wire_version_without_tag(legacy_blob):
    # Blobs written before v0.4.1 carry no version field at all.
    stripped = legacy_blob[: legacy_blob.rfind(b"\x12\x050.5.0")]
    assert detect_wire_version(stripped) is None


def test_detect_wire_version_rejects_garbage():
    with pytest.raises(ValueError):
        detect_wire_version(b"\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff")


def test_migrate_refuses_current_data(current_blob):
    with pytest.raises(ValueError, match="already readable"):
        migrate_bytes(current_blob)


def test_migrate_needs_explicit_version_when_untagged(legacy_blob):
    stripped = legacy_blob[: legacy_blob.rfind(b"\x12\x050.5.0")]
    with pytest.raises(ValueError, match="no version tag"):
        migrate_bytes(stripped)


def test_legacy_blob_is_refused_by_the_gate(legacy_blob):
    with pytest.raises(ValueError, match="Incompatible compas_pb wire format"):
        pb_load_bts(legacy_blob)


def test_inspect_reports_versions(legacy_blob, capsys):
    assert main(["migrate", "tests/test_data/mesh_v0.5.0.data", "--inspect"]) == 0
    out = capsys.readouterr().out
    assert "0.5.0" in out
    assert "needs migration" in out


@pytest.mark.network
def test_migrate_legacy_blob(legacy_blob):
    """Full migration through an ephemeral environment holding compas_pb 0.5.0."""
    migrated = migrate_bytes(legacy_blob)

    data = pb_load_bts(migrated)
    mesh, cloud = data["mesh"], data["cloud"]

    assert mesh.attributes["label"] == "old-blob"
    assert mesh.face_vertices(0) == [0, 1, 2, 3]
    assert [mesh.vertex_attribute(v, "load") for v in mesh.vertices()] == [0, 1.5, 3, 4.5]
    assert len(cloud.points) == 2
    # Guids that were on the old wire come back as explicitly set, so they survive the
    # re-encode even though 1.0 no longer serializes auto-generated ones.
    assert mesh.guid is not None
