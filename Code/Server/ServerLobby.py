from concurrent import futures
import grpc
import sys
import time
import socket
import multiprocessing as mp

from Client.ClientGRPC import Client_pb2, Client_pb2_grpc
from Server.ServerLobbyGRPC import ServerLobby_pb2, ServerLobby_pb2_grpc
from Server.ServerRoomGRPC import (ServerRoomMusic_pb2, ServerRoomMusic_pb2_grpc, 
                            ServerRoomTime_pb2, ServerRoomTime_pb2_grpc)

from Server.ServerRoom import startServerRoom

from Server.ServerConstants import MAX_GRPC_OPTION

class ServerLobbyServicer(ServerLobby_pb2_grpc.ServerLobbyServicer):
    def __init__(self):
        self.users = {} # Contains username to (room, last update time, stub)
        self.rooms = {} # Contains room name to (address, count, last update time, stub)

    def GetRoomValue(self, index):
        return [item[index] for item in self.rooms.values()]
    
    def CheckUsers(self):
        print("Checking Users", list(self.users.keys()))
        for key in list(self.users.keys()):
            print(f"User {key} Heartbeat")
            try:
                self.users[key][2].Heartbeat(Client_pb2.HeartbeatRequest())
                self.users[key] = (self.users[key][0], int(time.time()), self.users[key][2])
            except grpc.RpcError:
                del self.users[key]
    
    def CheckRooms(self):
        for key in list(self.rooms.keys()):
            print(f"Getting Status of {key}")
            try:
                response = self.rooms[key][3].CurrentState(ServerRoomMusic_pb2.CurrentStateRequest())
                if len(response.usernames) > 0:
                    self.rooms[key] = (self.rooms[key][0],
                                        self.rooms[key][1],
                                        int(time.time()),
                                        self.rooms[key][3])
                    print(f"{key} is confirmed active with users", response.usernames)
                    continue
                self.rooms[key][3].KillRoom(ServerRoomMusic_pb2.KillRoomRequest())
                print(f"Killed {key}")
            except grpc.RpcError:
                del self.rooms[key]

    # Join the lobby
    def JoinLobby(self, request, context):
        print(f"JoinLobby Request with username {request.username}")
        self.CheckUsers()

        if request.username in self.users:
            print("Duplicate User Rejected:", request.username)
            return ServerLobby_pb2.JoinLobbyResponse(status=ServerLobby_pb2.Status.MATCH)
        
        UserStub = None
        try:
            channel = grpc.insecure_channel(request.MusicPlayerAddress, options = MAX_GRPC_OPTION)
            UserStub = Client_pb2_grpc.ClientStub(channel)
            grpc.channel_ready_future(channel).result(timeout=1)
            print(f"Lobby connected to User {request.username} at {request.MusicPlayerAddress}")
        except Exception as e:
            print(f"Failed to connect to {request.username}: {e}")
            return ServerLobby_pb2.JoinLobbyResponse(status=ServerLobby_pb2.Status.ERROR)
        
        self.users[request.username] = ("Lobby", int(time.time()), UserStub)
        print("User added:", request.username)
        return ServerLobby_pb2.JoinLobbyResponse(status=ServerLobby_pb2.Status.SUCCESS)
    
    # Leave the lobby
    def LeaveLobby(self, request, context):
        print(f"LeaveLobby Request with username {request.username}")
        if request.username in self.users:
            del self.users[request.username]
        return ServerLobby_pb2.JoinLobbyResponse(status=ServerLobby_pb2.Status.SUCCESS)

    # Get the currently active rooms
    def GetRooms(self, request, context):
        self.CheckRooms()
        return ServerLobby_pb2.GetRoomsResponse(rooms=list(self.rooms.keys()), 
                                                addresses=self.GetRoomValue(0))

    # Try to join a room
    def JoinRoom(self, request, context):
        print("Join Room Request on", request.roomname, "given", self.GetRoomValue(0))
        self.CheckRooms()
        
        if request.roomname not in self.rooms:
            return ServerLobby_pb2.JoinRoomResponse(status=ServerLobby_pb2.Status.ERROR)
        self.users[request.username] = (request.roomname, int(time.time()), self.users[request.username][2])
        self.rooms[request.roomname] = (self.rooms[request.roomname][0], 
                                        self.rooms[request.roomname][1] + 1,
                                        int(time.time()),
                                        self.rooms[request.roomname][3])
        return ServerLobby_pb2.JoinRoomResponse(status=ServerLobby_pb2.Status.SUCCESS)

    # Inform you left a room
    def LeaveRoom(self, request, context):
        self.users[request.username] = ("Lobby", int(time.time()), self.users[request.username][2])
        if request.roomname in self.rooms:
            self.rooms[request.roomname] = (self.rooms[request.roomname][0], 
                                        (self.rooms[request.roomname][1] - 1 if self.rooms[request.roomname][1] - 1 > 0 else 0),
                                        int(time.time()),
                                        self.rooms[request.roomname][3])
        return ServerLobby_pb2.LeaveRoomResponse(status=ServerLobby_pb2.Status.SUCCESS)

    # Try to start a room
    def StartRoom(self, request, context):
        self.CheckRooms()

        print(f"StartRoom Request with name {request.name}")
        name = "Room: " + request.name
        if name in self.rooms:
            return ServerLobby_pb2.StartRoomResponse(status=ServerLobby_pb2.Status.MATCH, 
                                                     rooms=list(self.rooms.keys()), 
                                                     addresses=self.GetRoomValue(0))
        LobbyQueue = mp.Queue()
        ServerRoom = mp.Process(target=startServerRoom, args=(LobbyQueue, name))
        ServerRoom.start()
        
        RoomMusicAddress = LobbyQueue.get()
        print(name, " Started with address ", RoomMusicAddress)

        # Connect to ServerRoom
        RoomStub = None
        try:
            channel = grpc.insecure_channel(RoomMusicAddress, options = MAX_GRPC_OPTION)
            RoomStub = ServerRoomMusic_pb2_grpc.ServerRoomMusicStub(channel)
            grpc.channel_ready_future(channel).result(timeout=1)
            print(f"Lobby connected to {name} at {RoomMusicAddress}")
        except Exception as e:
            print(f"Failed to connect to Room: {e}")
            return ServerLobby_pb2.StartRoomResponse(status=ServerLobby_pb2.Status.ERROR, 
                                                     rooms=list(self.rooms.keys()), 
                                                     addresses=self.GetRoomValue(0))

        self.rooms[name] = (RoomMusicAddress, 0, int(time.time()), RoomStub)

        print("Current Rooms:", list(self.rooms.keys()), "\n", self.GetRoomValue(0))

        return ServerLobby_pb2.StartRoomResponse(status=ServerLobby_pb2.Status.SUCCESS, 
                                                     rooms=list(self.rooms.keys()), 
                                                     addresses=self.GetRoomValue(0))

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python ServerLobby.py Port")
        sys.exit(1)
    port = sys.argv[1]

    hostname = socket.gethostbyname(socket.gethostname())

    address = hostname + ":" + port

    mp.set_start_method('spawn')

    ServerLobby = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    ServerLobby_pb2_grpc.add_ServerLobbyServicer_to_server(ServerLobbyServicer(), ServerLobby)
    ServerLobby.add_insecure_port(address)
    
    ServerLobby.start()
    print(f"ServerLobby started on {address}")
    
    ServerLobby.wait_for_termination()
