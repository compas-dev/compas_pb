from __future__ import print_function

import os

from .api import pb_load
from .api import pb_dump
from .api import pb_dump_bts
from .api import pb_load_bts
from .api import pb_dump_json
from .api import pb_load_json


__author__ = ["Wei-Ting Chen", "Chen Kasirer"]
__copyright__ = "Gramazio Kohler Research"
__license__ = "MIT License"
__email__ = "kasirer@arch.ethz.ch"
__version__ = "0.5.0"


HERE = os.path.dirname(__file__)
HOME = os.path.abspath(os.path.join(HERE, "../../"))
PROTOBUF_DEFS = os.path.abspath(os.path.join(HERE, "protobuf_defs"))

__all__ = [
    "HOME",
    "PROTOBUF_DEFS",
    "pb_load",
    "pb_dump",
    "pb_dump_bts",
    "pb_load_bts",
    "pb_dump_json",
    "pb_load_json",
]
