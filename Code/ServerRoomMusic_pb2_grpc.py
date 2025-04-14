# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

import ServerRoomMusic_pb2 as ServerRoomMusic__pb2

GRPC_GENERATED_VERSION = '1.70.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in ServerRoomMusic_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class ServerRoomMusicStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.KillRoom = channel.unary_unary(
                '/ServerRoomMusic.ServerRoomMusic/KillRoom',
                request_serializer=ServerRoomMusic__pb2.KillRoomRequest.SerializeToString,
                response_deserializer=ServerRoomMusic__pb2.KillRoomResponse.FromString,
                _registered_method=True)
        self.CurrentState = channel.unary_unary(
                '/ServerRoomMusic.ServerRoomMusic/CurrentState',
                request_serializer=ServerRoomMusic__pb2.CurrentStateRequest.SerializeToString,
                response_deserializer=ServerRoomMusic__pb2.CurrentStateResponse.FromString,
                _registered_method=True)
        self.AddSong = channel.unary_unary(
                '/ServerRoomMusic.ServerRoomMusic/AddSong',
                request_serializer=ServerRoomMusic__pb2.AddSongRequest.SerializeToString,
                response_deserializer=ServerRoomMusic__pb2.AddSongResponse.FromString,
                _registered_method=True)
        self.DeleteSong = channel.unary_unary(
                '/ServerRoomMusic.ServerRoomMusic/DeleteSong',
                request_serializer=ServerRoomMusic__pb2.DeleteSongRequest.SerializeToString,
                response_deserializer=ServerRoomMusic__pb2.DeleteSongResponse.FromString,
                _registered_method=True)
        self.PauseSong = channel.unary_unary(
                '/ServerRoomMusic.ServerRoomMusic/PauseSong',
                request_serializer=ServerRoomMusic__pb2.PauseSongRequest.SerializeToString,
                response_deserializer=ServerRoomMusic__pb2.PauseSongResponse.FromString,
                _registered_method=True)
        self.MovePosition = channel.unary_unary(
                '/ServerRoomMusic.ServerRoomMusic/MovePosition',
                request_serializer=ServerRoomMusic__pb2.MovePositionRequest.SerializeToString,
                response_deserializer=ServerRoomMusic__pb2.MovePositionResponse.FromString,
                _registered_method=True)


class ServerRoomMusicServicer(object):
    """Missing associated documentation comment in .proto file."""

    def KillRoom(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CurrentState(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def AddSong(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteSong(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def PauseSong(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def MovePosition(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ServerRoomMusicServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'KillRoom': grpc.unary_unary_rpc_method_handler(
                    servicer.KillRoom,
                    request_deserializer=ServerRoomMusic__pb2.KillRoomRequest.FromString,
                    response_serializer=ServerRoomMusic__pb2.KillRoomResponse.SerializeToString,
            ),
            'CurrentState': grpc.unary_unary_rpc_method_handler(
                    servicer.CurrentState,
                    request_deserializer=ServerRoomMusic__pb2.CurrentStateRequest.FromString,
                    response_serializer=ServerRoomMusic__pb2.CurrentStateResponse.SerializeToString,
            ),
            'AddSong': grpc.unary_unary_rpc_method_handler(
                    servicer.AddSong,
                    request_deserializer=ServerRoomMusic__pb2.AddSongRequest.FromString,
                    response_serializer=ServerRoomMusic__pb2.AddSongResponse.SerializeToString,
            ),
            'DeleteSong': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteSong,
                    request_deserializer=ServerRoomMusic__pb2.DeleteSongRequest.FromString,
                    response_serializer=ServerRoomMusic__pb2.DeleteSongResponse.SerializeToString,
            ),
            'PauseSong': grpc.unary_unary_rpc_method_handler(
                    servicer.PauseSong,
                    request_deserializer=ServerRoomMusic__pb2.PauseSongRequest.FromString,
                    response_serializer=ServerRoomMusic__pb2.PauseSongResponse.SerializeToString,
            ),
            'MovePosition': grpc.unary_unary_rpc_method_handler(
                    servicer.MovePosition,
                    request_deserializer=ServerRoomMusic__pb2.MovePositionRequest.FromString,
                    response_serializer=ServerRoomMusic__pb2.MovePositionResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'ServerRoomMusic.ServerRoomMusic', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('ServerRoomMusic.ServerRoomMusic', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class ServerRoomMusic(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def KillRoom(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/ServerRoomMusic.ServerRoomMusic/KillRoom',
            ServerRoomMusic__pb2.KillRoomRequest.SerializeToString,
            ServerRoomMusic__pb2.KillRoomResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def CurrentState(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/ServerRoomMusic.ServerRoomMusic/CurrentState',
            ServerRoomMusic__pb2.CurrentStateRequest.SerializeToString,
            ServerRoomMusic__pb2.CurrentStateResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def AddSong(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/ServerRoomMusic.ServerRoomMusic/AddSong',
            ServerRoomMusic__pb2.AddSongRequest.SerializeToString,
            ServerRoomMusic__pb2.AddSongResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def DeleteSong(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/ServerRoomMusic.ServerRoomMusic/DeleteSong',
            ServerRoomMusic__pb2.DeleteSongRequest.SerializeToString,
            ServerRoomMusic__pb2.DeleteSongResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def PauseSong(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/ServerRoomMusic.ServerRoomMusic/PauseSong',
            ServerRoomMusic__pb2.PauseSongRequest.SerializeToString,
            ServerRoomMusic__pb2.PauseSongResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def MovePosition(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/ServerRoomMusic.ServerRoomMusic/MovePosition',
            ServerRoomMusic__pb2.MovePositionRequest.SerializeToString,
            ServerRoomMusic__pb2.MovePositionResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
