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
                                    MAX_GRPC_OPTION, MAX_SONG_QUEUE, 
                                    REACTION_TIME, SONG_QUEUE_UPDATE, ROOM_WORKERS)

class Command(IntEnum):
    START = 0
    STOP = 1
    SKIP = 2
    ADD = 3


def MusicPlayer(Servicer):
    position = 0
    PrevTime = 0
    CurrTime = 0
    action = None

    while not Servicer.Terminate.is_set():
        try:
            action = Servicer.ActionQueue.get_nowait()
            print("Recieved action", action)
        except queue.Empty:
            if Servicer.playing and position + time.clock_gettime(time.CLOCK_REALTIME) - PrevTime > Servicer.CurrentSong[2]: # Song over
                Servicer.CurrentSong = None
                Servicer.playing = False
                action = None
                if not Servicer.SongQueue.empty():
                    action = Command.START
            else:
                continue

        Delay = (max(Servicer.delays.values()) if len(Servicer.delays) > 0 else 0)
        Delay = Delay*WAIT_MULTIPLIER + CONSTANT_PROCCESS_TIME

        if action == Command.SKIP:
            Servicer.CurrentSong = Servicer.SongQueue.get()
            position = 0
            action = Command.START

        if action == Command.START:   
            if Servicer.CurrentSong == None:
                Servicer.CurrentSong = Servicer.SongQueue.get()           
            CurrTime = time.clock_gettime(time.CLOCK_REALTIME) + Delay
            for user in Servicer.users.keys():
                try:
                    Servicer.users[user].StartSong(Client_pb2.StartSongRequest(name=Servicer.CurrentSong[0], 
                                                                               time=CurrTime, 
                                                                               position = position))
                except grpc._channel._InactiveRpcError:
                    Servicer.inactive.put(user)
                    print("Missed", user)

            PrevTime = CurrTime
            Servicer.playing = True
            print(f"Sent Song Start request to all clients at {round(CurrTime%100000, 5)}")
            print("All", list(Servicer.users.keys()))
            print("Started", Servicer.CurrentSong[0], "lasting", Servicer.CurrentSong[2])

        elif action == Command.STOP:
            if Servicer.CurrentSong[2] - position < REACTION_TIME:
                continue

            CurrTime = time.clock_gettime(time.CLOCK_REALTIME) + Delay
            for user in Servicer.users.keys():
                try:
                    Servicer.users[user].StopSong(Client_pb2.StopSongRequest(time=CurrTime))
                except grpc._channel._InactiveRpcError:
                    Servicer.inactive.put(user)
                    print("Missed", user)

            position += (CurrTime - PrevTime)//1 # Round down to nearest second
            PrevTime = CurrTime
            Servicer.playing = False
            print(f"Sent Song Stop request to all clients at {round(CurrTime%100000, 5)}")
            print("All", list(Servicer.users.keys()))

class ServerRoomTimeServicer(ServerRoomTime_pb2_grpc.ServerRoomTimeServicer):
    def TimeSync(self, request, context):
        return ServerRoomTime_pb2.TimeSyncResponse(time=time.clock_gettime(time.CLOCK_REALTIME))

class ServerRoomMusicServicer(ServerRoomMusic_pb2_grpc.ServerRoomMusicServicer):
    def __init__(self, TimeAddress, RoomAddress, Name, Terminate):
        self.name = Name # Read only
        self.RoomAddress = RoomAddress # Read only
        self.TimeAddress = TimeAddress # Read only
        self.Terminate = Terminate # Atomic Servicer Write, Thread Read

        self.users = {}  # Holds user to User music GRPC mappings, Servicer Write, Thread Read
        self.delays = {} # Holds user to delay mappings, Servicer Write, Thread Read
        self.SongQueue = queue.Queue(maxsize=MAX_SONG_QUEUE) # list of (Name, bytes, duration) mappings, Atomic or mutexed

        self.ActionQueue = queue.Queue() # Servicer Write, Thread Read
        self.ActionLock = threading.Lock() # Servicer Write

        self.QueueUpdateTime = time.time() # Servicer Write
        self.SongQueueList = [] # Servicer Write
        self.CurrentSong = None # Thread Write
        self.playing = False # Thread Write

        self.inactive = queue.Queue() # Atomic

        MusicPlayerThread = threading.Thread(target=MusicPlayer, args=(self,))
        MusicPlayerThread.start()

    def ReleaseLock(self):
        release = threading.Timer(REACTION_TIME, self.ActionLock.release)
        release.start()

    # Kill Room
    def KillRoom(self, request, context):
        print("Shutting Down", self.name)
        self.Terminate.set()
        return ServerRoomMusic_pb2.KillRoomResponse()
    
    # Ping all users
    def Ping(self):
        # print("Pinging all Users")
        
        for user in self.users.keys():
            try:
                self.users[user].Heartbeat(Client_pb2.HeartbeatRequest())
            except grpc._channel._InactiveRpcError:
                self.inactive.put(user)
                print("Ping Missed", user)
        #print("Room Ping to", list(self.users.keys()))
    
    # Remove Inactive Users
    def RemoveInactive(self):
        self.Ping()
        while not self.inactive.empty():
            current = self.inactive.get()
            if current in self.users:
                del self.users[current]
            if current in self.delays:
                del self.delays[current]
        if len(self.users) == 0:
            print("No Users Left")
            self.Terminate.set()
    
    # Try to join a room
    def JoinRoom(self, request, context):
        print("Join Room Request: ", request.username, request.ClientMusicAddress)
        if len(self.users) > 0:
            self.RemoveInactive()
        # Establish stub to user
        UserStub = None
        try:
            channel = grpc.insecure_channel(request.ClientMusicAddress, options = MAX_GRPC_OPTION)
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
        
        print("TimeSync Start Success for", request.username)
        self.users[request.username] = UserStub

        # Check if joined late
        
        if self.CurrentSong != None or not self.SongQueue.empty():
            print(f"{request.username} Joined Late, Sending Songs")
            name = None
            AudioData = None
            SongList = None
            with self.SongQueue.mutex:
                if self.CurrentSong != None:
                    name, AudioData, _duration = self.CurrentSong
                SongList = list(self.SongQueue.queue)
            
            print("Sending Current Song", name, AudioData)
            if name != None:
                try:
                    UserStub.AddSong(Client_pb2.AddSongRequest(name=name, AudioData=AudioData))
                except grpc._channel._InactiveRpcError:
                    return ServerRoomMusic_pb2.JoinRoomResponse(success=False, RoomTimeAddress=self.TimeAddress)
            
            print("Sending Remaining Songs")
            for song in SongList:
                try:
                    UserStub.AddSong(Client_pb2.AddSongRequest(name=song[0], AudioData=song[1]))
                except grpc._channel._InactiveRpcError:
                    return ServerRoomMusic_pb2.JoinRoomResponse(success=False, RoomTimeAddress=self.TimeAddress)
                
        
        
        print(request.username, "has successfully joined", self.name)
        return ServerRoomMusic_pb2.JoinRoomResponse(success=True, RoomTimeAddress=self.TimeAddress)

    # Inform you left a room
    def LeaveRoom(self, request, context):
        if request.username in self.users:
            self.users[request.username].Leave(Client_pb2.LeaveRequest())
            del self.users[request.username]
        if request.username in self.delays:
            del self.delays[request.username]

        print(request.username, "has left", self.name)

        self.RemoveInactive()

        return ServerRoomMusic_pb2.LeaveRoomResponse(success=True)
    
    # Update TimeSync stats
    def SyncStat(self, request, context):
        self.delays[request.username] = request.delay
        return ServerRoomMusic_pb2.SyncStatResponse()

    # Current State
    def CurrentState(self, request, context):
        if time.time() - self.QueueUpdateTime > SONG_QUEUE_UPDATE:
            with self.SongQueue.mutex:
                self.SongQueueList = list(self.SongQueue.queue)
                self.QueueUpdateTime = time.time()
            remove = threading.Timer(1, self.RemoveInactive)
            remove.start()
        return ServerRoomMusic_pb2.CurrentStateResponse(usernames=list(self.users.keys()), 
                                                        MusicList=[item[0] for item in self.SongQueueList])

    # Add Song RPC method
    def AddSong(self, request, context):
        if not self.ActionLock.acquire(blocking=False):
            return ServerRoomMusic_pb2.AddSongResponse(success=False)
        
        print("Adding", request.name, "to", self.name)

        name = request.name + str(int(time.time()))

        audio = MP3(BytesIO(request.AudioData))
        try:
            self.SongQueue.put_nowait((name, request.AudioData, audio.info.length))
        except queue.Full:
            self.ActionLock.release()
            return ServerRoomMusic_pb2.AddSongResponse(success=False)
        
        print("Inform Users of Song")

        for user in self.users.keys():
            try:
                self.users[user].AddSong(Client_pb2.AddSongRequest(name=name, AudioData=request.AudioData))
            except grpc._channel._InactiveRpcError:
                self.inactive.put(user)
                print("Missed", user)
        print("Sent", name, "to", list(self.users.keys()))

        self.ReleaseLock()
        return ServerRoomMusic_pb2.AddSongResponse(success=True)

    # Skip Song
    def SkipSong(self, request, context):
        if not self.ActionLock.acquire(blocking=False):
            return ServerRoomMusic_pb2.SkipSongResponse(success=False)
        
        if self.CurrentSong == None or self.SongQueue.empty():
            self.ReleaseLock()
            return ServerRoomMusic_pb2.StartSongResponse(success=False)
        
        self.ActionQueue.put(Command.SKIP)

        self.ReleaseLock()
        return ServerRoomMusic_pb2.SkipSongResponse(success=True)

    # Start Song
    def StartSong(self, request, context):
        if self.playing or not self.ActionLock.acquire(blocking=False):
            print("Playing:", self.playing)
            return ServerRoomMusic_pb2.StartSongResponse(success=False)
        print("Recieved Start Song Command")
        print("Current Song:", (self.CurrentSong[0] if self.CurrentSong != None else "None"))
        if self.CurrentSong == None and self.SongQueue.empty():
            self.ReleaseLock()
            return ServerRoomMusic_pb2.StartSongResponse(success=False)
        
        self.ActionQueue.put(Command.START)

        self.ReleaseLock()
        return ServerRoomMusic_pb2.StartSongResponse(success=True)

    # Stop Song
    def StopSong(self, request, context):
        if not self.playing or not self.ActionLock.acquire(blocking=False):
            print("Playing:", self.playing)
            return ServerRoomMusic_pb2.StopSongResponse(success=False)
        self.ActionQueue.put(Command.STOP)

        self.ReleaseLock()
        return ServerRoomMusic_pb2.StopSongResponse(success=True)

def startServerRoom(LobbyQueue, Name):
    # Get hostname
    hostname = socket.gethostbyname(socket.gethostname())

    # Set up thread terminator
    Terminate = threading.Event()

    # Start ServerRoomTime gRPC server.
    ServerRoomTime = grpc.server(futures.ThreadPoolExecutor(max_workers=ROOM_WORKERS))
    ServerRoomTime_pb2_grpc.add_ServerRoomTimeServicer_to_server(ServerRoomTimeServicer(), ServerRoomTime)
    TimeAddress = hostname + ":" + str(ServerRoomTime.add_insecure_port(f"{hostname}:0"))
    ServerRoomTime.start()
    print(f"ServerRoomTime started on {TimeAddress}")

    # Start ServerRoomMusic gRPC server.
    ServerRoomMusic = grpc.server(futures.ThreadPoolExecutor(max_workers=ROOM_WORKERS), options = MAX_GRPC_OPTION)
    RoomAddress = hostname + ":" + str(ServerRoomMusic.add_insecure_port(f"{hostname}:0"))
    ServerRoomMusic_pb2_grpc.add_ServerRoomMusicServicer_to_server(ServerRoomMusicServicer(TimeAddress, RoomAddress, Name, Terminate), ServerRoomMusic)
    ServerRoomMusic.start()
    print(f"ServerRoomMusic started on {RoomAddress}")

    if LobbyQueue != None:
        LobbyQueue.put(RoomAddress)
    
    while not Terminate.is_set():
        time.sleep(1)

    time.sleep(1)
    ServerRoomMusic.stop(0)
    ServerRoomTime.stop(0)
    print("Fully Shutdown", Name)

if __name__ == '__main__':
    startServerRoom(None, None)
