from concurrent import futures
import grpc
import time
import socket

from Client.ClientGRPC import Client_pb2, Client_pb2_grpc
from Server.ServerLobbyGRPC import ServerLobby_pb2, ServerLobby_pb2_grpc
from Server.ServerRoomGRPC import (ServerRoomMusic_pb2, ServerRoomMusic_pb2_grpc, 
                            ServerRoomTime_pb2, ServerRoomTime_pb2_grpc)

from Server.ServerConstants import MAX_TOLERANT_DELAY, WAIT_MULTIPLIER, MAX_DISTRIBUTION_TIME, CONSTANT_PROCCESS_TIME

class ServerRoomTimeServicer(ServerRoomTime_pb2_grpc.ServerRoomTimeServicer):
    def TimeSync(self, request, context):
        return ServerRoomTime_pb2.TimeSyncResponse(time=time.clock_gettime(time.CLOCK_REALTIME))

class ServerRoomMusicServicer(ServerRoomMusic_pb2_grpc.ServerRoomMusicServicer):
    def __init__(self, TimeAddress, Name, Room):
        self.Servicer = Room
        self.name = Name
        self.TimeAddress = TimeAddress
        self.users = {}  # Holds user to stub mappings
        self.delays = {} # Holds user to delay mappings

    def Shutdown(self):
        time.sleep(1)
        print("Shutting Down", self.name)
        self.Servicer.stop(0)

    # Kill Room
    def KillRoom(self, request, context):
        self.Shutdown()
        return ServerRoomMusic_pb2.KillRoomResponse()
    
    # Try to join a room
    def JoinRoom(self, request, context):
        print("Join Room Request: ", request.username, request.ClientAddress)
        # Establish stub to user
        UserStub = None
        try:
            channel = grpc.insecure_channel(request.ClientAddress)
            UserStub = Client_pb2_grpc.ClientStub(channel)
            grpc.channel_ready_future(channel).result(timeout=1)
            print(f"Room connected to User {request.username} at {request.ClientAddress}")
        except Exception as e:
            print(f"Failed to connect to User: {e}")
            return ServerRoomMusic_pb2.JoinRoomResponse(status=ServerRoomMusic_pb2.Status.ERROR, 
                                                    RoomTimeAddress=self.TimeAddress)
        self.users[request.username] = UserStub
        
        print(request.username, "has successfully joined", self.name)
        return ServerRoomMusic_pb2.JoinRoomResponse(status=ServerRoomMusic_pb2.Status.SUCCESS, 
                                                    RoomTimeAddress=self.TimeAddress)

    # Inform you left a room
    def LeaveRoom(self, request, context):
        if request.username in self.users:
            del self.users[request.username]
            del self.delays[request.username]
        print(request.username, "has left", self.name)
        return ServerRoomMusic_pb2.LeaveRoomResponse(status=ServerRoomMusic_pb2.Status.SUCCESS)
    
    # Update TimeSync stats
    def SyncStat(self, request, context):
        CurrentDelay = (max(self.delays.values()) if len(self.delays) > 0 else 0)
        if (request.delay > MAX_TOLERANT_DELAY or 
            CurrentDelay*WAIT_MULTIPLIER > MAX_DISTRIBUTION_TIME):
            return ServerRoomMusic_pb2.SyncStatResponse(status=ServerRoomMusic_pb2.Status.ERROR)
        self.delays[request.username] = request.delay
        return ServerRoomMusic_pb2.SyncStatResponse(status=ServerRoomMusic_pb2.Status.SUCCESS)

    # Current State
    def CurrentState(self, request, context):
        return ServerRoomMusic_pb2.CurrentStateResponse(usernames=list(self.users.keys()))

    # Add Song RPC method
    def AddSong(self, request, context):
        pass

    # Delete Song
    def DeleteSong(self, request, context):
        pass

    # Start Song
    def StartSong(self, request, context):
        print("Recieved Start Song Command")
        Delay = (max(self.delays.values()) if len(self.delays) > 0 else 0)
        Delay = Delay*WAIT_MULTIPLIER + CONSTANT_PROCCESS_TIME
        Start = time.clock_gettime(time.CLOCK_REALTIME) + Delay
        file = "Server/Music/MapleLeafRag.mp3"
        inactive = []
        with open(file, 'rb') as f:
            SongBytes = f.read()

        for user in self.users.keys():
            try:
                print("Try ping", user)
                response = self.users[user].CurrentState(Client_pb2.CurrentStateRequest())
                print("Try ping", response.response)
            except Exception as e:
                print(f"Failed to Ping User: {e}")
            try:
                self.users[user].StartSong(Client_pb2.StartSongRequest(start=Start, AudioData=SongBytes))
            except grpc._channel._InactiveRpcError:
                inactive.append(user)
        print(f"Sent Song Start request to all clients at {round(Start%1000, 5)}")
        print("All", list(self.users.keys()), "\nMissed", inactive)
        return ServerRoomMusic_pb2.StartSongResponse()

    # Pause Song
    def PauseSong(self, request, context):
        pass

def startServerRoom(LobbyQueue, Name):
    # Get hostname
    hostname = socket.gethostbyname(socket.gethostname())

    # Start ServerRoomTime gRPC server.
    ServerRoomTime = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    ServerRoomTime_pb2_grpc.add_ServerRoomTimeServicer_to_server(ServerRoomTimeServicer(), ServerRoomTime)
    TimeAddress = hostname + ":" + str(ServerRoomTime.add_insecure_port(f"{hostname}:0"))
    ServerRoomTime.start()
    print(f"ServerRoomTime started on {TimeAddress}")

    # Start ServerRoomMusic gRPC server.
    ServerRoomMusic = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    ServerRoomMusic_pb2_grpc.add_ServerRoomMusicServicer_to_server(ServerRoomMusicServicer(TimeAddress, Name, ServerRoomMusic), ServerRoomMusic)
    MusicAddress = hostname + ":" + str(ServerRoomMusic.add_insecure_port(f"{hostname}:0"))
    ServerRoomMusic.start()
    print(f"ServerRoomMusic started on {MusicAddress}")

    if LobbyQueue != None:
        LobbyQueue.put(MusicAddress)

    ServerRoomMusic.wait_for_termination()
    ServerRoomTime.stop(0)
    print("Fully Shutdown", Name)

if __name__ == '__main__':
    startServerRoom(None, None)
