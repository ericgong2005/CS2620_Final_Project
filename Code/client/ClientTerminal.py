from concurrent import futures
import grpc
import sys

from Client.ClientGRPC import Client_pb2, Client_pb2_grpc
from Server.ServerLobbyGRPC import ServerLobby_pb2, ServerLobby_pb2_grpc
from Server.ServerRoomGRPC import (ServerRoomMusic_pb2, ServerRoomMusic_pb2_grpc, 
                            ServerRoomTime_pb2, ServerRoomTime_pb2_grpc)

class ClientServicer(Client_pb2_grpc.ClientServicer):
    def __init__(self):
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

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python ClientTerminal.py ServerHost:Port")
        sys.exit(1)
    server = sys.argv[1]

    Client = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    Client_pb2_grpc.add_ClientServicer_to_server(ClientServicer(), Client)
    ClientAddress = Client.add_insecure_port("localhost:0")
    
    Client.start()
    print(f"Client started on {ClientAddress}")
    
    Client.wait_for_termination()
