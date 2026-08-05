# Migrating older data

`compas_pb` refuses to read data written by an incompatible version. If you have blobs written
by an older release, `compas_pb migrate` re-encodes them into the current wire format.

```bash
compas_pb migrate old.pb -o new.pb
```

## Why old data is refused rather than best-effort parsed

`compas_pb` reuses protobuf field numbers across format revisions. Version 1.0.0 changed what
those fields hold: coordinates went from `float` to `double`, mesh points went from one message
per point to a packed `repeated double`, faces moved to CSR form, and per-element attributes
became columnar. Protobuf does not reject a blob whose field numbers still line up, so an old
blob read by a new build can *silently misparse* into plausible-looking but wrong geometry.

Deserialization therefore checks the version tag and raises rather than guessing. Compatibility
follows SemVer: under `0.x` every minor release is a break, and from `1.0` on only major bumps
are. So `1.0` and `1.2` interoperate, while `0.5` and `1.0` do not.

## How migration works

There is no way to read both wire formats in one process, the two builds generate protobuf
descriptors from the same file path, and only one can be registered at a time. So `migrate`
decodes the data in a throwaway environment holding the version that *wrote* it, bridges through
COMPAS JSON, and re-encodes with the current version:

```
old.pb ──> [ephemeral env, compas_pb 0.5.0] ──> COMPAS JSON ──> [this build] ──> new.pb
```

This needs [`uv`](https://docs.astral.sh/uv/) on `PATH`, and network access the first time a
given old version is fetched. Nothing is installed into your own environment.

## Usage

```bash
# Check what wrote a blob, without migrating it
compas_pb migrate old.pb --inspect

# File in, file out
compas_pb migrate old.pb -o new.pb

# Pipes work too
cat old.pb | compas_pb migrate - > new.pb

# Blobs written before v0.4.1 carry no version tag, so name the version yourself
compas_pb migrate ancient.pb --from-version 0.3.1 -o new.pb

# Pin the interpreter for the ephemeral environment
compas_pb migrate old.pb --python 3.12 -o new.pb
```

Migrating a directory is a shell loop:

```bash
for f in data/*.pb; do compas_pb migrate "$f" -o "migrated/$(basename "$f")"; done
```

The same thing is available from Python:

```python
from compas_pb.cli import migrate_bytes

with open("old.pb", "rb") as f:
    migrated = migrate_bytes(f.read())
```

## What survives, and what does not

Geometry, datastructures, attributes and explicitly set guids all come across. Two caveats are
inherent to the old data rather than to migration:

- **Precision is not recovered.** Pre-1.0 coordinates were `float32` on the wire. Migration
  preserves exactly what was stored, so a point written as `0.1` comes back as
  `0.10000000149011612`. It will now round-trip losslessly from here on, but the precision the
  old format discarded is gone.
- **Integral floats may arrive as ints.** Pre-1.0 routed values through `google.protobuf.Value`,
  which returned whole numbers as `int`. A vertex attribute written as `3.0` migrates as `3`.
  This is the old reader's behaviour, faithfully carried forward.

Auto-generated guids are a non-issue in practice: a guid that was on the old wire is treated as
explicitly set when read back, so it survives the re-encode even though 1.0 no longer serializes
session-local ones.

!!! note

    `compas_pb` output is not byte-for-byte reproducible: protobuf serializes map fields in an
    unspecified order, so migrating the same blob twice yields equal data in different bytes.
    Compare deserialized objects, not hashes.
