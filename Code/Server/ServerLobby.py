from concurrent import futures
import grpc
import sys
import time
import multiprocessing as mp

from Client.ClientGRPC import Client_pb2, Client_pb2_grpc
from Server.ServerLobbyGRPC import ServerLobby_pb2, ServerLobby_pb2_grpc
from Server.ServerRoomGRPC import (ServerRoomMusic_pb2, ServerRoomMusic_pb2_grpc, 
                            ServerRoomTime_pb2, ServerRoomTime_pb2_grpc)

from Server.ServerRoom import startServerRoom

class ServerLobbyServicer(ServerLobby_pb2_grpc.ServerLobbyServicer):
    def __init__(self):
        self.users = {} # Contains username to (room, last update time)
        self.rooms = {} # Contains room name to (address, count, last update time)

    def GetRoomAddresses(self):
        return [item[0] for item in self.rooms.values()]
    
    def CheckRooms(self):
        for 

    # Join the lobby
    def JoinLobby(self, request, context):
        print(f"JoinLobby Request with username {request.username}")
        if request.username in self.users:
            return ServerLobby_pb2.JoinLobbyResponse(status=ServerLobby_pb2.Status.MATCH)
        self.users[request.username] = ("Lobby", int(time.time()))
        return ServerLobby_pb2.JoinLobbyResponse(status=ServerLobby_pb2.Status.SUCCESS)

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
        print(f"StartRoom Request with name {request.name}")
        name = "Room: " + request.name
        if name in self.rooms:
            return ServerLobby_pb2.StartRoomResponse(status=ServerLobby_pb2.Status.MATCH, 
                                                     rooms=list(self.rooms.keys()), 
                                                     addresses=self.GetRoomAddresses())
        LobbyQueue = mp.Queue()
        ServerRoom = mp.Process(target=startServerRoom, args=(LobbyQueue, name))
        ServerRoom.start()
        
        RoomMusicAddress = LobbyQueue.get()
        print(name, " Started with address ", RoomMusicAddress)

        self.rooms[name] = (RoomMusicAddress, 0, int(time.time()))
        print("Current Rooms:", self.rooms)

        return ServerLobby_pb2.StartRoomResponse(status=ServerLobby_pb2.Status.SUCCESS, 
                                                     rooms=list(self.rooms.keys()), 
                                                     addresses=self.GetRoomAddresses())

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python ServerLobby.py Host:Port")
        sys.exit(1)
    address = sys.argv[1]

    mp.set_start_method('spawn')

    ServerLobby = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    ServerLobby_pb2_grpc.add_ServerLobbyServicer_to_server(ServerLobbyServicer(), ServerLobby)
    ServerLobby.add_insecure_port(address)
    
    ServerLobby.start()
    print(f"ServerLobby started on {address}")
    
    ServerLobby.wait_for_termination()
