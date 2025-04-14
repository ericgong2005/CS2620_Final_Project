# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

import ServerLobby_pb2 as ServerLobby__pb2

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
        + f' but the generated code in ServerLobby_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class ServerLobbyStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.JoinLobby = channel.unary_unary(
                '/ServerLobby.ServerLobby/JoinLobby',
                request_serializer=ServerLobby__pb2.JoinLobbyRequest.SerializeToString,
                response_deserializer=ServerLobby__pb2.JoinLobbyResponse.FromString,
                _registered_method=True)
        self.GetRooms = channel.unary_unary(
                '/ServerLobby.ServerLobby/GetRooms',
                request_serializer=ServerLobby__pb2.GetRoomsRequest.SerializeToString,
                response_deserializer=ServerLobby__pb2.GetRoomsResponse.FromString,
                _registered_method=True)
        self.JoinRoom = channel.unary_unary(
                '/ServerLobby.ServerLobby/JoinRoom',
                request_serializer=ServerLobby__pb2.JoinRoomRequest.SerializeToString,
                response_deserializer=ServerLobby__pb2.JoinRoomResponse.FromString,
                _registered_method=True)
        self.LeaveRoom = channel.unary_unary(
                '/ServerLobby.ServerLobby/LeaveRoom',
                request_serializer=ServerLobby__pb2.LeaveRoomRequest.SerializeToString,
                response_deserializer=ServerLobby__pb2.LeaveRoomResponse.FromString,
                _registered_method=True)
        self.StartRoom = channel.unary_unary(
                '/ServerLobby.ServerLobby/StartRoom',
                request_serializer=ServerLobby__pb2.StartRoomRequest.SerializeToString,
                response_deserializer=ServerLobby__pb2.StartRoomResponse.FromString,
                _registered_method=True)


class ServerLobbyServicer(object):
    """Missing associated documentation comment in .proto file."""

    def JoinLobby(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetRooms(self, request, context):
        """Missing associated documentation comment in .proto file."""
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

    def StartRoom(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ServerLobbyServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'JoinLobby': grpc.unary_unary_rpc_method_handler(
                    servicer.JoinLobby,
                    request_deserializer=ServerLobby__pb2.JoinLobbyRequest.FromString,
                    response_serializer=ServerLobby__pb2.JoinLobbyResponse.SerializeToString,
            ),
            'GetRooms': grpc.unary_unary_rpc_method_handler(
                    servicer.GetRooms,
                    request_deserializer=ServerLobby__pb2.GetRoomsRequest.FromString,
                    response_serializer=ServerLobby__pb2.GetRoomsResponse.SerializeToString,
            ),
            'JoinRoom': grpc.unary_unary_rpc_method_handler(
                    servicer.JoinRoom,
                    request_deserializer=ServerLobby__pb2.JoinRoomRequest.FromString,
                    response_serializer=ServerLobby__pb2.JoinRoomResponse.SerializeToString,
            ),
            'LeaveRoom': grpc.unary_unary_rpc_method_handler(
                    servicer.LeaveRoom,
                    request_deserializer=ServerLobby__pb2.LeaveRoomRequest.FromString,
                    response_serializer=ServerLobby__pb2.LeaveRoomResponse.SerializeToString,
            ),
            'StartRoom': grpc.unary_unary_rpc_method_handler(
                    servicer.StartRoom,
                    request_deserializer=ServerLobby__pb2.StartRoomRequest.FromString,
                    response_serializer=ServerLobby__pb2.StartRoomResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'ServerLobby.ServerLobby', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('ServerLobby.ServerLobby', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class ServerLobby(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def JoinLobby(request,
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
            '/ServerLobby.ServerLobby/JoinLobby',
            ServerLobby__pb2.JoinLobbyRequest.SerializeToString,
            ServerLobby__pb2.JoinLobbyResponse.FromString,
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
    def GetRooms(request,
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
            '/ServerLobby.ServerLobby/GetRooms',
            ServerLobby__pb2.GetRoomsRequest.SerializeToString,
            ServerLobby__pb2.GetRoomsResponse.FromString,
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
            '/ServerLobby.ServerLobby/JoinRoom',
            ServerLobby__pb2.JoinRoomRequest.SerializeToString,
            ServerLobby__pb2.JoinRoomResponse.FromString,
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
            '/ServerLobby.ServerLobby/LeaveRoom',
            ServerLobby__pb2.LeaveRoomRequest.SerializeToString,
            ServerLobby__pb2.LeaveRoomResponse.FromString,
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
    def StartRoom(request,
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
            '/ServerLobby.ServerLobby/StartRoom',
            ServerLobby__pb2.StartRoomRequest.SerializeToString,
            ServerLobby__pb2.StartRoomResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
