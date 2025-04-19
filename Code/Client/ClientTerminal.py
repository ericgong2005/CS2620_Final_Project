from concurrent import futures
import grpc
import sys
import os
import time
import multiprocessing as mp
import threading
import socket
import numpy as np

import vlc

from Client.ClientGRPC import Client_pb2, Client_pb2_grpc
from Server.ServerLobbyGRPC import ServerLobby_pb2, ServerLobby_pb2_grpc
from Server.ServerRoomGRPC import (ServerRoomMusic_pb2, ServerRoomMusic_pb2_grpc, 
                            ServerRoomTime_pb2, ServerRoomTime_pb2_grpc)

from Server.ServerConstants import MAX_GRPC_TRANSMISSION, CLIENT_WORKERS

from Client.ClientPlayer import ClientPlayerStart

def ClientTerminalRoom(RoomStub, ClientAddress, username):
    # Connect to Room
    response = RoomStub.JoinRoom(ServerRoomMusic_pb2.JoinRoomRequest(username=username, 
                                                                     ClientMusicAddress=ClientAddress))
    if not response.success:
        print("Error Connecting to Room")
        return

    while True:
        command = input(f"Room: Enter a command as {username}: ")
        if command == "exit":
            print("Exiting Room")
            RoomStub.LeaveRoom(ServerRoomMusic_pb2.LeaveRoomRequest(username=username))
            return
        lines = command.split()
        if not lines:
            continue
            
        elif lines[0] == "Start":
            request = RoomStub.StartSong(ServerRoomMusic_pb2.StartSongRequest())
            print(request.success)
        
        elif lines[0] == "Stop":
            request = RoomStub.StopSong(ServerRoomMusic_pb2.StopSongRequest())
            print(request.success)

        elif lines[0] == "Skip":
            request = RoomStub.SkipSong(ServerRoomMusic_pb2.SkipSongRequest())
            print(request.success)

        elif lines[0] == "Add":
            file = "Server/Music/MapleLeafRag.mp3"
            with open(file, "rb") as f:
                AudioBytes = f.read()
            request = RoomStub.AddSong(ServerRoomMusic_pb2.AddSongRequest(name="Maple Leaf Rag", AudioData=AudioBytes))
            print(request.success)
            print("Current Songs: ", request.MusicList)

        else:
            print("Unknown Command")
    

def ClientTerminalStart(LobbyStub, ClientAddress):
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

            elif lines[0] == "GetRooms":
                response = LobbyStub.GetRooms(ServerLobby_pb2.GetRoomsRequest())
                print("Rooms:\n", response.rooms)

            elif lines[0] == "StartJoin":
                if len(lines) < 2:
                    print("Usage: StartJoin <Name>")
                    continue
                room = lines[1]
                response = LobbyStub.StartRoom(ServerLobby_pb2.StartRoomRequest(name=room))
                if response.status == ServerLobby_pb2.Status.MATCH:
                    print(f"Name Taken.\nCurrent Rooms:\n{response.rooms}")
                elif response.status == ServerLobby_pb2.Status.ERROR:
                    print(f"Room Failed to Start.\nCurrent Rooms:\n{response.rooms}")
                else:
                    print(f"Room Made.\nCurrent Rooms:\n{response.rooms}")
                    room = "Room: " + room
                    response = LobbyStub.GetRooms(ServerLobby_pb2.GetRoomsRequest())
                    roomlist = list(response.rooms)
                    RoomAddress = response.addresses[roomlist.index(room)]
                    try:
                        channel = grpc.insecure_channel(RoomAddress)
                        RoomStub = ServerRoomMusic_pb2_grpc.ServerRoomMusicStub(channel)
                        grpc.channel_ready_future(channel).result(timeout=1)
                        print(f"Client connected to {room} at {RoomAddress}")
                        LobbyStub.JoinRoom(ServerLobby_pb2.JoinRoomRequest(username=username, roomname=room))
                        ClientTerminalRoom(RoomStub, ClientAddress, username)
                    except grpc.FutureTimeoutError:
                        print("Failed to Connect") 
                    LobbyStub.LeaveRoom(ServerLobby_pb2.LeaveRoomRequest(username=username))

            elif lines[0] == "Join":
                response = LobbyStub.GetRooms(ServerLobby_pb2.GetRoomsRequest())
                if len(response.rooms) == 0:
                    print("No active rooms, create a room first")
                    continue
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
                    ClientTerminalRoom(RoomStub, ClientAddress, username)
                except grpc.FutureTimeoutError:
                    print("Failed to Connect") 
                LobbyStub.LeaveRoom(ServerLobby_pb2.LeaveRoomRequest(username=username))

            else:
                print("Unknown Command")

    except KeyboardInterrupt:
        LobbyStub.LeaveLobby(ServerLobby_pb2.LeaveLobbyRequest(username=username))
        return

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python ClientTerminal.py ServerHost:Port")
        sys.exit(1)
    ServerAddress = sys.argv[1]

    # Get hostname
    hostname = socket.gethostbyname(socket.gethostname())

    # Set up MusicPlayer
    ClientPlayer = grpc.server(futures.ThreadPoolExecutor(max_workers=2),
                         options = [('grpc.max_send_message_length', MAX_GRPC_TRANSMISSION),
                                    ('grpc.max_receive_message_length', MAX_GRPC_TRANSMISSION)])
    ClientPlayerAddress =  hostname + ":" + str(ClientPlayer.add_insecure_port(f"{hostname}:0"))

    TerminateCommand = threading.Event()

    Thread = threading.Thread(target=ClientPlayerStart, args=(ClientPlayer, ClientPlayerAddress, TerminateCommand,))
    Thread.start()

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

    ClientTerminalStart(LobbyStub, ClientPlayerAddress)
    
    TerminateCommand.set()

    print("Client Stopped")