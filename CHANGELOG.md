# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added

### Changed

### Removed


## [1.0.0] 2026-08-05

### Added

### Changed

* Breaking: The wire format changed in a way that is not backwards compatible. Once the version is bumped at release, data serialized by older versions will be refused on deserialization (the wire-version check is now a hard gate; compatibility follows SemVer — under 0.x every minor is breaking, from 1.0 on only major bumps are).
* Breaking: Auto-generated guids no longer round-trip. They were always session-local `uuid4`s and never stable across save/load; only explicitly set guids are now serialized.
* Reworked the wire format into a fully lossless binary mode: all geometry coordinate/scalar fields are now `double` instead of `float`, so `float64` geometry round-trips exactly.
* Changed `AnyData` to use explicit `int64`/`double`/`dict_value`/`list_value` arms instead of routing values through `google.protobuf.Value`/`Any`, so integral floats no longer come back as ints and nested dicts/lists no longer carry a type URL. `Mesh`/`Graph` are now fully lossless (canonical hash matches).
* Changed mesh vertices, pointcloud, polyline, polygon, bezier and polyhedron points to a flat packed `repeated double` layout, and mesh faces to CSR form (`face_vertices` + `face_sizes`), instead of one message per point/face.
* Changed per-element attributes (mesh vertices/faces/edges and graph nodes/edges) to a columnar `repeated AttributeColumn` layout with packed numeric arrays, replacing the previous per-element `map<string, AnyData>`. Empty/absent attribute sets cost nothing.
* Changed `GraphData` to store node keys once, node attributes (including `x`/`y`/`z`) column-wise, and edges as index pairs into the node keys.
* Changed `guid` and `name` to only be serialized when explicitly set. Auto-generated guids (session-local `uuid4`s) no longer round-trip; explicit guids still do.
* Changed `Rotation` to be stored as its flattened 4x4 matrix (like other transforms) and reconstructed via `Rotation.from_matrix`, so rotations round-trip bit-exact.
* Changed the wire-version check into a hard gate: deserialization now raises on a missing or incompatible wire version (compatibility follows SemVer) instead of warning and continuing.

### Removed


## [0.5.0] 2026-05-08

### Added

* Added support for attributes of `compas.datastructures.Mesh` (mesh, edges, vertices, faces attributes) to be serialized and deserialized. PointData is backwards compatible with previous versions, so vertex attributes are filtered to remove `x`, `y`, `z` keys.
* Added support for `compas.datastructures.Graph` serialization and deserialization.

### Changed

### Removed


## [0.4.10] 2026-04-15

### Added

### Changed

* Better handling of os and architecture combinations in the invocations module.

### Removed


## [0.4.9] 2026-02-16

### Added

### Changed

* Refactored proto definitions from 31 separate files into three organized files (`geometry.proto`, `datastructures.proto`, `message.proto`) to better reflect COMPAS package structure.
* Fixed `guid` isn't maintained round-trip on some types.

### Removed


## [0.4.8] 2026-01-05

### Added

### Changed

* Migrated documentation to mkdocs.

### Removed


## [0.4.7] 2025-12-11

### Added

* Added support for `generate-proto-classes` to create `.pyi` files for generated Python classes.

### Changed

* Migrated the documentation website to MkDocs Material from Sphinx.

### Removed


## [0.4.6] 2025-11-17

### Added

### Changed

* Fixed handling of serialized `None` values.

### Removed


## [0.4.5] 2025-11-03

### Added

### Changed

* Fixed empty assets `zip` file with different language support.

### Removed


## [0.4.4] 2025-10-16

### Added

### Changed

### Removed


## [0.4.3] 2025-10-16

### Added

### Changed

### Removed


## [0.4.2] 2025-10-16

### Added

* Added support for `compas.geometry.Capsule` serialization and deserialization.
* Added support for `compas.geometry.Quaternion` serialization and deserialization.
* Added support for `compas.geometry.Scale` serialization and deserialization.
* Added support for `compas.geometry.Reflection` serialization and deserialization.
* Added support for `compas.geometry.Shear` serialization and deserialization.
* Added support for `compas.geometry.Projection` serialization and deserialization.
* Added support for `compas.geometry.Bezier` serialization and deserialization.
* Added support for `compas.geometry.Hyperbola` serialization and deserialization.
* Added support for `compas.geometry.Parabola` serialization and deserialization.
* Added support for `compas.geometry.Polyhedron` serialization and deserialization.

### Changed

* Fixed running `protoc` fails with permission denied on Mac.

### Removed


## [0.4.1] 2025-10-13

### Added

### Changed

* Fixed `invoke` task to work on MacOS with Apple Silicon.

### Removed


## [0.4.0] 2025-09-10

### Added

* Added attribute `version` in `message.proto` to track/ship the package version
* Added `.proto` file into build package.
* Added `FallbackData` member `fallback` to `AnyData` to allow for fallback serialization of unknown types.

### Changed

* Changed plugin discovery to use entry points instead of the COMPAS plugin system's name scanning.
* Added `importlib_metadata` as a conditional dependency to support Python <= 3.9.
* Renamed `compas_pb.IDL` to `compas_pb.PROTOBUF_DEFS`.

### Removed

* Removed `compas_pb.DATA`.
* Removed `compas_pb.DOCS`.
* Removed `compas_pb.TEMP`.


## [0.3.1] 2025-08-27

### Added

* Added `create_class_assets` for invoke task to package the proto generated class file with `cpp`, `csharp` into assets.

### Changed

* Fixed `compas_pb` support in Python 3.9.

### Removed


## [0.3.0] 2025-08-26

### Added

* Added module `compas_pb.invocations` which offers re-usable protobuf related tasks for plugins. 

### Changed

* remove `PrimitiveData` into `AnyData` with `Google.WellKownType.value`.

### Removed


## [0.2.0] 2025-08-20

### Added

* change `ListData.data` and `DictData.data` to better naming of `ListData.items` `DictData.items`.
* Added support for `compas.geometry.Plane` serialization and deserialization.
* Added support for `compas.geometry.Polygon` serialization and deserialization.
* Added support for `compas.geometry.Box` serialization and deserialization.
* Added support for `compas.geometry.Arc` serialization and deserialization.
* Added support for `compas.geometry.Sphere` serialization and deserialization.
* Added support for `compas.geometry.Cylinder` serialization and deserialization.
* Added support for `compas.geometry.Cone` serialization and deserialization.
* Added support for `compas.geometry.Torus` serialization and deserialization.
* Added support for `compas.geometry.Ellipse` serialization and deserialization.
* Added support for `compas.geometry.Polyline` serialization and deserialization.
* Added support for `compas.geometry.Pointcloud` serialization and deserialization.
* Added support for `compas.geometry.Transformation` serialization and deserialization.
* Added support for `compas.geometry.Translation` serialization and deserialization.
* Added support for `compas.geometry.Rotation` serialization and deserialization.

### Changed

### Removed


## [0.1.1] 2025-08-07

### Added

### Changed

* Removed debug print from registration.
* Added missing docs URL to the README.

### Removed


## [0.1.0] 2025-08-07

### Added

### Changed

* Changed to use the native protobuf Any to deal with our arbitrary data.

### Removed

