# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: Client/ClientGRPC/Client.proto
# Protobuf Python Version: 5.29.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    29,
    0,
    '',
    'Client/ClientGRPC/Client.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1e\x43lient/ClientGRPC/Client.proto\x12\x06\x43lient\"\x15\n\x13\x43urrentStateRequest\"(\n\x14\x43urrentStateResponse\x12\x10\n\x08response\x18\x01 \x01(\t\"8\n\x0fLoadSongRequest\x12\x11\n\tsong_name\x18\x01 \x01(\t\x12\x12\n\naudio_data\x18\x02 \x01(\x0c\"#\n\x10LoadSongResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\"1\n\x10StartSongRequest\x12\r\n\x05start\x18\x01 \x01(\x01\x12\x0e\n\x06offset\x18\x02 \x01(\x01\"$\n\x11StartSongResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\"\x1f\n\x0fStopSongRequest\x12\x0c\n\x04stop\x18\x01 \x01(\x01\"#\n\x10StopSongResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x32\x93\x02\n\x06\x43lient\x12I\n\x0c\x43urrentState\x12\x1b.Client.CurrentStateRequest\x1a\x1c.Client.CurrentStateResponse\x12=\n\x08LoadSong\x12\x17.Client.LoadSongRequest\x1a\x18.Client.LoadSongResponse\x12@\n\tStartSong\x12\x18.Client.StartSongRequest\x1a\x19.Client.StartSongResponse\x12=\n\x08StopSong\x12\x17.Client.StopSongRequest\x1a\x18.Client.StopSongResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'Client.ClientGRPC.Client_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_CURRENTSTATEREQUEST']._serialized_start=42
  _globals['_CURRENTSTATEREQUEST']._serialized_end=63
  _globals['_CURRENTSTATERESPONSE']._serialized_start=65
  _globals['_CURRENTSTATERESPONSE']._serialized_end=105
  _globals['_LOADSONGREQUEST']._serialized_start=107
  _globals['_LOADSONGREQUEST']._serialized_end=163
  _globals['_LOADSONGRESPONSE']._serialized_start=165
  _globals['_LOADSONGRESPONSE']._serialized_end=200
  _globals['_STARTSONGREQUEST']._serialized_start=202
  _globals['_STARTSONGREQUEST']._serialized_end=251
  _globals['_STARTSONGRESPONSE']._serialized_start=253
  _globals['_STARTSONGRESPONSE']._serialized_end=289
  _globals['_STOPSONGREQUEST']._serialized_start=291
  _globals['_STOPSONGREQUEST']._serialized_end=322
  _globals['_STOPSONGRESPONSE']._serialized_start=324
  _globals['_STOPSONGRESPONSE']._serialized_end=359
  _globals['_CLIENT']._serialized_start=362
  _globals['_CLIENT']._serialized_end=637
# @@protoc_insertion_point(module_scope)
