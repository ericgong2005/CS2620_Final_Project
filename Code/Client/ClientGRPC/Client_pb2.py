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




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1e\x43lient/ClientGRPC/Client.proto\x12\x06\x43lient\"Q\n\x13RegisterRoomRequest\x12\x13\n\x0bRoomAddress\x18\x01 \x01(\t\x12\x13\n\x0bTimeAddress\x18\x02 \x01(\t\x12\x10\n\x08username\x18\x03 \x01(\t\"\'\n\x14RegisterRoomResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\"1\n\x0e\x41\x64\x64SongRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x11\n\tAudioData\x18\x02 \x01(\x0c\"\x11\n\x0f\x41\x64\x64SongResponse\"@\n\x10StartSongRequest\x12\x0c\n\x04time\x18\x01 \x01(\x01\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x10\n\x08position\x18\x03 \x01(\x01\"$\n\x11StartSongResponse\x12\x0f\n\x07Missing\x18\x01 \x01(\x08\"\x1f\n\x0fStopSongRequest\x12\x0c\n\x04time\x18\x01 \x01(\x01\"#\n\x10StopSongResponse\x12\x0f\n\x07Missing\x18\x01 \x01(\x08\"\x0e\n\x0cLeaveRequest\"\x0f\n\rLeaveResponse\"\x12\n\x10HeartbeatRequest\"\x13\n\x11HeartbeatResponse2\x88\x03\n\x06\x43lient\x12I\n\x0cRegisterRoom\x12\x1b.Client.RegisterRoomRequest\x1a\x1c.Client.RegisterRoomResponse\x12:\n\x07\x41\x64\x64Song\x12\x16.Client.AddSongRequest\x1a\x17.Client.AddSongResponse\x12@\n\tStartSong\x12\x18.Client.StartSongRequest\x1a\x19.Client.StartSongResponse\x12=\n\x08StopSong\x12\x17.Client.StopSongRequest\x1a\x18.Client.StopSongResponse\x12\x34\n\x05Leave\x12\x14.Client.LeaveRequest\x1a\x15.Client.LeaveResponse\x12@\n\tHeartbeat\x12\x18.Client.HeartbeatRequest\x1a\x19.Client.HeartbeatResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'Client.ClientGRPC.Client_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_REGISTERROOMREQUEST']._serialized_start=42
  _globals['_REGISTERROOMREQUEST']._serialized_end=123
  _globals['_REGISTERROOMRESPONSE']._serialized_start=125
  _globals['_REGISTERROOMRESPONSE']._serialized_end=164
  _globals['_ADDSONGREQUEST']._serialized_start=166
  _globals['_ADDSONGREQUEST']._serialized_end=215
  _globals['_ADDSONGRESPONSE']._serialized_start=217
  _globals['_ADDSONGRESPONSE']._serialized_end=234
  _globals['_STARTSONGREQUEST']._serialized_start=236
  _globals['_STARTSONGREQUEST']._serialized_end=300
  _globals['_STARTSONGRESPONSE']._serialized_start=302
  _globals['_STARTSONGRESPONSE']._serialized_end=338
  _globals['_STOPSONGREQUEST']._serialized_start=340
  _globals['_STOPSONGREQUEST']._serialized_end=371
  _globals['_STOPSONGRESPONSE']._serialized_start=373
  _globals['_STOPSONGRESPONSE']._serialized_end=408
  _globals['_LEAVEREQUEST']._serialized_start=410
  _globals['_LEAVEREQUEST']._serialized_end=424
  _globals['_LEAVERESPONSE']._serialized_start=426
  _globals['_LEAVERESPONSE']._serialized_end=441
  _globals['_HEARTBEATREQUEST']._serialized_start=443
  _globals['_HEARTBEATREQUEST']._serialized_end=461
  _globals['_HEARTBEATRESPONSE']._serialized_start=463
  _globals['_HEARTBEATRESPONSE']._serialized_end=482
  _globals['_CLIENT']._serialized_start=485
  _globals['_CLIENT']._serialized_end=877
# @@protoc_insertion_point(module_scope)
