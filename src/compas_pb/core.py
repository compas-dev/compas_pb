import base64
from importlib.metadata import version
from typing import Any
from typing import Union

import compas
from compas.data import Data
from compas.data import DataDecoder
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse

from compas_pb.generated import message_pb2

from .registry import SerializerRegistry

_CURRENT_VERSION: str = version("compas_pb")


def _ensure_serializers():
    from .plugin import PLUGIN_MANAGER

    PLUGIN_MANAGER.discover_plugins()


def _decode_dict(data_dict: dict) -> Data:
    return DataDecoder().object_hook(data_dict)


def primitive_to_pb(obj: Union[int, float, bool, str, bytes]) -> message_pb2.AnyData:
    """
    Convert a python native type to a protobuf message.

    Parameters
    ----------
    obj : :class: `int`, `float`, `bool`, `str`, `bytes`
        The python native type to convert.

    Returns
    -------
    :class: `compas_pb.generated.message_pb2.AnyData`
        The protobuf message type of AnyData.
    """

    data_offset = message_pb2.AnyData()

    type_ = type(obj)
    if type_ is type(None):
        data_offset.value.null_value = 0  # this just needs to be set to any integer value to indicate null
    elif type_ is int:
        data_offset.int_value = obj  # explicit int arm: preserves the int/float distinction
    elif type_ is float:
        data_offset.double_value = obj  # explicit float arm: an integral float stays a float
    elif type_ is bool:
        data_offset.value.bool_value = obj
    elif type_ is str:
        data_offset.value.string_value = obj
    elif type_ is bytes:
        data_offset.value.string_value = "base64:" + base64.b64encode(obj).decode("utf-8")  # Add base64: prefix
    else:
        raise TypeError(f"Unsupported type: {type_}")

    return data_offset


def primitive_from_pb(primitive: message_pb2.AnyData) -> Union[int, float, bool, str, bytes]:
    """Convert a protobuf message to a python native type.

    Parameters
    ----------
    proto_data : :class: `compas_pb.generated.message_pb2.AnyData`
        The protobuf message type of Anydata(contains struct_pb2.Value).

    Returns
    -------
    data_offset : Union[int, float, bool, str, bytes]
        The converted python native type.
    """
    type_ = primitive.value.WhichOneof("kind")
    if type_ == "null_value":
        data_offset = None
    elif type_ == "number_value":
        # Legacy path only: int/float now use the explicit int_value/double_value arms.
        data_offset = primitive.value.number_value
    elif type_ == "bool_value":
        data_offset = primitive.value.bool_value
    elif type_ == "string_value":
        data_offset = primitive.value.string_value
        if data_offset.startswith("base64:"):
            data_offset = base64.b64decode(data_offset[7:])
    else:
        raise ValueError(f"Unsupported primitive type: {type_}")

    return data_offset


def any_to_pb(obj: Union[compas.data.Data, int, float, bool, str, bytes]) -> message_pb2.AnyData:
    """Convert any object to a protobuf any message.

    Parameters
    ----------
    obj : Union[compas.data.Data, list, dict, int, float, bool, str]
        The object to convert. Can be a COMPAS Data object, list, dict, or primitive type.

    Returns
    -------
        :class: `compas_pb.generated.message_pb2.AnyData`
            The protobuf message type of AnyData.
    """
    if not SerializerRegistry._SERIALIZERS or not SerializerRegistry._DESERIALIZERS:
        _ensure_serializers()

    proto_data = message_pb2.AnyData()

    try:
        serializer = SerializerRegistry.get_serializer(obj)
        if serializer:
            pb_obj = serializer(obj)
            proto_data.message.Pack(pb_obj)
        elif isinstance(obj, Data):
            proto_data = _serialize_fallback(obj)
        else:
            proto_data = primitive_to_pb(obj)
        return proto_data
    except TypeError as e:
        raise TypeError(f"Unsupported type: {type(obj)}: {e}")


def any_from_pb(proto_data: message_pb2.AnyData) -> Union[compas.data.Data, int, float, bool, str, bytes]:
    """Convert a protobuf message to a supported object.

    Parameters
    ----------
    proto_data : :class: `compas_pb.generated.message_pb2.AnyData`
        The protobuf message type of AnyData.

    Returns
    -------
    Union[compas.data.Data, list, dict, int, float, bool, str]
        The converted object. Can be a COMPAS Data object, list, dict, or primitive type.
    """
    if not SerializerRegistry._SERIALIZERS or not SerializerRegistry._DESERIALIZERS:
        _ensure_serializers()

    union_field = proto_data.WhichOneof("data")
    if union_field == "value":
        return primitive_from_pb(proto_data)
    elif union_field == "int_value":
        return proto_data.int_value
    elif union_field == "double_value":
        return proto_data.double_value
    elif union_field == "fallback":
        return _deserialize_fallback(proto_data)
    elif union_field == "message":
        return _handle_known_type(proto_data)
    else:
        raise NameError(f"Unexpected AnyData field: {union_field}")


def _handle_known_type(proto_data: message_pb2.AnyData, proto_type: str = None) -> Any:
    # type.googleapis.com/<fully.qualified.message.name>
    if proto_type is None:
        proto_type = proto_data.message.type_url.rpartition("/")[2]

    deserializer = SerializerRegistry.get_deserializer(proto_type)
    if not deserializer:
        raise TypeError(f"Unsupported proto type: {proto_type}")

    unpacked_instance = deserializer.__protobuf_cls__()
    # The registry lookup above has already selected the message class from Any's
    # type URL. Parsing its payload directly avoids making Any.Unpack validate and
    # split that same URL again for every object in a collection.
    unpacked_instance.ParseFromString(proto_data.message.value)
    return deserializer(unpacked_instance)


def serialize_message(data) -> message_pb2.MessageData:
    """Serialize a top-level protobuf message.

    Parameters
    ----------
    data : object
        The data to be serialized. This can be a COMPAS object, a list of objects, or a dictionary.

    Returns
    -------
    message : message_pb2.MessageData

    """
    if not data:
        raise ValueError("No message data to convert.")

    _ensure_serializers()
    message_data = _serializer_any(data)
    message = message_pb2.MessageData(data=message_data, version=_CURRENT_VERSION)
    return message


def serialize_message_bts(data) -> bytes:
    """Serialize a top-level protobuf message.

    Parameters
    ----------
    data : object
        The data to be serialized. This can be a COMPAS object, a list of objects, or a dictionary.

    Returns
    -------
    message : bytes
        The serialized protobuf message as bytes.

    """
    message = serialize_message(data)
    message_bts = message.SerializeToString()
    return message_bts


def serialize_message_to_json(data) -> dict:
    """Serialize a top-level protobuf message.

    Parameters
    ----------
    data : object
        The data to be serialized. This can be a COMPAS object, a list of objects, or a dictionary.

    Returns
    -------
    message : dict
        The serialized protobuf message as a dictionary.

    """
    message = serialize_message(data)
    message_json = MessageToJson(message)
    return message_json


def _serializer_any(obj) -> message_pb2.AnyData:
    """Serialize a COMPAS object to protobuf message."""
    any_data = message_pb2.AnyData()

    if isinstance(obj, (list, tuple)):
        # Explicit list arm — avoids the google.protobuf.Any type_url on every nested list.
        any_data.list_value.CopyFrom(_serialize_list(obj))
    elif isinstance(obj, dict):
        # Explicit dict arm — avoids the google.protobuf.Any type_url on every nested dict.
        any_data.dict_value.CopyFrom(_serialize_dict(obj))
    else:
        # check if it is COMPAS object or Python native type or fallback to dictionary.
        any_data = any_to_pb(obj)
    return any_data


def _serialize_list(data_list) -> message_pb2.ListData:
    """Serialize a Python list containing mixed data type."""
    list_data = message_pb2.ListData()
    for item in data_list:
        data_offset = _serializer_any(item)
        list_data.items.append(data_offset)
    return list_data


def _serialize_dict(data_dict) -> message_pb2.DictData:
    """Serialize a Python dictionary containing mixed data types."""
    dict_data = message_pb2.DictData()
    for key, value in data_dict.items():
        data_offset = _serializer_any(value)
        dict_data.items[key].CopyFrom(data_offset)
    return dict_data


def _serialize_fallback(obj: Data) -> message_pb2.AnyData:
    """Fallback serializer to convert a dictionary to protobuf DictData."""
    result = message_pb2.AnyData()
    fallback_data = message_pb2.FallbackData()
    dict_data: message_pb2.DictData = _serialize_dict(obj.__jsondump__())
    fallback_data.data.CopyFrom(dict_data)
    result.fallback.CopyFrom(fallback_data)
    return result


def deserialize_message(binary_data) -> Union[list, dict]:
    """Deserialize a top-level protobuf message.

    Parameters
    ----------
    binary_data : bytes
        The binary data to be deserialized.

    Returns
    -------
    message : Union[list, dict]
        The deserialized protobuf message.

    """
    message_data = deserialize_message_bts(binary_data)
    return _deserialize_any(message_data)


def deserialize_message_bts(binary_data) -> message_pb2.MessageData:
    """Deserialize a binary data into bytes string.

    Parameters
    ----------
    binary_data : bytes
        The binary data to be deserialized.

    Returns
    -------
    message_data : message_pb2.MessageData
        The protobuf message data.

    """
    if not binary_data:
        raise ValueError("Binary data is empty.")

    _ensure_serializers()
    any_data = message_pb2.MessageData()
    any_data.ParseFromString(binary_data)

    _check_version_compatibility(any_data)

    return any_data.data


def deserialize_message_from_json(json_data: str) -> dict:
    """Deserialize a top-level protobuf message into dictionary.

    Parameters
    ----------
    json_data : str
        A JSON string representation of the data.

    Returns
    -------
    message : dict
        The deserialized protobuf message as a dictionary.

    """
    if not json_data:
        raise ValueError("No message data to convert.")

    _ensure_serializers()
    message = message_pb2.MessageData()
    json_message = Parse(json_data, message)

    any_data = message_pb2.MessageData()
    any_data.CopyFrom(json_message)

    _check_version_compatibility(any_data)

    return _deserialize_any(any_data.data)


def _deserialize_any(data: Union[message_pb2.AnyData, message_pb2.ListData, message_pb2.DictData]) -> Union[list, dict]:
    """Deserialize a protobuf message to COMPAS object."""
    field = data.WhichOneof("data")
    if field == "list_value":
        data_offset = _deserialize_list(data.list_value)
    elif field == "dict_value":
        data_offset = _deserialize_dict(data.dict_value)
    elif field == "message":
        proto_type = data.message.type_url.rpartition("/")[2]
        if proto_type == message_pb2.ListData.DESCRIPTOR.full_name:  # legacy: list in Any
            list_data = message_pb2.ListData.FromString(data.message.value)
            data_offset = _deserialize_list(list_data)
        elif proto_type == message_pb2.DictData.DESCRIPTOR.full_name:  # legacy: dict in Any
            dict_data = message_pb2.DictData.FromString(data.message.value)
            data_offset = _deserialize_dict(dict_data)
        else:
            data_offset = _handle_known_type(data, proto_type)
    else:
        data_offset = any_from_pb(data)
    return data_offset


def _deserialize_list(data_list: message_pb2.ListData) -> list:
    """Deserialize a protobuf ListData message to Python list."""
    data_offset = []
    for item in data_list.items:
        data_offset.append(_deserialize_any(item))
    return data_offset


def _deserialize_dict(data_dict: message_pb2.DictData) -> dict:
    """Deserialize a protobuf DictData message to Python dictionary."""
    data_offset = {}
    for key, value in data_dict.items.items():
        data_offset[key] = _deserialize_any(value)
    return data_offset


def _deserialize_fallback(data_dict: message_pb2.AnyData) -> Data:
    """Fallback deserializer to convert a protobuf FallbackData message to Python dictionary."""
    obj_data = _deserialize_dict(data_dict.fallback.data)
    return _decode_dict(obj_data)


def _wire_compat_key(version_str: str) -> str:
    """Wire-compatibility key of a version, following SemVer.

    Under 0.x there is no stability guarantee, so every minor release may change the binary
    schema: the key is ``MAJOR.MINOR`` (``0.5.x`` is compatible with ``0.5.y`` but not with
    ``0.6.x``). From 1.0 on, ``MAJOR`` is the boundary and minor releases stay
    backwards-compatible: the key is ``MAJOR`` (``1.0`` and ``1.2`` are compatible; ``2.0``
    is not).
    """
    parts = str(version_str).split(".")
    major = parts[0]
    if major == "0" and len(parts) >= 2:
        return "0.{}".format(parts[1])
    return major


def _check_version_compatibility(any_data: message_pb2.MessageData) -> None:
    """Raise if the message's wire version is incompatible with this build.

    compas_pb reuses protobuf field numbers across format revisions, so data written by an
    incompatible version can *silently misparse* rather than fail cleanly. A missing or
    mismatched wire version is therefore a hard error, not a warning.
    """
    incoming = any_data.version or ""
    if not incoming:
        raise ValueError(
            "No version tag in the message; cannot verify compas_pb wire-format compatibility "
            "(reader is {}).".format(_CURRENT_VERSION)
        )
    if _wire_compat_key(incoming) != _wire_compat_key(_CURRENT_VERSION):
        raise ValueError(
            "Incompatible compas_pb wire format: message was written by version {} but this "
            "reader is {}. The binary schema differs between these versions; re-serialize the "
            "source or read it with a matching compas_pb version.".format(incoming, _CURRENT_VERSION)
        )
