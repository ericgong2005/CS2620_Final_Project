from concurrent import futures
import grpc
import time
import socket
import queue
import threading
from enum import IntEnum 
from io import BytesIO
from mutagen.mp3 import MP3

from Client.ClientGRPC import Client_pb2, Client_pb2_grpc
from Server.ServerLobbyGRPC import ServerLobby_pb2, ServerLobby_pb2_grpc
from Server.ServerRoomGRPC import (ServerRoomMusic_pb2, ServerRoomMusic_pb2_grpc, 
                            ServerRoomTime_pb2, ServerRoomTime_pb2_grpc)

from Server.ServerConstants import (MAX_TOLERANT_DELAY, WAIT_MULTIPLIER, 
                                    MAX_DISTRIBUTION_TIME, CONSTANT_PROCCESS_TIME, 
                                    MAX_GRPC_TRANSMISSION, MAX_SONG_QUEUE, REACTION_TIME)

class Command(IntEnum):
    START = 0
    PAUSE = 1
    SKIP = 2


def MusicPlayer(Terminate, SongQueue, ActionQueue, users, delays, inactive):
    CurrentSong = None
    position = 0
    PrevTime = 0
    CurrTime = 0
    action = None
    playing = False

    while not Terminate.set():
        try:
            action = ActionQueue.get_nowait()
        except:
            if playing and position + time.clock_gettime(time.CLOCK_REALTIME) - PrevTime > CurrentSong[2]: # Song over
                CurrentSong = SongQueue.get()
                position = 0
                action == Command.START

        Delay = (max(delays.values()) if len(delays) > 0 else 0)
        Delay = Delay*WAIT_MULTIPLIER + CONSTANT_PROCCESS_TIME

        if action == Command.SKIP:
            CurrentSong = SongQueue.get()
            position = 0
            action = Command.START

        if action == Command.START:
            if CurrentSong == None:
                CurrentSong = SongQueue.get()
            inactive = []
            CurrTime = time.clock_gettime(time.CLOCK_REALTIME) + Delay
            for user in users.keys():
                try:
                    users[user].StartSong(Client_pb2.StartSongRequest(name=CurrentSong[0], time=CurrTime, position = position))
                except grpc._channel._InactiveRpcError:
                    inactive.append(user)

            PrevTime = CurrTime
            playing = True
            print(f"Sent Song Start request to all clients at {round(CurrTime%100000, 5)}")
            print("All", list(users.keys()), "\nMissed", inactive)

        elif action == Command.STOP:
            if CurrentSong[2] - position < REACTION_TIME:
                continue

            inactive = []
            CurrTime = time.clock_gettime(time.CLOCK_REALTIME) + Delay
            for user in users.keys():
                try:
                    users[user].StopSong(Client_pb2.StopSongRequest(time=CurrTime))
                except grpc._channel._InactiveRpcError:
                    inactive.append(user)

            position += (CurrTime - PrevTime)//1 # Round down to nearest second
            PrevTime = CurrTime
            playing = False
            print(f"Sent Song Stop request to all clients at {round(CurrTime%100000, 5)}")
            print("All", list(users.keys()), "\nMissed", inactive)

class ServerRoomTimeServicer(ServerRoomTime_pb2_grpc.ServerRoomTimeServicer):
    def TimeSync(self, request, context):
        return ServerRoomTime_pb2.TimeSyncResponse(time=time.clock_gettime(time.CLOCK_REALTIME))

class ServerRoomMusicServicer(ServerRoomMusic_pb2_grpc.ServerRoomMusicServicer):
    def __init__(self, TimeAddress, RoomAddress, Name, Room, Terminate):
        self.Servicer = Room
        self.name = Name
        self.RoomAddress = RoomAddress
        self.TimeAddress = TimeAddress
        self.users = {}  # Holds user to User music GRPC mappings
        self.delays = {} # Holds user to delay mappings
        self.SongQueue = queue.Queue(maxsize=MAX_SONG_QUEUE) # list of (Name, bytes, duration) mappings

        self.ActionQueue = queue.Queue()
        self.ActionLock = threading.Lock()

        self.inactive = []

        MusicPlayerThread = threading.Thread(target=MusicPlayer, args=(Terminate, self.SongQueue, 
                                                                       self.ActionQueue, self.users, 
                                                                       self.delays, self.inactive))
        MusicPlayerThread.start()

    def Shutdown(self):
        time.sleep(1)
        print("Shutting Down", self.name)
        self.Servicer.stop(0)

    def ReleaseLock(self):
        time.sleep(REACTION_TIME)
        self.ActionLock.release()

    # Kill Room
    def KillRoom(self, request, context):
        self.Shutdown()
        return ServerRoomMusic_pb2.KillRoomResponse()
    
    # Try to join a room
    def JoinRoom(self, request, context):
        print("Join Room Request: ", request.username, request.ClientMusicAddress)
        # Establish stub to user
        UserStub = None
        try:
            channel = grpc.insecure_channel(request.ClientMusicAddress)
            UserStub = Client_pb2_grpc.ClientStub(channel)
            grpc.channel_ready_future(channel).result(timeout=1)
            print(f"Room connected to User {request.username} at {request.ClientMusicAddress}")
        except Exception as e:
            print(f"Failed to connect to {request.username}: {e}")
            return ServerRoomMusic_pb2.JoinRoomResponse(success=False, RoomTimeAddress=self.TimeAddress)
        
        response = UserStub.RegisterRoom(Client_pb2.RegisterRoomRequest(RoomAddress=self.RoomAddress,
                                                             TimeAddress=self.TimeAddress,
                                                             username=request.username))
       
        if not response.success:
            print("Failed to start TimeSync for", request.username)
            return ServerRoomMusic_pb2.JoinRoomResponse(success=False, RoomTimeAddress=self.TimeAddress)
        
        self.users[request.username] = UserStub
        
        print(request.username, "has successfully joined", self.name)
        return ServerRoomMusic_pb2.JoinRoomResponse(success=True, RoomTimeAddress=self.TimeAddress)

    # Inform you left a room
    def LeaveRoom(self, request, context):
        if request.username in self.users:
            del self.users[request.username]
        if request.username in self.delays:
            del self.delays[request.username]

        print(request.username, "has left", self.name)

        return ServerRoomMusic_pb2.LeaveRoomResponse(success=True)
    
    # Update TimeSync stats
    def SyncStat(self, request, context):
        self.delays[request.username] = request.delay
        return ServerRoomMusic_pb2.SyncStatResponse()

    # Current State
    def CurrentState(self, request, context):
        return ServerRoomMusic_pb2.CurrentStateResponse(usernames=list(self.users.keys()), 
                                                        MusicList=[item[0] for item in self.SongQueue])

    # Add Song RPC method
    def AddSong(self, request, context):
        if not self.ActionLock.acquire(blocking=False):
            return ServerRoomMusic_pb2.AddSongResponse(success=False, usernames=list(self.users.keys()), 
                                                        MusicList=[item[0] for item in self.SongQueue])
        
        print("Adding", request.name, "to", self.name)
        audio = MP3(BytesIO(request.AudioData))
        try:
            self.SongQueue.put_nowait(((request.name + str(time.time())), request.AudioData, audio.info.length))
        except queue.Full:
            self.ActionLock.release()
            return ServerRoomMusic_pb2.AddSongResponse(success=False, usernames=list(self.users.keys()), 
                                                        MusicList=[item[0] for item in self.SongQueue])
        
        inactive = []
        for user in self.users.keys():
            try:
                self.users[user].AddSong(Client_pb2.AddSongRequest(name=request.name, AudioData=request.AudioData))
            except grpc._channel._InactiveRpcError:
                inactive.append(user)
        print("Sent", request.name, "to", list(self.users.keys()), "\nMissed", inactive)

        self.ReleaseLock()
        return ServerRoomMusic_pb2.AddSongResponse(success=True, usernames=list(self.users.keys()), 
                                                        MusicList=[item[0] for item in self.SongQueue])

    # Skip Song
    def SkipSong(self, request, context):
        if not self.ActionLock.acquire(blocking=False):
            return ServerRoomMusic_pb2.SkipSongResponse(success=False)
        
        self.ActionQueue.put(Command.SKIP)

        self.ReleaseLock()
        return ServerRoomMusic_pb2.SkipSongRequest(sucess=True)

    # Start Song
    def StartSong(self, request, context):
        if not self.ActionLock.acquire(blocking=False):
            return ServerRoomMusic_pb2.StartSongResponse(success=False)
        print("Recieved Start Song Command")
        if self.SongQueue.empty():
            time.sleep(REACTION_TIME)
            self.ActionLock.release()
            return ServerRoomMusic_pb2.StartSongResponse(success=False)
        
        self.ActionQueue.put(Command.START)

        self.ReleaseLock()
        return ServerRoomMusic_pb2.StartSongResponse()

    # Pause Song
    def PauseSong(self, request, context):
        if not self.ActionLock.acquire(blocking=False):
            return ServerRoomMusic_pb2.PauseSongResponse(success=False)
        self.ActionQueue.put(Command.PAUSE)

        self.ReleaseLock()
        return ServerRoomMusic_pb2.PauseSongResponse(success=True)

def startServerRoom(LobbyQueue, Name):
    # Get hostname
    hostname = socket.gethostbyname(socket.gethostname())

    # Set up thread terminator
    Terminate = threading.Event()

    # Start ServerRoomTime gRPC server.
    ServerRoomTime = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    ServerRoomTime_pb2_grpc.add_ServerRoomTimeServicer_to_server(ServerRoomTimeServicer(), ServerRoomTime)
    TimeAddress = hostname + ":" + str(ServerRoomTime.add_insecure_port(f"{hostname}:0"))
    ServerRoomTime.start()
    print(f"ServerRoomTime started on {TimeAddress}")

    # Start ServerRoomMusic gRPC server.
    ServerRoomMusic = grpc.server(futures.ThreadPoolExecutor(max_workers=1),
                                  options = [('grpc.max_send_message_length', MAX_GRPC_TRANSMISSION),
                                    ('grpc.max_receive_message_length', MAX_GRPC_TRANSMISSION)])
    RoomAddress = hostname + ":" + str(ServerRoomMusic.add_insecure_port(f"{hostname}:0"))
    ServerRoomMusic_pb2_grpc.add_ServerRoomMusicServicer_to_server(ServerRoomMusicServicer(TimeAddress, RoomAddress, Name, ServerRoomMusic, Terminate), ServerRoomMusic)
    ServerRoomMusic.start()
    print(f"ServerRoomMusic started on {RoomAddress}")

    if LobbyQueue != None:
        LobbyQueue.put(RoomAddress)

    ServerRoomMusic.wait_for_termination()
    ServerRoomTime.stop(0)
    Terminate.set()
    print("Fully Shutdown", Name)

if __name__ == '__main__':
    startServerRoom(None, None)
