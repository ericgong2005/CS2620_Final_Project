from concurrent import futures
import grpc
import os
import time
import socket
import numpy as np
import queue
import itertools
import threading
import sys
from enum import IntEnum

import vlc

from Client.ClientGRPC import Client_pb2, Client_pb2_grpc
from Server.ServerLobbyGRPC import ServerLobby_pb2, ServerLobby_pb2_grpc
from Server.ServerRoomGRPC import (ServerRoomMusic_pb2, ServerRoomMusic_pb2_grpc, 
                            ServerRoomTime_pb2, ServerRoomTime_pb2_grpc)

from Server.ServerConstants import (WAIT, OFFSET_VARIANCE, OFFSET_COUNTS, DELAY_COUNTS, MAX_GRPC_OPTION, CLIENT_WORKERS)

class Command(IntEnum):
    LEAVE = 0
    PAUSE = 1
    START = 2
    LOAD = 3 
    SYNC = 4

def TimeSync(PlayerQueue, Event, Counter, TimeAddress, RoomAddress, Username, ThreadConfirm, Terminate):
    print("Starting New TimeSync")

    delay = []
    offset = []

    PrevOffset = 0
    PrevDelay = 0

    TimeStub = None
    try:
        channel = grpc.insecure_channel(TimeAddress)
        TimeStub = ServerRoomTime_pb2_grpc.ServerRoomTimeStub(channel)
        grpc.channel_ready_future(channel).result(timeout=1)
        print(f"ClientPlayer TimeSync connected to Time Provider at {TimeAddress}")
    except grpc.FutureTimeoutError:
        return
    
    RoomStub = None
    try:
        channel = grpc.insecure_channel(RoomAddress)
        RoomStub = ServerRoomMusic_pb2_grpc.ServerRoomMusicStub(channel)
        grpc.channel_ready_future(channel).result(timeout=1)
        print(f"ClientPlayer TimeSync connected to Room at {RoomAddress}")
    except grpc.FutureTimeoutError:
        return
    
    ThreadConfirm.set()
    try:
        while not Event.is_set() and not Terminate.is_set():
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

            if len(offset) > OFFSET_COUNTS:
                offset = offset[1:]
            if len(delay) > DELAY_COUNTS:
                delay = delay[1:]

            CurrDelay = np.max(delay)
            CurrOffset = np.mean(offset)

            if CurrDelay > PrevDelay:
                RoomStub.SyncStat(ServerRoomMusic_pb2.SyncStatRequest(delay=CurrDelay, username=Username))
            if abs(CurrOffset - PrevOffset) > OFFSET_VARIANCE:
                PlayerQueue.put((Command.SYNC, next(Counter), CurrOffset))

            PrevDelay = CurrDelay
            PrevOffset = CurrOffset

            time.sleep(WAIT)
    except grpc._channel._InactiveRpcError:
        pass
    print("Ending current TimeSync")
    sys.exit(0)

class ClientServicer(Client_pb2_grpc.ClientServicer):
    def __init__(self, PlayerQueue, PlayerAddress, MusicPath, Terminate):
        self.PlayerQueue = PlayerQueue
        self.PlayerAddress = PlayerAddress
        self.MusicPath = MusicPath
        self.Terminate = Terminate
        self.Counter = itertools.count()
        self.CurrentTimeSync = threading.Event()
        self.RecievedSongs = []


    # Register Room
    def RegisterRoom(self, request, context):
        print("Recieved Register Room Request")

        self.CurrentTimeSync.set()

        self.CurrentTimeSync = threading.Event()
        ThreadConfirm = threading.Event()
        Thread = threading.Thread(target=TimeSync, args=(self.PlayerQueue, self.CurrentTimeSync, 
                                                         self.Counter, request.TimeAddress, request.RoomAddress,
                                                         request.username, ThreadConfirm, self.Terminate))
        Thread.start()

        # If the thread returns before Confirm is set, the TimeSync start failed
        while not ThreadConfirm.is_set():
            if not Thread.is_alive():
                return Client_pb2.RegisterRoomResponse(success=False)

        return Client_pb2.RegisterRoomResponse(success=True)
    
    # Add Song
    def AddSong(self, request, context):
        print("Recieved Load Song Request")

        file = os.path.join(self.MusicPath, request.name)
        with open(file, 'wb') as f:
            f.write(request.AudioData)
        self.PlayerQueue.put((Command.LOAD, next(self.Counter), request.name, str(file)))

        return Client_pb2.AddSongResponse()

    # Start Song
    def StartSong(self, request, context):
        self.PlayerQueue.put((Command.START, next(self.Counter), request.time, request.name, request.position))
        return Client_pb2.StartSongResponse()

    # Stop Song
    def StopSong(self, request, context):
        self.PlayerQueue.put((Command.PAUSE, next(self.Counter), request.time))
        return Client_pb2.StopSongResponse()
    
    # Left Room
    def Leave(self, request, context):
        self.PlayerQueue.put((Command.LEAVE, next(self.Counter)))
        return Client_pb2.LeaveResponse()
    
    # Heartbeat
    def Heartbeat(self, request, context):
        return Client_pb2.HeartbeatResponse()


def ClientPlayerStart(ClientPlayer, PlayerAddress, Terminate):
    PlayerQueue = queue.Queue()

    Songs = {}
    CurrentSong = None
    CurrentSongName = None
    Offset = 0

    MusicPath = f"Client/Client_{PlayerAddress.replace(':', '_')}"
    os.makedirs(MusicPath, exist_ok=True)

    VLCInstance = vlc.Instance('--quiet')

    Client_pb2_grpc.add_ClientServicer_to_server(ClientServicer(PlayerQueue, PlayerAddress, MusicPath, Terminate), ClientPlayer)
    
    ClientPlayer.start()
    print(f"ClientPlayer started on {PlayerAddress}")

    while not Terminate.is_set(): 
        try:
            request = PlayerQueue.get(timeout=1)
            print(request)
        except queue.Empty:
            continue

        if request[0] == Command.LOAD and request[3] not in Songs:
            media  = VLCInstance.media_new_path(os.path.abspath(request[3]))
            media.add_option(':start-paused')  
            player = VLCInstance.media_player_new()
            player.set_media(media)
            Songs[request[2]] = player
            player.play()
        
        if request[0] == Command.START:
            try:
                CurrentSong = Songs[request[3]]
            except KeyError:
                print("You don't have this song!")
                continue
            Start = request[2] + Offset
            while time.clock_gettime(time.CLOCK_REALTIME) < Start: pass
            CurrentSong.set_time(int(request[4]*1000))
            CurrentSong.play()
            print("True start at", round(time.clock_gettime(time.CLOCK_REALTIME)%1000,5))
            print("Want start at", round(Start%1000,5))

            if request[3] != CurrentSongName:
                if CurrentSongName in Songs:
                    Songs[CurrentSongName].release()
                    del Songs[CurrentSongName]
                CurrentSongName = request[3]
        
        if request[0] == Command.PAUSE and CurrentSong != None:
            Start = request[2] + Offset
            while time.clock_gettime(time.CLOCK_REALTIME) < Start: pass
            CurrentSong.pause()
            print("True start at", round(time.clock_gettime(time.CLOCK_REALTIME)%1000,5))
            print("Want start at", round(Start%1000,5))

        if request[0] == Command.SYNC:
            Offset = request[2]
        
        if request[0] == Command.LEAVE:
            if CurrentSong != None:
                CurrentSong.release()
            Songs = {}
            CurrentSong = None
            CurrentSongName = None


    ClientPlayer.stop(0)

    VLCInstance.release()

    print("Client Player Stopped")

    sys.exit(0)
    

if __name__ == '__main__':
    hostname = socket.gethostbyname(socket.gethostname())
    ClientPlayer = grpc.server(futures.ThreadPoolExecutor(max_workers=CLIENT_WORKERS),options = MAX_GRPC_OPTION)
    ClientPlayerAddress =  hostname + ":" + str(ClientPlayer.add_insecure_port(f"{hostname}:0"))

    TerminateCommand = threading.Event()

    Thread = threading.Thread(target=ClientPlayerStart, args=(ClientPlayer, ClientPlayerAddress, TerminateCommand,))
    Thread.start()

    try:
        while True:
            time.sleep(1000)
    except KeyboardInterrupt:
        print("Shutdown Detected")
        TerminateCommand.set()