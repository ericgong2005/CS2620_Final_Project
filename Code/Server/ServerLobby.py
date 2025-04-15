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

from Server.ServerConstants import ROOM_TIMEOUT

class ServerLobbyServicer(ServerLobby_pb2_grpc.ServerLobbyServicer):
    def __init__(self):
        self.users = {} # Contains username to (room, last update time)
        self.rooms = {} # Contains room name to (address, count, last update time, stub)

    def GetRoomValue(self, index):
        return [item[index] for item in self.rooms.values()]
    
    def CheckRooms(self):
        CurrentTime = int(time.time())
        for key in list(self.rooms.keys()):
            if CurrentTime - self.rooms[key][2] > ROOM_TIMEOUT:
                print(f"{key} has timed out. Removing...")
                try:
                    self.rooms[key][3].KillRoom(ServerRoomMusic_pb2.KillRoomRequest())
                except grpc._channel._InactiveRpcError:
                    pass
                del self.rooms[key]

    # Join the lobby
    def JoinLobby(self, request, context):
        print(f"JoinLobby Request with username {request.username}")
        if request.username in self.users:
            return ServerLobby_pb2.JoinLobbyResponse(status=ServerLobby_pb2.Status.MATCH)
        self.users[request.username] = ("Lobby", int(time.time()))
        return ServerLobby_pb2.JoinLobbyResponse(status=ServerLobby_pb2.Status.SUCCESS)

    # Get the currently active rooms
    def GetRooms(self, request, context):
        return ServerLobby_pb2.GetRoomsResponse(rooms=list(self.rooms.keys()), 
                                                addresses=self.GetRoomValue(0))

    # Try to join a room
    def JoinRoom(self, request, context):
        self.CheckRooms()
        
        if request.roomname not in self.rooms:
            return ServerLobby_pb2.JoinRoomResponse(status=ServerLobby_pb2.Status.ERROR)
        self.users[request.username] = (request.roomname, int(time.time()))
        self.rooms[request.roomname] = (self.rooms[request.roomname][0], 
                                        self.rooms[request.roomname][1] + 1,
                                        int(time.time()),
                                        self.rooms[request.roomname][3])
        return ServerLobby_pb2.JoinRoomResponse(status=ServerLobby_pb2.Status.SUCCESS)

    # Inform you left a room
    def LeaveRoom(self, request, context):
        self.users[request.username] = ("Lobby", int(time.time()))
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
            channel = grpc.insecure_channel(RoomMusicAddress)
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
