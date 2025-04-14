from concurrent import futures
import grpc
import sys
import time

import ServerRoomMusic_pb2
import ServerRoomMusic_pb2_grpc

import ServerRoomTime_pb2
import ServerRoomTime_pb2_grpc

class ServerRoomTimeServicer(ServerRoomTime_pb2_grpc.ServerRoomTimeServicer):
    def TimeSync(self, request, context):
        return ServerRoomTime_pb2.TimeSyncResponse(time=int(time.perf_counter()))

class ServerRoomMusicServicer(ServerRoomMusic_pb2_grpc.ServerRoomMusicServicer):
    def __init__(self):
        self.users = {}  # Example: a dictionary to hold room states

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

def start():
    if len(sys.argv) != 3:
        print("Usage: python server.py MusicHost:Port TimeHost:Port")
        sys.exit(1)

    music_address = sys.argv[1]
    time_address = sys.argv[2]

    # Create and start the ServerRoomTime gRPC server.
    ServerRoomTime = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    ServerRoomTime_pb2_grpc.add_ServerRoomTimeServicer_to_server(ServerRoomTimeServicer(), ServerRoomTime)
    ServerRoomTime.add_insecure_port(time_address)
    ServerRoomTime.start()
    print(f"ServerRoomTime started on {time_address}")

    # Create and start the ServerRoomMusic gRPC server.
    ServerRoomMusic = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    ServerRoomMusic_pb2_grpc.add_ServerRoomMusicServicer_to_server(ServerRoomMusicServicer(), ServerRoomMusic)
    ServerRoomMusic.add_insecure_port(music_address)
    ServerRoomMusic.start()
    print(f"ServerRoomMusic started on {music_address}")

    ServerRoomMusic.wait_for_termination()
    ServerRoomTime.stop(0)

if __name__ == '__main__':
    start()
