# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from Server.ServerRoomGRPC import ServerRoomMusic_pb2 as Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2

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
        + f' but the generated code in Server/ServerRoomGRPC/ServerRoomMusic_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class ServerRoomMusicStub(object):
    """-----------------------------------------------------------------
    Service definition
    -----------------------------------------------------------------
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.KillRoom = channel.unary_unary(
                '/ServerRoomMusic.ServerRoomMusic/KillRoom',
                request_serializer=Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.KillRoomRequest.SerializeToString,
                response_deserializer=Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.KillRoomResponse.FromString,
                _registered_method=True)
        self.JoinRoom = channel.unary_unary(
                '/ServerRoomMusic.ServerRoomMusic/JoinRoom',
                request_serializer=Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.JoinRoomRequest.SerializeToString,
                response_deserializer=Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.JoinRoomResponse.FromString,
                _registered_method=True)
        self.LeaveRoom = channel.unary_unary(
                '/ServerRoomMusic.ServerRoomMusic/LeaveRoom',
                request_serializer=Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.LeaveRoomRequest.SerializeToString,
                response_deserializer=Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.LeaveRoomResponse.FromString,
                _registered_method=True)
        self.SyncStat = channel.unary_unary(
                '/ServerRoomMusic.ServerRoomMusic/SyncStat',
                request_serializer=Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.SyncStatRequest.SerializeToString,
                response_deserializer=Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.SyncStatResponse.FromString,
                _registered_method=True)
        self.CurrentState = channel.unary_unary(
                '/ServerRoomMusic.ServerRoomMusic/CurrentState',
                request_serializer=Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.CurrentStateRequest.SerializeToString,
                response_deserializer=Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.CurrentStateResponse.FromString,
                _registered_method=True)
        self.AddSong = channel.unary_unary(
                '/ServerRoomMusic.ServerRoomMusic/AddSong',
                request_serializer=Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.AddSongRequest.SerializeToString,
                response_deserializer=Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.AddSongResponse.FromString,
                _registered_method=True)
        self.DeleteSong = channel.unary_unary(
                '/ServerRoomMusic.ServerRoomMusic/DeleteSong',
                request_serializer=Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.DeleteSongRequest.SerializeToString,
                response_deserializer=Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.DeleteSongResponse.FromString,
                _registered_method=True)
        self.StartSong = channel.unary_unary(
                '/ServerRoomMusic.ServerRoomMusic/StartSong',
                request_serializer=Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.StartSongRequest.SerializeToString,
                response_deserializer=Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.StartSongResponse.FromString,
                _registered_method=True)
        self.PauseSong = channel.unary_unary(
                '/ServerRoomMusic.ServerRoomMusic/PauseSong',
                request_serializer=Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.PauseSongRequest.SerializeToString,
                response_deserializer=Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.PauseSongResponse.FromString,
                _registered_method=True)


class ServerRoomMusicServicer(object):
    """-----------------------------------------------------------------
    Service definition
    -----------------------------------------------------------------
    """

    def KillRoom(self, request, context):
        """Room lifecycle
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def JoinRoom(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def LeaveRoom(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SyncStat(self, request, context):
        """Clock‑sync & state
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CurrentState(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def AddSong(self, request, context):
        """Song control
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteSong(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def StartSong(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def PauseSong(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ServerRoomMusicServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'KillRoom': grpc.unary_unary_rpc_method_handler(
                    servicer.KillRoom,
                    request_deserializer=Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.KillRoomRequest.FromString,
                    response_serializer=Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.KillRoomResponse.SerializeToString,
            ),
            'JoinRoom': grpc.unary_unary_rpc_method_handler(
                    servicer.JoinRoom,
                    request_deserializer=Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.JoinRoomRequest.FromString,
                    response_serializer=Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.JoinRoomResponse.SerializeToString,
            ),
            'LeaveRoom': grpc.unary_unary_rpc_method_handler(
                    servicer.LeaveRoom,
                    request_deserializer=Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.LeaveRoomRequest.FromString,
                    response_serializer=Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.LeaveRoomResponse.SerializeToString,
            ),
            'SyncStat': grpc.unary_unary_rpc_method_handler(
                    servicer.SyncStat,
                    request_deserializer=Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.SyncStatRequest.FromString,
                    response_serializer=Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.SyncStatResponse.SerializeToString,
            ),
            'CurrentState': grpc.unary_unary_rpc_method_handler(
                    servicer.CurrentState,
                    request_deserializer=Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.CurrentStateRequest.FromString,
                    response_serializer=Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.CurrentStateResponse.SerializeToString,
            ),
            'AddSong': grpc.unary_unary_rpc_method_handler(
                    servicer.AddSong,
                    request_deserializer=Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.AddSongRequest.FromString,
                    response_serializer=Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.AddSongResponse.SerializeToString,
            ),
            'DeleteSong': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteSong,
                    request_deserializer=Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.DeleteSongRequest.FromString,
                    response_serializer=Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.DeleteSongResponse.SerializeToString,
            ),
            'StartSong': grpc.unary_unary_rpc_method_handler(
                    servicer.StartSong,
                    request_deserializer=Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.StartSongRequest.FromString,
                    response_serializer=Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.StartSongResponse.SerializeToString,
            ),
            'PauseSong': grpc.unary_unary_rpc_method_handler(
                    servicer.PauseSong,
                    request_deserializer=Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.PauseSongRequest.FromString,
                    response_serializer=Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.PauseSongResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'ServerRoomMusic.ServerRoomMusic', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('ServerRoomMusic.ServerRoomMusic', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class ServerRoomMusic(object):
    """-----------------------------------------------------------------
    Service definition
    -----------------------------------------------------------------
    """

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
            Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.KillRoomRequest.SerializeToString,
            Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.KillRoomResponse.FromString,
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
    def JoinRoom(request,
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
            '/ServerRoomMusic.ServerRoomMusic/JoinRoom',
            Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.JoinRoomRequest.SerializeToString,
            Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.JoinRoomResponse.FromString,
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
    def LeaveRoom(request,
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
            '/ServerRoomMusic.ServerRoomMusic/LeaveRoom',
            Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.LeaveRoomRequest.SerializeToString,
            Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.LeaveRoomResponse.FromString,
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
    def SyncStat(request,
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
            '/ServerRoomMusic.ServerRoomMusic/SyncStat',
            Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.SyncStatRequest.SerializeToString,
            Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.SyncStatResponse.FromString,
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
            Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.CurrentStateRequest.SerializeToString,
            Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.CurrentStateResponse.FromString,
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
            Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.AddSongRequest.SerializeToString,
            Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.AddSongResponse.FromString,
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
            Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.DeleteSongRequest.SerializeToString,
            Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.DeleteSongResponse.FromString,
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
    def StartSong(request,
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
            '/ServerRoomMusic.ServerRoomMusic/StartSong',
            Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.StartSongRequest.SerializeToString,
            Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.StartSongResponse.FromString,
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
            Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.PauseSongRequest.SerializeToString,
            Server_dot_ServerRoomGRPC_dot_ServerRoomMusic__pb2.PauseSongResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
