from concurrent import futures
import grpc
import os
import time
import socket
import numpy as np
import queue
import itertools
import threading
from enum import IntEnum

import vlc

from Client.ClientGRPC import Client_pb2, Client_pb2_grpc
from Server.ServerLobbyGRPC import ServerLobby_pb2, ServerLobby_pb2_grpc
from Server.ServerRoomGRPC import (ServerRoomMusic_pb2, ServerRoomMusic_pb2_grpc, 
                            ServerRoomTime_pb2, ServerRoomTime_pb2_grpc)

from Server.ServerConstants import WAIT, MAX_OFFSET_VARIANCE, MAX_REPEATS, COUNTS, MAX_GRPC_TRANSMISSION

class Command(IntEnum):
    PAUSE = 0   
    START = 1
    LOAD = 2  
    SYNC = 3

'''
Repeats < 0 will repeat the sync until the variance in the computed clock offset
is less than MAX_OFFSET_VARIANCE, or for the specified number of repeats
'''
def TimeSync(PlayerQueue, Event, Counter, TimeStub, Username):
    PrevOffset = 0
    PrevDelay = 0
    
    while not Event.is_set():

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

        
        
        time.sleep(WAIT)

class ClientServicer(Client_pb2_grpc.ClientServicer):
    def __init__(self, PlayerQueue, PlayerAddress, MusicPath):
        self.PlayerQueue = PlayerQueue
        self.PlayerAddress = PlayerAddress
        self.MusicPath = MusicPath
        self.Counter = itertools.count()
        self.CurrentTimeSync = threading.Event()

    # Register Room
    def RegisterRoom(self, request, context):
        print("Recieved Register Room Request")

        self.CurrentTimeSync.set()

        TimeStub = None
        try:
            channel = grpc.insecure_channel(request.address)
            TimeStub = ServerRoomTime_pb2_grpc.ServerRoomTimeStub(channel)
            grpc.channel_ready_future(channel).result(timeout=1)
            print(f"ClientPlayer connected to Time Provider at {request.address}")
        except grpc.FutureTimeoutError:
            return Client_pb2.RegisterRoomResponse(Client_pb2.Status.ERROR)

        self.CurrentTimeSync = threading.Event()
        Thread = threading.Thread(target=TimeSync, args=(self.PlayerQueue, self.CurrentTimeSync, 
                                                         self.Counter, TimeStub, request.username,))
        Thread.start()

        return Client_pb2.RegisterRoomResponse(Client_pb2.Status.SUCCESS)
    
    # Load Song
    def LoadSong(self, request, context):
        print("Recieved Load Song Request")

        file = os.path.join(self.MusicPath, request.name)
        with open(file, 'wb') as f:
            f.write(request.AudioData)
        self.PlayerQueue.put((Command.LOAD, next(self.Counter), str(file)))

        return Client_pb2.LoadSongResponse()

    # Start Song
    def StartSong(self, request, context):
        self.PlayerQueue.put((Command.START, next(self.Counter), request.time, request.offset))
        return Client_pb2.StartSongResponse()

    # Pause Song
    def PauseSong(self, request, context):
        self.PlayerQueue.put((Command.PAUSE, next(self.Counter), request.time))
        return Client_pb2.PauseSongResponse()

def ClientPlayerStart(ClientPlayer, PlayerAddress):
    PlayerQueue = queue.Queue()

    MusicPath = f"Client/Client_{PlayerAddress.replace(':', '_')}"
    os.makedirs(MusicPath, exist_ok=True)

    Client_pb2_grpc.add_ClientServicer_to_server(ClientServicer(PlayerQueue, PlayerAddress, MusicPath), ClientPlayer)
    
    ClientPlayer.start()
    print(f"ClientPlayer started on {PlayerAddress}")
    
    ClientPlayer.stop(0)

    print("Client Stopped")
    

if __name__ == '__main__':
    hostname = socket.gethostbyname(socket.gethostname())
    ClientPlayer = grpc.server(futures.ThreadPoolExecutor(max_workers=1),
                         options = [('grpc.max_send_message_length', MAX_GRPC_TRANSMISSION),
                                    ('grpc.max_receive_message_length', MAX_GRPC_TRANSMISSION)])
    ClientPlayerAddress =  hostname + ":" + str(ClientPlayer.add_insecure_port(f"{hostname}:0"))

    ClientPlayerStart(ClientPlayer, ClientPlayerAddress)