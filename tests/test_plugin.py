import pytest
import tempfile
from pathlib import Path

from compas.geometry import Frame

from compas_pb import pb_dump
from compas_pb import pb_load


@pytest.fixture
def frame_data_path():
    # Golden file written by a previous run, so this exercises reading bytes we did not just
    # produce in-process. The wire-version check is a hard gate, so it has to be regenerated
    # whenever the compatibility key changes (every minor under 0.x, every major from 1.0 on):
    #   python -c "from compas.geometry import Frame; from compas_pb import pb_dump; pb_dump(Frame.worldXY(), 'tests/test_data/frame.data')"
    return "tests/test_data/frame.data"


def test_register_plugins_called(mocker, frame_data_path):
    mock_register = mocker.patch("compas_pb.core._ensure_serializers")
    data = pb_load(frame_data_path)

    # register_serializers should be called at least once during deserialization
    mock_register.assert_called()

    assert data is not None
    assert data == Frame.worldXY()


def test_pb_dump_and_load_equivalence(mocker):
    """Test that pb_dump and pb_load work correctly together."""
    mock_register = mocker.patch("compas_pb.core._ensure_serializers")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir) / "frame_out.data"
        tmp_path = str(tmp_path)
        frame = Frame.worldXY()

        # Dump the Frame
        pb_dump(frame, tmp_path)

        # register_serializers should be called during serialization
        mock_register.assert_called()

        # Load it back
        loaded = pb_load(tmp_path)

        # Verify contents
        assert isinstance(loaded, Frame)
        assert loaded == frame  # Assumes __eq__ is implemented correctly
