from concurrent import futures
import grpc
import time

from Client.ClientGRPC import Client_pb2, Client_pb2_grpc
from Server.ServerLobbyGRPC import ServerLobby_pb2, ServerLobby_pb2_grpc
from Server.ServerRoomGRPC import (ServerRoomMusic_pb2, ServerRoomMusic_pb2_grpc, 
                            ServerRoomTime_pb2, ServerRoomTime_pb2_grpc)

class ServerRoomTimeServicer(ServerRoomTime_pb2_grpc.ServerRoomTimeServicer):
    def TimeSync(self, request, context):
        return ServerRoomTime_pb2.TimeSyncResponse(time=int(time.perf_counter()))

class ServerRoomMusicServicer(ServerRoomMusic_pb2_grpc.ServerRoomMusicServicer):
    def __init__(self, TimeAddress, Name):
        self.Name = Name
        self.TimeAddress = TimeAddress
        self.users = {}  # Holds user to stub mappings

    # Kill Room
    def KillRoom(self, request, context):
        pass

    # Current State
    def CurrentState(self, request, context):
        pass

    # Add Song RPC method
    def AddSong(self, request, context):
        pass

    # Delete Song
    def DeleteSong(self, request, context):
        pass

    # Pause Song
    def PauseSong(self, request, context):
        pass

    # Move Position
    def MovePosition(self, request, context):
        pass

def startServerRoom(LobbyQueue, Name):
    # Start ServerRoomTime gRPC server.
    ServerRoomTime = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    ServerRoomTime_pb2_grpc.add_ServerRoomTimeServicer_to_server(ServerRoomTimeServicer(), ServerRoomTime)
    TimeAddress = ServerRoomTime.add_insecure_port("localhost:0")
    ServerRoomTime.start()
    print(f"ServerRoomTime started on {TimeAddress}")

    # Start ServerRoomMusic gRPC server.
    ServerRoomMusic = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    ServerRoomMusic_pb2_grpc.add_ServerRoomMusicServicer_to_server(ServerRoomMusicServicer(TimeAddress, Name), ServerRoomMusic)
    MusicAddress = ServerRoomMusic.add_insecure_port("localhost:0")
    ServerRoomMusic.start()
    print(f"ServerRoomMusic started on {MusicAddress}")

    if LobbyQueue != None:
        LobbyQueue.put(MusicAddress)

    ServerRoomMusic.wait_for_termination()
    ServerRoomTime.stop(0)

if __name__ == '__main__':
    startServerRoom(None, None)
