"""Command line interface for compas_pb."""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from importlib.metadata import version

import compas

from compas_pb.api import pb_dump_bts
from compas_pb.api import pb_load_bts
from compas_pb.core import _wire_compat_key

_CURRENT_VERSION: str = version("compas_pb")

# Runs inside the ephemeral environment of the *writing* version, so it may only use API that
# version already had. ``pb_load`` and COMPAS JSON are the two things stable across all of them.
_DECODE_SCRIPT = """
import sys
import compas
from compas_pb import pb_load

compas.json_dump(pb_load(sys.argv[1]), sys.argv[2])
"""


def _read_varint(buf: bytes, pos: int):
    """Read a base-128 varint from ``buf`` at ``pos``, returning ``(value, new_pos)``."""
    result = 0
    shift = 0
    while True:
        if pos >= len(buf):
            raise ValueError("truncated varint")
        byte = buf[pos]
        pos += 1
        result |= (byte & 0x7F) << shift
        if not byte & 0x80:
            return result, pos
        shift += 7
        if shift > 63:
            raise ValueError("varint overflows 64 bits")


def detect_wire_version(blob: bytes):
    """Read ``MessageData.version`` out of a blob without parsing its payload.

    The payload of an incompatible blob cannot be parsed by this build -- that is the whole
    reason migration is needed -- so this walks only the top-level fields, skipping field 1
    (``data``) by its length prefix. ``version`` has been field 2 of ``MessageData`` since the
    tag was introduced, and top-level framing has not changed since.

    Returns ``None`` for a blob written before the version tag existed.
    """
    pos = 0
    end = len(blob)
    while pos < end:
        tag, pos = _read_varint(blob, pos)
        field_no, wire_type = tag >> 3, tag & 0x07
        if wire_type == 0:
            _, pos = _read_varint(blob, pos)
        elif wire_type == 1:
            pos += 8
        elif wire_type == 5:
            pos += 4
        elif wire_type == 2:
            length, pos = _read_varint(blob, pos)
            if field_no == 2:
                return blob[pos : pos + length].decode("utf-8")
            pos += length
        else:
            raise ValueError("unsupported protobuf wire type {}; not a compas_pb message".format(wire_type))
    return None


def _decode_with(source_version: str, blob: bytes, python: str = None) -> str:
    """Decode ``blob`` in an ephemeral environment holding ``source_version``, returning COMPAS JSON."""
    if shutil.which("uv") is None:
        raise RuntimeError("`uv` is required to migrate older data but was not found on PATH. See https://docs.astral.sh/uv/getting-started/installation/")

    workdir = tempfile.mkdtemp(prefix="compas_pb_migrate_")
    blob_path = os.path.join(workdir, "source.pb")
    json_path = os.path.join(workdir, "bridge.json")
    script_path = os.path.join(workdir, "decode.py")
    try:
        with open(blob_path, "wb") as f:
            f.write(blob)
        with open(script_path, "w") as f:
            f.write(_DECODE_SCRIPT)

        cmd = ["uv", "run", "--no-project", "--quiet"]
        if python:
            cmd += ["--python", python]
        cmd += ["--with", "compas_pb=={}".format(source_version), "python", script_path, blob_path, json_path]

        result = subprocess.run(cmd, capture_output=True, text=True, cwd=workdir)
        if result.returncode != 0:
            raise RuntimeError("failed to read the data with compas_pb {}:\n{}".format(source_version, (result.stderr or result.stdout).strip()))

        with open(json_path, "r") as f:
            return f.read()
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def migrate_bytes(blob: bytes, source_version: str = None, python: str = None) -> bytes:
    """Re-encode a blob written by an older compas_pb into the current wire format.

    Parameters
    ----------
    blob : bytes
        The serialized data to migrate.
    source_version : str, optional
        Version that wrote the blob. Detected from the blob when omitted, which is only
        possible if it carries a version tag.
    python : str, optional
        Python version for the ephemeral environment, e.g. ``"3.12"``.

    Returns
    -------
    bytes
        The same data in the current wire format.

    """
    if source_version is None:
        source_version = detect_wire_version(blob)
    if source_version is None:
        raise ValueError("this blob carries no version tag, so the version that wrote it cannot be detected; pass --from-version explicitly")

    if _wire_compat_key(source_version) == _wire_compat_key(_CURRENT_VERSION):
        raise ValueError("data written by {} is already readable by this build ({}); no migration needed".format(source_version, _CURRENT_VERSION))

    bridge = _decode_with(source_version, blob, python=python)
    migrated = pb_dump_bts(compas.json_loads(bridge))

    # Cheap proof the result is readable before it reaches the user's disk.
    pb_load_bts(migrated)
    return migrated


def _cmd_migrate(args) -> int:
    blob = sys.stdin.buffer.read() if args.input == "-" else open(args.input, "rb").read()
    if not blob:
        print("error: no input data", file=sys.stderr)
        return 1

    if args.inspect:
        detected = detect_wire_version(blob)
        print("written by:  {}".format(detected or "<no version tag>"))
        print("this build:  {}".format(_CURRENT_VERSION))
        if detected and _wire_compat_key(detected) == _wire_compat_key(_CURRENT_VERSION):
            print("status:      readable as-is")
        else:
            print("status:      needs migration")
        return 0

    if args.output == "-" and sys.stdout.isatty():
        print("error: refusing to write binary data to a terminal; pass -o OUTPUT or redirect stdout", file=sys.stderr)
        return 1

    try:
        migrated = migrate_bytes(blob, source_version=args.from_version, python=args.python)
    except (ValueError, RuntimeError) as e:
        print("error: {}".format(e), file=sys.stderr)
        return 1

    if args.output == "-":
        sys.stdout.buffer.write(migrated)
    else:
        with open(args.output, "wb") as f:
            f.write(migrated)
        print("migrated {} -> {} ({} bytes)".format(args.input, args.output, len(migrated)), file=sys.stderr)
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="compas_pb", description="Utilities for compas_pb serialized data.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    migrate = subparsers.add_parser(
        "migrate",
        help="re-encode data written by an older compas_pb into the current wire format",
        description=(
            "Reads a blob written by an older compas_pb, decodes it in an ephemeral environment "
            "holding that version, and re-encodes it with this one. Requires `uv` and network "
            "access the first time a given version is fetched."
        ),
    )
    migrate.add_argument("input", help="path to the data to migrate, or - for stdin")
    migrate.add_argument("-o", "--output", default="-", help="where to write the migrated data, or - for stdout (default)")
    migrate.add_argument("--from-version", default=None, help="version that wrote the data; detected from the blob when omitted")
    migrate.add_argument("--python", default=None, help="python version for the ephemeral environment, e.g. 3.12")
    migrate.add_argument("--inspect", action="store_true", help="report the version that wrote the data and exit")
    migrate.set_defaults(func=_cmd_migrate)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
