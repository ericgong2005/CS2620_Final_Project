from concurrent import futures
import grpc
import sys
import time
import multiprocessing as mp
import socket
import numpy as np

from Client.ClientGRPC import Client_pb2, Client_pb2_grpc
from Server.ServerLobbyGRPC import ServerLobby_pb2, ServerLobby_pb2_grpc
from Server.ServerRoomGRPC import (ServerRoomMusic_pb2, ServerRoomMusic_pb2_grpc, 
                            ServerRoomTime_pb2, ServerRoomTime_pb2_grpc)

from Server.ServerConstants import WAIT, MAX_OFFSET_VARIANCE, MAX_REPEATS, COUNTS

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
'''
Repeats < 0 will repeat the sync until the variance in the computed clock offset
is less than MAX_OFFSET_VARIANCE, or for the specified number of repeats
'''
def TimeSync(TimeStub, offset, delay, repeats = -1):
    while True:
        Start = time.clock_gettime(time.CLOCK_REALTIME)
        response = TimeStub.TimeSync(ServerRoomTime_pb2.TimeSyncRequest())
        End = time.clock_gettime(time.CLOCK_REALTIME)
        CurDelay = (End - Start)/2
        CurOffset = Start + CurDelay - response.time
        # print("TimeSync Stats:\n\tStarted:", round(Start%100,3), 
        #       "\n\tEnded:", round(End%100,3),
        #       "\n\tPredicted Delay:", CurDelay,
        #       "\n\tPredicted Offset:", CurOffset,
        #       "\n\tPrevious Offset Variance:", (np.var(offset) if len(offset > 1) else "Too Few Measurements"))
        delay = np.append(delay, CurDelay)
        offset = np.append(offset, CurOffset)
        if len(delay) > COUNTS:
            delay = delay[1:]
            offset = offset[1:]
        if (len(delay) == COUNTS and 
            (repeats == 0 or 
            np.var(offset) < MAX_OFFSET_VARIANCE or 
            repeats + MAX_REPEATS < 0)):
            return (offset, delay)
        time.sleep(WAIT)
        repeats = repeats - 1

def ClientTerminalRoom(RoomStub, ClientQueue, ClientAddress, username):
    # Connect to Room
    response = RoomStub.JoinRoom(ServerRoomMusic_pb2.JoinRoomRequest(username=username, 
                                                                     ClientAddress=ClientAddress))
    if response.status == ServerRoomMusic_pb2.Status.ERROR:
        print("Error Connecting to Room")
        return
    
    TimeStub = None
    try:
        channel = grpc.insecure_channel(response.RoomTimeAddress)
        TimeStub = ServerRoomTime_pb2_grpc.ServerRoomTimeStub(channel)
        grpc.channel_ready_future(channel).result(timeout=1)
        print(f"Client connected to Time Provider at {response.RoomTimeAddress}")
    except grpc.FutureTimeoutError:
        print("Failed to Connect to Time Provider") 
        RoomStub.LeaveRoom(ServerRoomMusic_pb2.LeaveRoomRequest(username=username))
        return
    
    print("Begin Time Sync")
    offset = np.array([])
    delay = np.array([])
    offset, delay = TimeSync(TimeStub, offset, delay)
    print("TimeSync Results:\n\tOffset (ms): ", round(np.mean(offset)*1000,5), 
          "\n\tDelay (ms):", round(np.mean(delay)*1000, 5), 
          "\n\tOffset Variance (ns):", round(np.var(offset)*10**6,5),
          "\n\tDelay Variance (ns):", round(np.var(delay)*10**6,5))

    while True:
        command = input(f"Room: Enter a command as {username}: ")
        if command == "exit":
            print("Exiting Room")
            RoomStub.LeaveRoom(ServerRoomMusic_pb2.LeaveRoomRequest(username=username))
            return
        lines = command.split()
        if not lines:
            continue

        if lines[0] == "Sync":
            print("Begin Time Sync")
            offset, delay = offset, delay = TimeSync(TimeStub, offset, delay, 5)
            print("TimeSync Results:\n\tOffset (ms): ", round(np.mean(offset)*1000,5), 
                    "\n\tDelay (ms):", round(np.mean(delay)*1000, 5), 
                    "\n\tOffset Variance (ns):", round(np.var(offset)*10**6,5),
                    "\n\tDelay Variance (ns):", round(np.var(delay)*10**6,5))

        else:
            print("Unknown Command")
    

def ClientTerminalStart(LobbyStub, ClientQueue, ClientAddress):
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
                # Implement LeaveLobby
                break
            lines = command.split()
            if not lines:
                continue

            if lines[0] == "Start":
                if len(lines) < 2:
                    print("Usage: Start <Name>")
                    continue
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
                    RoomStub = ServerRoomMusic_pb2_grpc.ServerRoomMusicStub(channel)
                    grpc.channel_ready_future(channel).result(timeout=1)
                    print(f"Client connected to {room} at {RoomAddress}")
                    LobbyStub.JoinRoom(ServerLobby_pb2.JoinRoomRequest(username=username, roomname=room))
                    ClientTerminalRoom(RoomStub, ClientQueue, ClientAddress, username)
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

    # Get hostname
    hostname = socket.gethostbyname(socket.gethostname())

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
    ClientAddress =  hostname + ":" + str(Client.add_insecure_port(f"{hostname}:0"))
    
    Client.start()
    print(f"Client started on {ClientAddress}")

    ClientTerminalStart(LobbyStub, ClientQueue, ClientAddress)
        
    Client.stop(0)
