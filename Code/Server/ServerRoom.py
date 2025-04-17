#!/usr/bin/env python3
# ServerRoom.py

from concurrent import futures
import grpc
import time
import socket

from Client.ClientGRPC import Client_pb2, Client_pb2_grpc
from Server.ServerLobbyGRPC import ServerLobby_pb2, ServerLobby_pb2_grpc
from Server.ServerRoomGRPC import (
    ServerRoomMusic_pb2, ServerRoomMusic_pb2_grpc,
    ServerRoomTime_pb2, ServerRoomTime_pb2_grpc
)
from Server.ServerConstants import (
    MAX_TOLERANT_DELAY, WAIT_MULTIPLIER,
    MAX_DISTRIBUTION_TIME, CONSTANT_PROCCESS_TIME
)

class ServerRoomTimeServicer(ServerRoomTime_pb2_grpc.ServerRoomTimeServicer):
    def TimeSync(self, request, context):
        return ServerRoomTime_pb2.TimeSyncResponse(
            time=time.clock_gettime(time.CLOCK_REALTIME)
        )

class ServerRoomMusicServicer(ServerRoomMusic_pb2_grpc.ServerRoomMusicServicer):
    def __init__(self, time_address, name, server):
        self.Servicer = server
        self.name = name
        self.time_address = time_address
        self.users = {}    # username -> ClientStub
        self.delays = {}   # username -> last delay
        self.queue = []    # list of (filename, audio_bytes)

    def Shutdown(self):
        time.sleep(1)
        print("Shutting Down", self.name)
        self.Servicer.stop(0)

    # Kill Room
    def KillRoom(self, request, context):
        self.Shutdown()
        return ServerRoomMusic_pb2.KillRoomResponse()

    # Join Room
    def JoinRoom(self, request, context):
        print("Join Room Request:", request.username, request.ClientAddress)
        try:
            chan = grpc.insecure_channel(request.ClientAddress)
            stub = Client_pb2_grpc.ClientStub(chan)
            grpc.channel_ready_future(chan).result(timeout=1)
        except Exception as e:
            print("Failed to connect to user stub:", e)
            return ServerRoomMusic_pb2.JoinRoomResponse(
                status=ServerRoomMusic_pb2.Status.ERROR,
                RoomTimeAddress=self.time_address
            )
        self.users[request.username] = stub
        print(request.username, "has successfully joined", self.name)
        return ServerRoomMusic_pb2.JoinRoomResponse(
            status=ServerRoomMusic_pb2.Status.SUCCESS,
            RoomTimeAddress=self.time_address
        )

    # Leave Room
    def LeaveRoom(self, request, context):
        if request.username in self.users:
            del self.users[request.username]
            self.delays.pop(request.username, None)
        print(request.username, "has left", self.name)
        return ServerRoomMusic_pb2.LeaveRoomResponse(
            status=ServerRoomMusic_pb2.Status.SUCCESS
        )

    # Sync statistics
    def SyncStat(self, request, context):
        current_max = max(self.delays.values()) if self.delays else 0
        if (request.delay > MAX_TOLERANT_DELAY or
            current_max * WAIT_MULTIPLIER > MAX_DISTRIBUTION_TIME):
            return ServerRoomMusic_pb2.SyncStatResponse(
                status=ServerRoomMusic_pb2.Status.ERROR
            )
        self.delays[request.username] = request.delay
        return ServerRoomMusic_pb2.SyncStatResponse(
            status=ServerRoomMusic_pb2.Status.SUCCESS
        )

    # Current State
    def CurrentState(self, request, context):
        return ServerRoomMusic_pb2.CurrentStateResponse(
            usernames=list(self.users.keys())
        )

    # Add Song
    def AddSong(self, request, context):
        print(f"[{self.name}] AddSong: {request.filename} ({len(request.audio_data)} bytes)")
        self.queue.append((request.filename, request.audio_data))
        position = len(self.queue) - 1
        return ServerRoomMusic_pb2.AddSongResponse(
            status=ServerRoomMusic_pb2.Status.SUCCESS,
            queue_position=position
        )

    # Delete Song (skip current)
    def DeleteSong(self, request, context):
        if not self.queue:
            print(f"[{self.name}] DeleteSong: queue empty")
            return ServerRoomMusic_pb2.DeleteSongResponse(
                status=ServerRoomMusic_pb2.Status.ERROR
            )
        fname, _ = self.queue.pop(0)
        print(f"[{self.name}] Deleted song '{fname}' from queue")
        return ServerRoomMusic_pb2.DeleteSongResponse(
            status=ServerRoomMusic_pb2.Status.SUCCESS
        )

    # Start Song: broadcast LoadSong + StartSong to each client
    def StartSong(self, request, context):
        print(f"[{self.name}] StartSong Command received")
        # compute synchronized start time
        max_delay = max(self.delays.values()) if self.delays else 0
        wait = max_delay * WAIT_MULTIPLIER + CONSTANT_PROCCESS_TIME
        start_time = time.clock_gettime(time.CLOCK_REALTIME) + wait

        # take the head of queue
        if not self.queue:
            print(f"[{self.name}] No song to play")
            return ServerRoomMusic_pb2.StartSongResponse(
                status=ServerRoomMusic_pb2.Status.ERROR
            )
        fname, audio_bytes = self.queue[0]

        inactive = []
        for user, stub in self.users.items():
            try:
                # 1) send the audio to client
                stub.LoadSong(
                    Client_pb2.LoadSongRequest(
                        song_name=fname,
                        audio_data=audio_bytes
                    )
                )
                # 2) tell client when to start
                stub.StartSong(
                    Client_pb2.StartSongRequest(
                        start=start_time,
                        offset=0.0
                    )
                )
            except Exception as e:
                print(f"[{self.name}] Failed StartSong to {user}:", e)
                inactive.append(user)

        print(f"[{self.name}] Broadcast StartSong at {start_time}, missed:", inactive)
        return ServerRoomMusic_pb2.StartSongResponse(
            status=ServerRoomMusic_pb2.Status.SUCCESS
        )

    # Pause Song → StopSong on client
    def PauseSong(self, request, context):
        # here request.pause_time is unused, we'll just issue Stop at now
        stop_time = time.clock_gettime(time.CLOCK_REALTIME)
        print(f"[{self.name}] PauseSong → StopSong at {stop_time}")
        for user, stub in self.users.items():
            try:
                stub.StopSong(
                    Client_pb2.StopSongRequest(stop=stop_time)
                )
            except Exception as e:
                print(f"[{self.name}] Failed StopSong to {user}:", e)
        return ServerRoomMusic_pb2.PauseSongResponse(
            status=ServerRoomMusic_pb2.Status.SUCCESS
        )


def startServerRoom(lobby_queue, name):
    host = socket.gethostbyname(socket.gethostname())

    # Time‐sync server
    time_srv = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    ServerRoomTime_pb2_grpc.add_ServerRoomTimeServicer_to_server(
        ServerRoomTimeServicer(), time_srv
    )
    time_addr = f"{host}:{time_srv.add_insecure_port(f'{host}:0')}"
    time_srv.start()
    print("ServerRoomTime started on", time_addr)

    # Music server
    music_srv = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    ServerRoomMusic_pb2_grpc.add_ServerRoomMusicServicer_to_server(
        ServerRoomMusicServicer(time_addr, name, music_srv),
        music_srv
    )
    music_addr = f"{host}:{music_srv.add_insecure_port(f'{host}:0')}"
    music_srv.start()
    print("ServerRoomMusic started on", music_addr)

    if lobby_queue:
        lobby_queue.put(music_addr)

    music_srv.wait_for_termination()
    time_srv.stop(0)
    print("Fully Shutdown", name)

if __name__ == "__main__":
    startServerRoom(None, None)
