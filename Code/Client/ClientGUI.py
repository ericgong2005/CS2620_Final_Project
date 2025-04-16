#!/usr/bin/env python3
# ClientGUI.py

import sys
import socket
import threading
import time
import numpy as np

from concurrent import futures
import grpc

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QLineEdit, QPushButton,
    QMessageBox, QDialog, QListWidget, QVBoxLayout, QHBoxLayout,
    QWidget, QFrame, QFileDialog
)
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import QStandardPaths

from Client.ClientGRPC import Client_pb2, Client_pb2_grpc
from Server.ServerLobbyGRPC import ServerLobby_pb2, ServerLobby_pb2_grpc
from Server.ServerRoomGRPC import (
    ServerRoomMusic_pb2, ServerRoomMusic_pb2_grpc,
    ServerRoomTime_pb2, ServerRoomTime_pb2_grpc
)
from Server.ServerConstants import WAIT, MAX_OFFSET_VARIANCE, MAX_REPEATS, COUNTS


# -------------------------------------------------------------------
# Globals for our client‐side gRPC servicer
# -------------------------------------------------------------------
client_servicer_port = None
client_address = None
_client_ready_evt = threading.Event()


# -------------------------------------------------------------------
# TimeSync helper (copied from your terminal client)
# -------------------------------------------------------------------
def TimeSync(time_stub, offset_arr, delay_arr, repeats=-1):
    while True:
        start = time.clock_gettime(time.CLOCK_REALTIME)
        resp = time_stub.TimeSync(ServerRoomTime_pb2.TimeSyncRequest())
        end = time.clock_gettime(time.CLOCK_REALTIME)

        cur_delay = (end - start) / 2.0
        cur_offset = start + cur_delay - resp.time

        delay_arr = np.append(delay_arr, cur_delay)
        offset_arr = np.append(offset_arr, cur_offset)
        if len(delay_arr) > COUNTS:
            delay_arr = delay_arr[1:]
            offset_arr = offset_arr[1:]

        if (len(delay_arr) == COUNTS and
            (repeats == 0 or np.var(offset_arr) < MAX_OFFSET_VARIANCE or repeats + MAX_REPEATS < 0)):
            return offset_arr, delay_arr

        time.sleep(WAIT)
        repeats -= 1


# -------------------------------------------------------------------
# Our client‐side gRPC server (for StartSong, etc)
# -------------------------------------------------------------------
class ClientServicer(Client_pb2_grpc.ClientServicer):
    def CurrentState(self, request, context):
        return Client_pb2.CurrentStateResponse(response="OK")

    def LoadSong(self, request, context):
        pass

    def StartSong(self, request, context):
        print("Received StartSong RPC; would play at", request.start)
        return Client_pb2.StartSongResponse()

    def StopSong(self, request, context):
        pass


def serve_grpc():
    global client_servicer_port, client_address
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    Client_pb2_grpc.add_ClientServicer_to_server(ClientServicer(), server)

    client_servicer_port = server.add_insecure_port("0.0.0.0:0")
    server.start()

    host = socket.gethostbyname(socket.gethostname())
    client_address = f"{host}:{client_servicer_port}"
    print(f"[Client gRPC] listening on {client_address}")

    _client_ready_evt.set()
    server.wait_for_termination()


# -------------------------------------------------------------------
# Qt GUI Windows
# -------------------------------------------------------------------
class LoginWindow(QMainWindow):
    def __init__(self, lobby_stub, client_addr):
        super().__init__()
        self.lobby_stub = lobby_stub
        self.client_address = client_addr
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Music Client Login")
        self.setGeometry(100, 100, 400, 200)

        self.welcome_label = QLabel("Welcome", self)
        self.welcome_label.move(170, 20)

        self.username_label = QLabel("Enter Username:", self)
        self.username_label.move(50, 80)

        self.username_input = QLineEdit(self)
        self.username_input.move(160, 75)
        self.username_input.resize(180, 25)

        self.submit_btn = QPushButton("Submit", self)
        self.submit_btn.move(160, 120)
        self.submit_btn.clicked.connect(self.on_submit)

    def on_submit(self):
        username = self.username_input.text().strip()
        if not username:
            QMessageBox.warning(self, "Input Error", "Username cannot be empty.")
            return

        try:
            req = ServerLobby_pb2.JoinLobbyRequest(username=username)
            resp = self.lobby_stub.JoinLobby(req)
        except grpc.RpcError as e:
            QMessageBox.critical(self, "RPC Error", f"Could not reach lobby server:\n{e}")
            return

        if resp.status == ServerLobby_pb2.Status.MATCH:
            QMessageBox.information(self, "Username Taken",
                                    f"Username '{username}' is already taken.")
        else:
            QMessageBox.information(self, "Username Available",
                                    f"Username '{username}' is available!")
            self.hide()
            self.lobby_win = LobbyWindow(self.lobby_stub, username,
                                         login_window=self,
                                         client_address=self.client_address)
            self.lobby_win.show()


class LobbyWindow(QMainWindow):
    def __init__(self, lobby_stub, username, login_window, client_address):
        super().__init__()
        self.lobby_stub = lobby_stub
        self.username = username
        self.login_window = login_window
        self.client_address = client_address
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"Lobby - {self.username}")
        self.setGeometry(100, 100, 400, 200)

        self.label = QLabel(f"Welcome {self.username}", self)
        self.label.move(150, 20)

        self.create_btn = QPushButton("Create Room", self)
        self.create_btn.move(50, 80)
        self.create_btn.clicked.connect(self.on_create)

        self.join_btn = QPushButton("Join Room", self)
        self.join_btn.move(150, 80)
        self.join_btn.clicked.connect(self.on_join)

        self.exit_btn = QPushButton("Exit Lobby", self)
        self.exit_btn.move(275, 80)
        self.exit_btn.clicked.connect(self.on_exit)

    def on_exit(self):
        req = ServerLobby_pb2.LeaveLobbyRequest(username=self.username)
        self.lobby_stub.LeaveLobby(req)
        self.close()
        self.login_window.show()

    def on_join(self):
        dialog = JoinRoomDialog(self.lobby_stub, self, self.username)
        if dialog.exec_() == QDialog.Accepted:
            self.hide()
            self.room_win = RoomWindow(
                lobby_stub=self.lobby_stub,
                username=self.username,
                room_name=dialog.room_name,
                room_address=dialog.room_address,
                parent_lobby=self,
                client_address=self.client_address
            )
            self.room_win.show()

    def on_create(self):
        dialog = CreateRoomDialog(self.lobby_stub, self, self.username)
        if dialog.exec_() == QDialog.Accepted:
            self.hide()
            self.room_win = RoomWindow(
                lobby_stub=self.lobby_stub,
                username=self.username,
                room_name=dialog.room_name,
                room_address=dialog.room_address,
                parent_lobby=self,
                client_address=self.client_address
            )
            self.room_win.show()


class JoinRoomDialog(QDialog):
    def __init__(self, lobby_stub, parent_lobby, username):
        super().__init__(parent_lobby)
        self.lobby_stub = lobby_stub
        self.parent_lobby = parent_lobby
        self.username = username
        self.room_name = None
        self.room_address = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Join Room")
        self.setGeometry(200, 200, 400, 300)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Enter Room Code", self))

        try:
            resp = self.lobby_stub.GetRooms(ServerLobby_pb2.GetRoomsRequest())
        except grpc.RpcError as e:
            QMessageBox.critical(self, "RPC Error", f"Error retrieving rooms:\n{e}")
            self.reject()
            return

        self.rooms = list(resp.rooms)
        self.addresses = list(resp.addresses)

        self.list = QListWidget(self)
        for room in self.rooms:
            self.list.addItem(room)
        layout.addWidget(self.list)

        self.input = QLineEdit(self)
        layout.addWidget(self.input)

        join_btn = QPushButton("Join", self)
        join_btn.clicked.connect(self.on_join)
        layout.addWidget(join_btn)

        cancel = QPushButton("Cancel", self)
        cancel.clicked.connect(self.reject)
        layout.addWidget(cancel)

        self.setLayout(layout)

    def on_join(self):
        roomname = self.input.text().strip()
        if not roomname:
            QMessageBox.warning(self, "Input Error", "Room name cannot be empty.")
            return

        req = ServerLobby_pb2.JoinRoomRequest(username=self.username, roomname=roomname)
        resp = self.lobby_stub.JoinRoom(req)
        if resp.status == ServerLobby_pb2.Status.ERROR:
            QMessageBox.information(self, "Error", "This room does not exist.")
            return

        address = None
        for r, addr in zip(self.rooms, self.addresses):
            if r == roomname:
                address = addr
                break

        if address is None:
            QMessageBox.critical(self, "Error", "Could not find address for that room.")
            return

        channel = grpc.insecure_channel(address)
        try:
            grpc.channel_ready_future(channel).result(timeout=5)
        except grpc.FutureTimeoutError:
            QMessageBox.critical(self, "Error", f"Cannot connect to room server at {address}")
            return

        QMessageBox.information(self, "Joined", f"Successfully joined '{roomname}' at {address}")
        self.room_name = roomname
        self.room_address = address
        self.accept()


class CreateRoomDialog(QDialog):
    def __init__(self, lobby_stub, parent_lobby, username):
        super().__init__(parent_lobby)
        self.lobby_stub = lobby_stub
        self.parent_lobby = parent_lobby
        self.username = username
        self.room_name = None
        self.room_address = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Create Room")
        self.setGeometry(200, 200, 300, 150)

        self.label = QLabel("Enter Desired Room Name:", self)
        self.label.move(20, 20)

        self.input = QLineEdit(self)
        self.input.move(20, 50)
        self.input.resize(260, 25)

        self.btn = QPushButton("Create", self)
        self.btn.move(100, 100)
        self.btn.clicked.connect(self.on_create)

    def on_create(self):
        room_name_raw = self.input.text().strip()
        if not room_name_raw:
            QMessageBox.warning(self, "Input Error", "Room name cannot be empty.")
            return

        req = ServerLobby_pb2.StartRoomRequest(name=room_name_raw)
        resp = self.lobby_stub.StartRoom(req)
        if resp.status == ServerLobby_pb2.Status.MATCH:
            QMessageBox.information(self, "Name Taken", f"Room '{room_name_raw}' is already taken.")
            return

        rooms = list(resp.rooms)
        addresses = list(resp.addresses)
        full_room_name = f"Room: {room_name_raw}"
        if full_room_name in rooms:
            idx = rooms.index(full_room_name)
            self.room_name = full_room_name
            self.room_address = addresses[idx]
        else:
            self.room_name = full_room_name
            self.room_address = None

        self.accept()


class RoomWindow(QMainWindow):
    def __init__(self, lobby_stub, username, room_name, room_address,
                 parent_lobby, client_address):
        super().__init__()
        self.lobby_stub = lobby_stub
        self.username = username
        self.room_name = room_name
        self.room_address = room_address
        self.parent_lobby = parent_lobby
        self.client_address = client_address
        self.room_stub = None

        self.init_room_connection()
        self.init_ui()
        self.refresh_room()

    def init_room_connection(self):
        channel = grpc.insecure_channel(self.room_address)
        try:
            grpc.channel_ready_future(channel).result(timeout=5)
            self.room_stub = ServerRoomMusic_pb2_grpc.ServerRoomMusicStub(channel)

            join_req = ServerRoomMusic_pb2.JoinRoomRequest(
                username=self.username,
                ClientAddress=self.client_address
            )
            join_resp = self.room_stub.JoinRoom(join_req)
            if join_resp.status != ServerRoomMusic_pb2.Status.SUCCESS:
                QMessageBox.critical(self, "Join Failed",
                                     "Room server refused our JoinRoom request.")
                return

            time_chan = grpc.insecure_channel(join_resp.RoomTimeAddress)
            grpc.channel_ready_future(time_chan).result(timeout=5)
            time_stub = ServerRoomTime_pb2_grpc.ServerRoomTimeStub(time_chan)

            offset_arr, delay_arr = TimeSync(time_stub,
                                             np.array([]),
                                             np.array([]),
                                             repeats=5)

            avg_delay = float(delay_arr.mean())
            sync_resp = self.room_stub.SyncStat(
                ServerRoomMusic_pb2.SyncStatRequest(delay=avg_delay)
            )
            if sync_resp.status != ServerRoomMusic_pb2.Status.SUCCESS:
                QMessageBox.critical(self, "Sync Failed",
                                     "Network too slow or room too full.")
                return

        except grpc.FutureTimeoutError:
            QMessageBox.critical(self, "Error",
                                 f"Cannot connect to room server at {self.room_address}")

    def init_ui(self):
        self.setWindowTitle(f"Room: {self.room_name}")
        self.setGeometry(150, 150, 900, 600)

        central = QWidget(self)
        self.setCentralWidget(central)
        hbox = QHBoxLayout()

        # Left: users list
        left_vbox = QVBoxLayout()
        left_vbox.addWidget(QLabel("Users In Room"))
        self.users_list = QListWidget()
        left_vbox.addWidget(self.users_list, stretch=1)
        self.leave_btn = QPushButton("Leave Room")
        self.leave_btn.clicked.connect(self.on_leave)
        left_vbox.addWidget(self.leave_btn)

        # Middle: playback controls
        middle_vbox = QVBoxLayout()
        middle_vbox.addStretch()
        # Play button
        self.play_btn = QPushButton("Play")
        self.play_btn.clicked.connect(self.on_play)
        middle_vbox.addWidget(self.play_btn)
        # Pause button
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.clicked.connect(self.on_pause)
        middle_vbox.addWidget(self.pause_btn)
        # Skip button
        self.skip_btn = QPushButton("Skip Song")
        self.skip_btn.clicked.connect(self.on_skip_song)
        middle_vbox.addWidget(self.skip_btn)

        # Right: queue
        right_vbox = QVBoxLayout()
        right_vbox.addWidget(QLabel("Song Queue"))
        self.queue_list = QListWidget()
        right_vbox.addWidget(self.queue_list, stretch=1)
        self.upload_btn = QPushButton("Upload Song mp3")
        self.upload_btn.clicked.connect(self.on_upload)
        right_vbox.addWidget(self.upload_btn)

        # separators
        line1 = QFrame(); line1.setFrameShape(QFrame.VLine); line1.setFrameShadow(QFrame.Sunken)
        line2 = QFrame(); line2.setFrameShape(QFrame.VLine); line2.setFrameShadow(QFrame.Sunken)

        hbox.addLayout(left_vbox)
        hbox.addWidget(line1)
        hbox.addLayout(middle_vbox)
        hbox.addWidget(line2)
        hbox.addLayout(right_vbox)
        central.setLayout(hbox)

        # start polling every 2 seconds
        self._poll_timer = QTimer(self)
        self._poll_timer.timeout.connect(self.refresh_room)
        self._poll_timer.start(2000)

    def on_play(self):
        QMessageBox.information(self, "Play",
                                "If we finished the code it would start playing the current song.")

    def on_pause(self):
        QMessageBox.information(self, "Pause",
                                "If we finished the code it would pause the current song.")

    def on_skip_song(self):
        QMessageBox.information(self, "Skip Song",
                                "If we finished the code it would skip to the next song in the queue.")

    def refresh_room(self):
        if not self.room_stub:
            return
        try:
            resp = self.room_stub.CurrentState(ServerRoomMusic_pb2.CurrentStateRequest())
            self.users_list.clear()
            for user in resp.usernames:
                self.users_list.addItem(user)
        except Exception as e:
            print("Error refreshing room state:", e)

    def on_leave(self):
        print(f"[ClientGUI] on_leave() called for user `{self.username}`")
        # 1) tell room
        if self.room_stub:
            try:
                print(f"[ClientGUI] ➡️ Calling room.LeaveRoom(username={self.username})")
                self.room_stub.LeaveRoom(
                    ServerRoomMusic_pb2.LeaveRoomRequest(username=self.username)
                )
            except Exception as e:
                print(f"[ClientGUI] ❌ room.LeaveRoom RPC failed:", e)
        # 2) tell lobby
        try:
            print(f"[ClientGUI] ➡️ Calling lobby.LeaveRoom(username={self.username}, roomname={self.room_name})")
            self.lobby_stub.LeaveRoom(
                ServerLobby_pb2.LeaveRoomRequest(
                    username=self.username,
                    roomname=self.room_name
                )
            )
        except Exception as e:
            print(f"[ClientGUI] ❌ lobby.LeaveRoom RPC failed:", e)
        # 3) UI teardown
        self._poll_timer.stop()
        self.close()
        self.parent_lobby.show()

    def on_upload(self):
        # Start the dialog in the user's Downloads folder:
        downloads_path = QStandardPaths.writableLocation(
            QStandardPaths.DownloadLocation
        )
        # Show only .mp3 files
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select MP3 to Upload",
            downloads_path,
            "MP3 Files (*.mp3);;All Files (*)"
        )
        if file_path:
            # For now we just show the path; later you'll actually upload it.
            QMessageBox.information(
                self,
                "File Selected",
                f"You chose:\n{file_path}"
            )
        else:
            # User cancelled
            pass


def run_gui(server_address):
    _client_ready_evt.wait()

    channel = grpc.insecure_channel(server_address)
    try:
        grpc.channel_ready_future(channel).result(timeout=5)
    except grpc.FutureTimeoutError:
        print(f"Failed to connect to lobby at {server_address}")
        sys.exit(1)

    lobby_stub = ServerLobby_pb2_grpc.ServerLobbyStub(channel)
    app = QApplication(sys.argv)
    login_win = LoginWindow(lobby_stub, client_address)
    login_win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python ClientGUI.py ServerHost:Port")
        sys.exit(1)

    t = threading.Thread(target=serve_grpc, daemon=True)
    t.start()

    run_gui(sys.argv[1])
