from concurrent import futures
import grpc
import sys

import ServerLobby_pb2_grpc

class ServerLobbyServicer(ServerLobby_pb2_grpc.ServerLobbyServicer):
    def __init__(self):
        users = {} # Contains username to (room, last update time)
        rooms = {} # Contains room to (count, last update time)

    # Join the lobby
    def JoinLobby(self, request, context):
        pass

    # Get the currently active rooms
    def GetRooms(self, request, context):
        pass

    # Try to join a room
    def JoinRoom(self, request, context):
        pass

    # Inform you left a room
    def LeaveRoom(self, request, context):
        pass

    # Try to start a room
    def StartRoom(self, request, context):
        pass

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python server.py Host:Port")
        sys.exit(1)
    address = sys.argv[1]

    ServerLobby = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    ServerLobby_pb2_grpc.add_ServerLobbyServicer_to_server(ServerLobbyServicer(), ServerLobby)
    ServerLobby.add_insecure_port(address)
    
    ServerLobby.start()
    print(f"ServerLobby started on {address}")
    
    ServerLobby.wait_for_termination()
