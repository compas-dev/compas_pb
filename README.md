<p align="center">
    <img src="compas_pb.svg" alt="compas_pb" width="200">
</p>

<p align="center">
    <a href="https://pypi.org/project/compas_pb/"><img src="https://img.shields.io/pypi/v/compas_pb.svg" alt="PyPI version"></a>
    <a href="https://pypi.org/project/compas_pb/"><img src="https://img.shields.io/pypi/pyversions/compas_pb.svg" alt="Python versions"></a>
    <a href="https://github.com/compas-dev/compas_pb/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License MIT"></a>
    <a href="https://github.com/compas-dev/compas_pb/actions"><img src="https://github.com/compas-dev/compas_pb/actions/workflows/build.yml/badge.svg" alt="Build Status"></a>
    <a href="https://compas.dev/compas_pb"><img src="https://img.shields.io/badge/docs-latest-brightgreen.svg" alt="Documentation"></a>
    <a href="https://compas.dev/mission-control/#compas_pb"><img src="https://compas.dev/badge.svg" alt="Made with COMPAS"></a>
</p>

A COMPAS extension which lets you serialize and deserialize COMPAS `Data` types using protobuf.

## Installation

Stable releases can be installed from PyPI.

```bash
pip install compas_pb
```

## Basic Usage

### Serialize to file

```python
from compas.geometry import Vector
from compas_pb import pb_dump
from compas_pb import pb_load

PATH = "vector.data"

vector = Vector(1.0, 2.0, 3.0)

pb_dump(vector, PATH)

loaded_vector = pb_load(PATH)

```

### (De)serialize to bytes

```python
from compas.geometry import Vector
from compas_pb import pb_dump_bts
from compas_pb import pb_load_bts

vector = Vector(1.0, 2.0, 3.0)

bytes_vector = pb_dump_bts(vector)

loaded_vector = pb_load_bts(bytes_vector)

```

### Serialization of arbitrarily nested data structures

```python
from compas.geometry import Vector
from compas.geometry import Polyline
from compas_pb import pb_dump_bts
from compas_pb import pb_load_bts

data = {
    "direction": Vector(1.0, 2.0, 3.0),
    "outlines": 
        [
            Polyline([0, 0, 0], [1, 1, 1], [2, 2, 2]), 
            Polyline([3, 3, 3], [4, 4, 4], [5, 5, 5])
        ],
}

pb_data = pb_dump_bts(data)

loaded_data = pb_load_bts(pb_data)

```

## Documentation

For further "getting started" instructions, a tutorial, examples, and an API reference,
please check out the online documentation here: [compas_pb docs](https://compas.dev/compas_pb)

## Issue Tracker

If you find a bug or if you have a problem with running the code, please file an issue on the [Issue Tracker](https://github.com/compas-dev/compas_pb/issues).
