from concurrent import futures
import grpc
import sys
import time
import multiprocessing as mp

from Client.ClientGRPC import Client_pb2, Client_pb2_grpc
from Server.ServerLobbyGRPC import ServerLobby_pb2, ServerLobby_pb2_grpc
from Server.ServerRoomGRPC import (ServerRoomMusic_pb2, ServerRoomMusic_pb2_grpc, 
                            ServerRoomTime_pb2, ServerRoomTime_pb2_grpc)

class ClientServicer(Client_pb2_grpc.ClientServicer):
    def __init__(self, ClientQueue):
        self.ClientQueue = ClientQueue

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

def ClientTerminalRoom(RoomStub, ClientQueue, username):
    while True:
        command = input(f"Room: Enter a command as {username}: ")
        if command == "exit":
            print("Exiting Room")
            return
        lines = command.split()
        if not lines:
            continue

        if lines[0] == "Sync":
            print("Begin Sync")

        else:
            print("Unknown Command")
    
    
def ClientTerminalStart(LobbyStub, ClientQueue):
    try:
        # Set a username
        username = None
        while username == None:
            username = input("Username: ")
            response = LobbyStub.JoinLobby(ServerLobby_pb2.JoinLobbyRequest(username=username))
            if response.status == ServerLobby_pb2.Status.MATCH:
                print("Username Taken")
                username = None

        # Handle commands
        while True:
            command = input(f"Lobby: Enter a command as {username}: ")
            if command == "exit":
                break
            lines = command.split()
            if not lines:
                continue

            if lines[0] == "Start":
                if len(lines) < 2:
                    print("Usage: Start <Name>")
                response = LobbyStub.StartRoom(ServerLobby_pb2.StartRoomRequest(name=lines[1]))
                if response.status == ServerLobby_pb2.Status.MATCH:
                    print(f"Name Taken.\nCurrent Rooms:\n{response.rooms}")
                elif response.status == ServerLobby_pb2.Status.ERROR:
                    print(f"Room Failed to Start.\nCurrent Rooms:\n{response.rooms}")
                else:
                    print(f"Room Made.\nCurrent Rooms:\n{response.rooms}")

            elif lines[0] == "Join":
                response = LobbyStub.GetRooms(ServerLobby_pb2.GetRoomsRequest())
                print("Rooms:\n", response.rooms)
                room = "Room: " + input("Choose a room: ")
                roomlist = list(response.rooms)
                if room not in roomlist:
                    print("Invalid Room")
                    continue
                RoomAddress = response.addresses[roomlist.index(room)]
                try:
                    channel = grpc.insecure_channel(RoomAddress)
                    RoomStub = ServerLobby_pb2_grpc.ServerLobbyStub(channel)
                    grpc.channel_ready_future(channel).result(timeout=1)
                    print(f"Client connected to {room} at {RoomAddress}")
                    LobbyStub.JoinRoom(ServerLobby_pb2.JoinRoomRequest(username=username, roomname=room))
                    ClientTerminalRoom(RoomStub, ClientQueue, username)
                except grpc.FutureTimeoutError:
                    print("Failed to Connect")
                LobbyStub.LeaveRoom(ServerLobby_pb2.LeaveRoomRequest(username=username))

            else:
                print("Unknown Command")

    except KeyboardInterrupt:
        return

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python ClientTerminal.py ServerHost:Port")
        sys.exit(1)
    ServerAddress = sys.argv[1]

    # Connect to ServerLobby
    LobbyStub = None
    while True:
        try:
            channel = grpc.insecure_channel(ServerAddress)
            LobbyStub = ServerLobby_pb2_grpc.ServerLobbyStub(channel)
            grpc.channel_ready_future(channel).result(timeout=1)
            print(f"Client connected to Lobby at {ServerAddress}")
            break
        except grpc.FutureTimeoutError:
            time.sleep(0.5)
            print("Waiting to connect to Lobby")

    ClientQueue = mp.Queue()

    Client = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    Client_pb2_grpc.add_ClientServicer_to_server(ClientServicer(ClientQueue), Client)
    ClientAddress = Client.add_insecure_port("localhost:0")
    
    Client.start()
    print(f"Client started on {ClientAddress}")

    ClientTerminalStart(LobbyStub, ClientQueue)
        
    Client.stop(0)
