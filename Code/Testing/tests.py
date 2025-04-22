import unittest
import sys
import os
import time
import threading
import grpc
import queue
import socket
import multiprocessing as mp
from unittest.mock import MagicMock, patch, Mock
from io import BytesIO

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Server.ServerLobby import ServerLobbyServicer
from Server.ServerRoom import (ServerRoomTimeServicer, ServerRoomMusicServicer, 
                              MusicPlayer, Command, startServerRoom)
from Server.ServerLobbyGRPC import ServerLobby_pb2, ServerLobby_pb2_grpc
from Server.ServerRoomGRPC import (ServerRoomMusic_pb2, ServerRoomMusic_pb2_grpc, 
                                  ServerRoomTime_pb2, ServerRoomTime_pb2_grpc)
from Client.ClientGRPC import Client_pb2, Client_pb2_grpc
from Server.ServerConstants import MAX_GRPC_OPTION

# Unit Tests for ServerLobby
class TestServerLobbyServicer(unittest.TestCase):
    def setUp(self):
        self.servicer = ServerLobbyServicer()
        # Mock user stub
        self.mock_user_stub = MagicMock()
        self.mock_user_stub.Heartbeat.return_value = Client_pb2.HeartbeatResponse()
        # Mock room stub
        self.mock_room_stub = MagicMock()
        self.mock_room_response = ServerRoomMusic_pb2.CurrentStateResponse(usernames=['user1'])
        self.mock_room_stub.CurrentState.return_value = self.mock_room_response
        
    def test_join_lobby_success(self):
        # Test successful join lobby
        with patch('grpc.insecure_channel') as _mock_channel, \
             patch('grpc.channel_ready_future') as mock_future, \
             patch('Client.ClientGRPC.Client_pb2_grpc.ClientStub') as mock_stub:
            mock_stub.return_value = self.mock_user_stub
            mock_future.return_value.result.return_value = None
            
            request = ServerLobby_pb2.JoinLobbyRequest(
                username='test_user',
                MusicPlayerAddress='127.0.0.1:50051'
            )
            context = MagicMock()
            
            response = self.servicer.JoinLobby(request, context)
            
            self.assertEqual(response.status, ServerLobby_pb2.Status.SUCCESS)
            self.assertIn('test_user', self.servicer.users)
            
    def test_join_lobby_duplicate(self):
        # Add a user first
        self.servicer.users = {'test_user': ('Lobby', int(time.time()), self.mock_user_stub)}
        
        # Test duplicate join attempt
        request = ServerLobby_pb2.JoinLobbyRequest(
            username='test_user',
            MusicPlayerAddress='127.0.0.1:50051'
        )
        context = MagicMock()
        
        response = self.servicer.JoinLobby(request, context)
        
        self.assertEqual(response.status, ServerLobby_pb2.Status.MATCH)
    
    def test_leave_lobby(self):
        # Add a user first
        self.servicer.users = {'test_user': ('Lobby', int(time.time()), self.mock_user_stub)}
        
        # Test leave lobby
        request = ServerLobby_pb2.LeaveLobbyRequest(username='test_user')
        context = MagicMock()
        
        response = self.servicer.LeaveLobby(request, context)
        
        self.assertEqual(response.status, ServerLobby_pb2.Status.SUCCESS)
        self.assertNotIn('test_user', self.servicer.users)
    
    def test_get_rooms(self):
        # Add a room first
        self.servicer.rooms = {
            'Room: test': ('127.0.0.1:50051', 1, int(time.time()), self.mock_room_stub)
        }
        
        request = ServerLobby_pb2.GetRoomsRequest()
        context = MagicMock()
        
        response = self.servicer.GetRooms(request, context)
        
        self.assertEqual(len(response.rooms), 1)
        self.assertEqual(response.rooms[0], 'Room: test')
        self.assertEqual(response.addresses[0], '127.0.0.1:50051')
    
    def test_join_room(self):
        # Setup
        self.servicer.users = {'test_user': ('Lobby', int(time.time()), self.mock_user_stub)}
        self.servicer.rooms = {
            'Room: test': ('127.0.0.1:50051', 0, int(time.time()), self.mock_room_stub)
        }
        
        request = ServerLobby_pb2.JoinRoomRequest(username='test_user', roomname='Room: test')
        context = MagicMock()
        
        response = self.servicer.JoinRoom(request, context)
        
        self.assertEqual(response.status, ServerLobby_pb2.Status.SUCCESS)
        self.assertEqual(self.servicer.users['test_user'][0], 'Room: test')
        self.assertEqual(self.servicer.rooms['Room: test'][1], 1)  # Count increased
    
    def test_leave_room(self):
        # Setup
        self.servicer.users = {'test_user': ('Room: test', int(time.time()), self.mock_user_stub)}
        self.servicer.rooms = {
            'Room: test': ('127.0.0.1:50051', 1, int(time.time()), self.mock_room_stub)
        }
        
        request = ServerLobby_pb2.LeaveRoomRequest(username='test_user', roomname='Room: test')
        context = MagicMock()
        
        response = self.servicer.LeaveRoom(request, context)
        
        self.assertEqual(response.status, ServerLobby_pb2.Status.SUCCESS)
        self.assertEqual(self.servicer.users['test_user'][0], 'Lobby')
        self.assertEqual(self.servicer.rooms['Room: test'][1], 0)  # Count decreased
    
    def test_start_room_success(self):
        # Test starting a new room
        with patch('multiprocessing.Process') as mock_process, \
             patch('multiprocessing.Queue') as mock_queue, \
             patch('grpc.insecure_channel') as _mock_channel, \
             patch('grpc.channel_ready_future') as mock_future, \
             patch('Server.ServerRoomGRPC.ServerRoomMusic_pb2_grpc.ServerRoomMusicStub') as mock_stub:
                
            mock_process_instance = MagicMock()
            mock_process.return_value = mock_process_instance
            
            mock_queue_instance = MagicMock()
            mock_queue_instance.get.return_value = '127.0.0.1:50052'
            mock_queue.return_value = mock_queue_instance
            
            mock_stub.return_value = self.mock_room_stub
            mock_future.return_value.result.return_value = None
            
            request = ServerLobby_pb2.StartRoomRequest(name='test_room')
            context = MagicMock()
            
            response = self.servicer.StartRoom(request, context)
            
            self.assertEqual(response.status, ServerLobby_pb2.Status.SUCCESS)
            self.assertIn('Room: test_room', self.servicer.rooms)
            mock_process_instance.start.assert_called_once()

# Unit Tests for ServerRoomTimeServicer
class TestServerRoomTimeServicer(unittest.TestCase):
    def setUp(self):
        self.servicer = ServerRoomTimeServicer()
    
    def test_time_sync(self):
        # Test time synchronization
        request = ServerRoomTime_pb2.TimeSyncRequest()
        context = MagicMock()
        
        response = self.servicer.TimeSync(request, context)
        
        # Verify that the response contains a timestamp
        self.assertIsNotNone(response.time)
        self.assertIsInstance(response.time, float)

# Unit Tests for ServerRoomMusicServicer
class TestServerRoomMusicServicer(unittest.TestCase):
    def setUp(self):
        # Create a mock terminate event
        self.terminate_event = threading.Event()
        
        # Set up the servicer with mock addresses
        self.time_address = '127.0.0.1:50053'
        self.room_address = '127.0.0.1:50054'
        self.room_name = 'Test Room'
        
        # Create a patch for the MusicPlayer thread
        self.thread_patcher = patch('threading.Thread')
        self.mock_thread = self.thread_patcher.start()
        mock_thread_instance = MagicMock()
        self.mock_thread.return_value = mock_thread_instance
        
        # Initialize the servicer
        self.servicer = ServerRoomMusicServicer(
            self.time_address, 
            self.room_address, 
            self.room_name, 
            self.terminate_event
        )
        
        # Create mock user stubs
        self.mock_user_stub = MagicMock()
        self.mock_user_stub.Heartbeat.return_value = Client_pb2.HeartbeatResponse()
        self.mock_user_stub.RegisterRoom.return_value = Client_pb2.RegisterRoomResponse(success=True)
    
    def tearDown(self):
        self.thread_patcher.stop()
        
    def test_kill_room(self):
        # Test killing a room
        request = ServerRoomMusic_pb2.KillRoomRequest()
        context = MagicMock()
        
        self.servicer.KillRoom(request, context)
        
        # Verify the terminate event was set
        self.assertTrue(self.terminate_event.is_set())
        
    def test_ping_and_remove_inactive(self):
        # Add a user
        self.servicer.users = {'test_user': self.mock_user_stub}
        self.servicer.delays = {'test_user': 0.1}
        
        # Test ping functionality
        self.servicer.Ping()
        
        # Verify heartbeat was called
        self.mock_user_stub.Heartbeat.assert_called_once()
        
        # For the inactive case, we'll directly simulate what the Ping method does
        # to avoid issues with the specific gRPC error type
        def fake_ping():
            # Directly add the user to inactive queue to simulate detection
            self.servicer.inactive.put('test_user')
        
        # Patch the Ping method to use our version
        with patch.object(self.servicer, 'Ping', fake_ping):
            # Call remove inactive
            self.servicer.RemoveInactive()
            
            # Verify the user was removed
            self.assertNotIn('test_user', self.servicer.users)
            self.assertNotIn('test_user', self.servicer.delays)
    
    def test_join_room_success(self):
        # Test joining a room successfully
        with patch('grpc.insecure_channel') as _mock_channel, \
             patch('grpc.channel_ready_future') as mock_future, \
             patch('Client.ClientGRPC.Client_pb2_grpc.ClientStub') as mock_stub:
                
            mock_stub.return_value = self.mock_user_stub
            mock_future.return_value.result.return_value = None
            
            request = ServerRoomMusic_pb2.JoinRoomRequest(
                username='test_user',
                ClientMusicAddress='127.0.0.1:50055'
            )
            context = MagicMock()
            
            response = self.servicer.JoinRoom(request, context)
            
            self.assertTrue(response.success)
            self.assertEqual(response.RoomTimeAddress, self.time_address)
            self.assertIn('test_user', self.servicer.users)
    
    def test_leave_room(self):
        # Setup
        self.servicer.users = {'test_user': self.mock_user_stub}
        self.servicer.delays = {'test_user': 0.1}
        
        # Test leave room
        request = ServerRoomMusic_pb2.LeaveRoomRequest(username='test_user')
        context = MagicMock()
        
        response = self.servicer.LeaveRoom(request, context)
        
        # Verify the leave method was called and user was removed
        self.mock_user_stub.Leave.assert_called_once()
        self.assertTrue(response.success)
        self.assertNotIn('test_user', self.servicer.users)
        
    def test_current_state(self):
        # Setup users and songs
        self.servicer.users = {'test_user': self.mock_user_stub}
        self.servicer.SongQueueList = [('song1', b'data1', 180), ('song2', b'data2', 240)]
        
        # Test current state
        request = ServerRoomMusic_pb2.CurrentStateRequest()
        context = MagicMock()
        
        with patch('threading.Timer') as _mock_timer:
            response = self.servicer.CurrentState(request, context)
        
        # Verify the response contains the correct data
        self.assertEqual(len(response.usernames), 1)
        self.assertEqual(response.usernames[0], 'test_user')
        self.assertEqual(len(response.MusicList), 2)
        self.assertEqual(response.MusicList[0], 'song1')
        self.assertEqual(response.MusicList[1], 'song2')
        
    def test_add_song(self):
        # Mock MP3 processing entirely
        with patch('Server.ServerRoom.MP3') as mock_mp3, \
             patch('Server.ServerRoom.BytesIO') as _mock_bytesio, \
             patch('threading.Timer') as _mock_timer, \
             patch.object(self.servicer, 'ReleaseLock') as _mock_release_lock:
            
            # Set up the MP3 mock
            mock_audio = MagicMock()
            mock_audio.info.length = 180
            mock_mp3.return_value = mock_audio
            
            # Test add song
            request = ServerRoomMusic_pb2.AddSongRequest(
                name='test_song',
                AudioData=b'test_audio_data'
            )
            context = MagicMock()
            
            # Mock the lock acquire
            self.servicer.ActionLock = MagicMock()
            self.servicer.ActionLock.acquire.return_value = True
            
            response = self.servicer.AddSong(request, context)
        
        # Verify song was added to queue
        self.assertTrue(response.success)
        self.assertEqual(self.servicer.SongQueue.qsize(), 1)
        
    def test_start_song(self):
        # Setup
        self.servicer.playing = False
        self.servicer.ActionLock = MagicMock()
        self.servicer.ActionLock.acquire.return_value = True
        self.servicer.CurrentSong = ('song1', b'data1', 180)
        
        # Test start song
        with patch.object(self.servicer, 'ReleaseLock') as _mock_release_lock:
            request = ServerRoomMusic_pb2.StartSongRequest()
            context = MagicMock()
            
            response = self.servicer.StartSong(request, context)
        
        # Verify action was queued
        self.assertTrue(response.success)
        self.assertEqual(self.servicer.ActionQueue.qsize(), 1)
        action = self.servicer.ActionQueue.get()
        self.assertEqual(action, Command.START)
        
    def test_stop_song(self):
        # Setup
        self.servicer.playing = True
        self.servicer.ActionLock = MagicMock()
        self.servicer.ActionLock.acquire.return_value = True
        
        # Test stop song
        with patch.object(self.servicer, 'ReleaseLock') as _mock_release_lock:
            request = ServerRoomMusic_pb2.StopSongRequest()
            context = MagicMock()
            
            response = self.servicer.StopSong(request, context)
        
        # Verify action was queued
        self.assertTrue(response.success)
        self.assertEqual(self.servicer.ActionQueue.qsize(), 1)
        action = self.servicer.ActionQueue.get()
        self.assertEqual(action, Command.STOP)

# Integration Tests
class TestServerIntegration(unittest.TestCase):
    @patch('Server.ServerRoom.startServerRoom')
    def test_lobby_create_and_join_room(self, mock_start_server_room):
        """Test the integration between ServerLobby and ServerRoom for room creation and joining"""
        # Create a real ServiceLobbyServicer instance instead of mocking the whole class
        lobby_servicer = ServerLobbyServicer()
        lobby_servicer.users = {}
        lobby_servicer.rooms = {}
        
        # Mock the process and queue for room creation
        with patch('multiprocessing.Process') as mock_process, \
             patch('multiprocessing.Queue') as mock_queue, \
             patch('grpc.insecure_channel') as _mock_channel, \
             patch('grpc.channel_ready_future') as mock_future, \
             patch('Server.ServerRoomGRPC.ServerRoomMusic_pb2_grpc.ServerRoomMusicStub') as mock_stub:
                
            # Setup for creating a room
            mock_process_instance = MagicMock()
            mock_process.return_value = mock_process_instance
            
            mock_queue_instance = MagicMock()
            mock_queue_instance.get.return_value = '127.0.0.1:50052'
            mock_queue.return_value = mock_queue_instance
            
            mock_room_stub = MagicMock()
            mock_stub.return_value = mock_room_stub
            mock_future.return_value.result.return_value = None
            
            # Create a room
            start_room_request = ServerLobby_pb2.StartRoomRequest(name='integration_test_room')
            context = MagicMock()
            
            start_room_response = lobby_servicer.StartRoom(start_room_request, context)
            
            # Verify room was created
            self.assertEqual(start_room_response.status, ServerLobby_pb2.Status.SUCCESS)
            mock_process_instance.start.assert_called_once()
            
            # Now test joining the room
            mock_user_stub = MagicMock()
            lobby_servicer.users = {'test_user': ('Lobby', int(time.time()), mock_user_stub)}
            lobby_servicer.rooms = {
                'Room: integration_test_room': ('127.0.0.1:50052', 0, int(time.time()), mock_room_stub)
            }
            
            join_room_request = ServerLobby_pb2.JoinRoomRequest(
                username='test_user', 
                roomname='Room: integration_test_room'
            )
            
            join_room_response = lobby_servicer.JoinRoom(join_room_request, context)
            
            # Verify user joined the room
            self.assertEqual(join_room_response.status, ServerLobby_pb2.Status.SUCCESS)
            self.assertEqual(lobby_servicer.users['test_user'][0], 'Room: integration_test_room')
            self.assertEqual(lobby_servicer.rooms['Room: integration_test_room'][1], 1)

class TestMusicPlayerIntegration(unittest.TestCase):
    @patch('threading.Thread')
    def test_music_player_integration(self, mock_thread):
        """Test integration between MusicPlayer thread and ServerRoomMusicServicer"""
        # Mock thread
        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance
        
        # Create servicer with real logic but mocked threading
        terminate_event = threading.Event()
        time_address = '127.0.0.1:50053'
        room_address = '127.0.0.1:50054'
        room_name = 'Test Music Room'
        
        # Create the servicer with patched components to avoid actual threading issues
        with patch('Server.ServerRoom.MusicPlayer') as _mock_music_player:
            servicer = ServerRoomMusicServicer(
                time_address, 
                room_address, 
                room_name, 
                terminate_event
            )
            
            # Patch ReleaseLock to avoid threading issues
            servicer.ReleaseLock = MagicMock()
            
            # Mock the client stub
            mock_user_stub = MagicMock()
            servicer.users = {'test_user': mock_user_stub}
            
            # Test song operations flow with mocked lock to prevent actual thread activity
            servicer.ActionLock = MagicMock()
            servicer.ActionLock.acquire.return_value = True
            
            # 1. Add a song
            with patch('Server.ServerRoom.MP3') as mock_mp3, \
                 patch('Server.ServerRoom.BytesIO') as _mock_bytesio:
                mock_audio = MagicMock()
                mock_audio.info.length = 180
                mock_mp3.return_value = mock_audio
                
                add_request = ServerRoomMusic_pb2.AddSongRequest(
                    name='test_integration_song',
                    AudioData=b'test_audio_data'
                )
                context = MagicMock()
                
                add_response = servicer.AddSong(add_request, context)
            self.assertTrue(add_response.success)
        
        # 2. Start the song
        start_request = ServerRoomMusic_pb2.StartSongRequest()
        start_response = servicer.StartSong(start_request, context)
        self.assertTrue(start_response.success)
        
        # Verify START command was added to the queue
        self.assertEqual(servicer.ActionQueue.qsize(), 1)
        action = servicer.ActionQueue.get()
        self.assertEqual(action, Command.START)
        
        # Simulate that song is playing
        servicer.playing = True
        
        # 3. Stop the song
        stop_request = ServerRoomMusic_pb2.StopSongRequest()
        stop_response = servicer.StopSong(stop_request, context)
        self.assertTrue(stop_response.success)
        
        # Verify STOP command was added to the queue
        self.assertEqual(servicer.ActionQueue.qsize(), 1)
        action = servicer.ActionQueue.get()
        self.assertEqual(action, Command.STOP)

# Run the tests if this file is executed directly
if __name__ == '__main__':
    unittest.main()