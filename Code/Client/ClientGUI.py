#!/usr/bin/env python3
# ClientGUI.py

import sys
import os
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
from PyQt5.QtCore import QTimer, QStandardPaths

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
_ready = threading.Event()

# -------------------------------------------------------------------
# TimeSync helper (copied from terminal client)
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
# Client‐side gRPC server (for LoadSong, StartSong, StopSong)
# -------------------------------------------------------------------
class ClientServicer(Client_pb2_grpc.ClientServicer):
    def CurrentState(self, request, context):
        return Client_pb2.CurrentStateResponse(response="OK")

    def LoadSong(self, request, context):
        # server sending us new audio bytes
        print(f"[Client] LoadSong: {request.song_name} ({len(request.audio_data)} bytes)")
        # you could save to file here
        return Client_pb2.LoadSongResponse(success=True)

    def StartSong(self, request, context):
        print(f"[Client] StartSong at {request.start}, offset {request.offset}")
        # schedule playback...
        return Client_pb2.StartSongResponse(success=True)

    def StopSong(self, request, context):
        print(f"[Client] StopSong at {request.stop}")
        # stop playback...
        return Client_pb2.StopSongResponse(success=True)

def serve_grpc():
    global client_servicer_port, client_address
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    Client_pb2_grpc.add_ClientServicer_to_server(ClientServicer(), server)
    client_servicer_port = server.add_insecure_port("0.0.0.0:0")
    server.start()

    host = socket.gethostbyname(socket.gethostname())
    client_address = f"{host}:{client_servicer_port}"
    print(f"[Client gRPC] listening on {client_address}")

    _ready.set()
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

        QLabel("Welcome", self).move(170, 20)
        QLabel("Enter Username:", self).move(50, 80)

        self.username_input = QLineEdit(self)
        self.username_input.move(160, 75)
        self.username_input.resize(180, 25)

        btn = QPushButton("Submit", self)
        btn.move(160, 120)
        btn.clicked.connect(self.on_submit)

    def on_submit(self):
        username = self.username_input.text().strip()
        if not username:
            QMessageBox.warning(self, "Input Error", "Username cannot be empty.")
            return
        try:
            resp = self.lobby_stub.JoinLobby(
                ServerLobby_pb2.JoinLobbyRequest(username=username)
            )
        except grpc.RpcError as e:
            QMessageBox.critical(self, "RPC Error", f"Could not reach lobby:\n{e}")
            return
        if resp.status == ServerLobby_pb2.Status.MATCH:
            QMessageBox.information(self, "Username Taken",
                                    f"Username '{username}' taken.")
        else:
            QMessageBox.information(self, "Username Available",
                                    f"Username '{username}' available.")
            self.hide()
            self.lobby_win = LobbyWindow(
                self.lobby_stub, username,
                login_window=self,
                client_address=self.client_address
            )
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

        QLabel(f"Welcome {self.username}", self).move(150, 20)

        create = QPushButton("Create Room", self)
        create.move(50, 80)
        create.clicked.connect(self.on_create)

        join = QPushButton("Join Room", self)
        join.move(150, 80)
        join.clicked.connect(self.on_join)

        exit_btn = QPushButton("Exit Lobby", self)
        exit_btn.move(275, 80)
        exit_btn.clicked.connect(self.on_exit)

    def on_exit(self):
        self.lobby_stub.LeaveLobby(
            ServerLobby_pb2.LeaveLobbyRequest(username=self.username)
        )
        self.close()
        self.login_window.show()

    def on_join(self):
        dlg = JoinRoomDialog(self.lobby_stub, self, self.username)
        if dlg.exec_() == QDialog.Accepted:
            self.hide()
            self.room_win = RoomWindow(
                self.lobby_stub, self.username,
                dlg.room_name, dlg.room_address,
                parent_lobby=self,
                client_address=self.client_address
            )
            self.room_win.show()

    def on_create(self):
        dlg = CreateRoomDialog(self.lobby_stub, self, self.username)
        if dlg.exec_() == QDialog.Accepted:
            self.hide()
            self.room_win = RoomWindow(
                self.lobby_stub, self.username,
                dlg.room_name, dlg.room_address,
                parent_lobby=self,
                client_address=self.client_address
            )
            self.room_win.show()

class JoinRoomDialog(QDialog):
    def __init__(self, lobby_stub, parent, username):
        super().__init__(parent)
        self.lobby_stub = lobby_stub
        self.username = username
        self.room_name = None
        self.room_address = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Join Room")
        self.setGeometry(200, 200, 400, 300)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Enter Room Code"))
        try:
            resp = self.lobby_stub.GetRooms(ServerLobby_pb2.GetRoomsRequest())
        except grpc.RpcError as e:
            QMessageBox.critical(self, "RPC Error", str(e))
            self.reject()
            return
        rooms = list(resp.rooms)
        addrs = list(resp.addresses)
        self.list = QListWidget()
        for r in rooms:
            self.list.addItem(r)
        layout.addWidget(self.list)
        self.input = QLineEdit()
        layout.addWidget(self.input)
        btns = QHBoxLayout()
        join = QPushButton("Join")
        join.clicked.connect(self.on_join)
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        btns.addWidget(join); btns.addWidget(cancel)
        layout.addLayout(btns)
        self.setLayout(layout)

    def on_join(self):
        roomname = self.input.text().strip()
        if not roomname:
            QMessageBox.warning(self, "Input Error", "Room name cannot be empty.")
            return
        resp = self.lobby_stub.JoinRoom(
            ServerLobby_pb2.JoinRoomRequest(username=self.username, roomname=roomname)
        )
        if resp.status != ServerLobby_pb2.Status.SUCCESS:
            QMessageBox.information(self, "Error", "Room does not exist.")
            return
        listing = self.lobby_stub.GetRooms(ServerLobby_pb2.GetRoomsRequest())
        rooms = list(listing.rooms)
        addrs = list(listing.addresses)
        idx = rooms.index(roomname)
        self.room_name = roomname
        self.room_address = addrs[idx]
        self.accept()

class CreateRoomDialog(QDialog):
    def __init__(self, lobby_stub, parent, username):
        super().__init__(parent)
        self.lobby_stub = lobby_stub
        self.username = username
        self.room_name = None
        self.room_address = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Create Room")
        self.setGeometry(200, 200, 300, 150)
        QLabel("Enter Desired Room Name:", self).move(20, 20)
        self.input = QLineEdit(self)
        self.input.move(20, 50); self.input.resize(260, 25)
        btn = QPushButton("Create", self)
        btn.move(100, 100); btn.clicked.connect(self.on_create)

    def on_create(self):
        base = self.input.text().strip()
        resp = self.lobby_stub.StartRoom(
            ServerLobby_pb2.StartRoomRequest(name=base)
        )
        if resp.status == ServerLobby_pb2.Status.MATCH:
            QMessageBox.information(self, "Name Taken", f"'{base}' in use.")
            return
        rooms = list(resp.rooms)
        addrs = list(resp.addresses)
        target = f"Room: {base}"
        for i, nm in enumerate(rooms):
            if nm == target:
                self.room_name = nm
                self.room_address = addrs[i]
                self.accept()
                return
        QMessageBox.critical(self, "Error", f"'{target}' not found.")

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
        _ = _ready.wait()  # ensure client stub is up
        chan = grpc.insecure_channel(self.room_address)
        grpc.channel_ready_future(chan).result(timeout=5)
        self.room_stub = ServerRoomMusic_pb2_grpc.ServerRoomMusicStub(chan)

        join = self.room_stub.JoinRoom(
            ServerRoomMusic_pb2.JoinRoomRequest(
                username=self.username,
                ClientAddress=self.client_address
            )
        )
        if join.status != ServerRoomMusic_pb2.Status.SUCCESS:
            QMessageBox.critical(self, "Join Failed", "Refused by server.")
            return

        tchan = grpc.insecure_channel(join.RoomTimeAddress)
        grpc.channel_ready_future(tchan).result(timeout=5)
        offsets, delays = TimeSync(
            ServerRoomTime_pb2_grpc.ServerRoomTimeStub(tchan),
            np.array([]), np.array([]), repeats=5
        )
        self.room_stub.SyncStat(
            ServerRoomMusic_pb2.SyncStatRequest(
                username=self.username,
                delay=float(delays.mean())
            )
        )

    def init_ui(self):
        self.setWindowTitle(f"Room: {self.room_name}")
        self.setGeometry(150, 150, 900, 600)
        cen = QWidget(self); self.setCentralWidget(cen)
        hbox = QHBoxLayout()

        # Left: users
        lv = QVBoxLayout()
        lv.addWidget(QLabel("Users In Room"))
        self.users_list = QListWidget(); lv.addWidget(self.users_list, stretch=1)
        btn = QPushButton("Leave Room"); btn.clicked.connect(self.on_leave); lv.addWidget(btn)

        # Middle: controls
        mv = QVBoxLayout(); mv.addStretch()
        pbtn = QPushButton("Play"); pbtn.clicked.connect(self.on_play); mv.addWidget(pbtn)
        sbt = QPushButton("Pause"); sbt.clicked.connect(self.on_pause); mv.addWidget(sbt)
        skp = QPushButton("Skip Song"); skp.clicked.connect(self.on_skip_song); mv.addWidget(skp)

        # Right: queue + upload
        rv = QVBoxLayout()
        rv.addWidget(QLabel("Song Queue"))
        self.queue_list = QListWidget(); rv.addWidget(self.queue_list, stretch=1)
        upl = QPushButton("Upload Song mp3"); upl.clicked.connect(self.on_upload); rv.addWidget(upl)

        line1 = QFrame(); line1.setFrameShape(QFrame.VLine); line1.setFrameShadow(QFrame.Sunken)
        line2 = QFrame(); line2.setFrameShape(QFrame.VLine); line2.setFrameShadow(QFrame.Sunken)

        hbox.addLayout(lv); hbox.addWidget(line1)
        hbox.addLayout(mv); hbox.addWidget(line2)
        hbox.addLayout(rv)
        cen.setLayout(hbox)

        self.timer = QTimer(self); self.timer.timeout.connect(self.refresh_room); self.timer.start(2000)

    def on_play(self):
        try:
            resp = self.room_stub.StartSong(ServerRoomMusic_pb2.StartSongRequest())
            if resp.status != ServerRoomMusic_pb2.Status.SUCCESS:
                raise grpc.RpcError(f"StartSong returned {resp.status}")
        except grpc.RpcError as e:
            QMessageBox.critical(self, "Error", f"StartSong RPC failed:\n{e}")

    def on_pause(self):
        try:
            resp = self.room_stub.PauseSong(ServerRoomMusic_pb2.PauseSongRequest())
            if resp.status != ServerRoomMusic_pb2.Status.SUCCESS:
                raise grpc.RpcError(f"PauseSong returned {resp.status}")
        except grpc.RpcError as e:
            QMessageBox.critical(self, "Error", f"PauseSong RPC failed:\n{e}")

    def on_skip_song(self):
        try:
            resp = self.room_stub.DeleteSong(ServerRoomMusic_pb2.DeleteSongRequest())
            if resp.status != ServerRoomMusic_pb2.Status.SUCCESS:
                raise grpc.RpcError(f"DeleteSong returned {resp.status}")
        except grpc.RpcError as e:
            QMessageBox.critical(self, "Error", f"DeleteSong RPC failed:\n{e}")

    def on_upload(self):
        dl = QStandardPaths.writableLocation(QStandardPaths.DownloadLocation)
        path, _ = QFileDialog.getOpenFileName(self, "Select MP3", dl, "MP3 Files (*.mp3)")
        if not path: return
        data = open(path, "rb").read()
        try:
            resp = self.room_stub.AddSong(
                ServerRoomMusic_pb2.AddSongRequest(
                    filename=os.path.basename(path),
                    audio_data=data
                )
            )
            if resp.status != ServerRoomMusic_pb2.Status.SUCCESS:
                raise grpc.RpcError(f"AddSong returned {resp.status}")
            QMessageBox.information(self, "Uploaded", f"Position {resp.queue_position}")
        except grpc.RpcError as e:
            QMessageBox.critical(self, "Error", f"AddSong RPC failed:\n{e}")

    def refresh_room(self):
        if not self.room_stub:
            return
        try:
            resp = self.room_stub.CurrentState(ServerRoomMusic_pb2.CurrentStateRequest())
            self.users_list.clear()
            for u in resp.usernames:
                self.users_list.addItem(u)
        except Exception as e:
            print("Error refreshing room:", e)

    def on_leave(self):
        try:
            self.room_stub.LeaveRoom(ServerRoomMusic_pb2.LeaveRoomRequest(username=self.username))
        except:
            pass
        try:
            self.lobby_stub.LeaveRoom(ServerLobby_pb2.LeaveRoomRequest(
                username=self.username, roomname=self.room_name
            ))
        except:
            pass
        self.timer.stop()
        self.close()
        self.parent_lobby.show()

def run_gui(server_address):
    _ = _ready.wait()
    chan = grpc.insecure_channel(server_address)
    grpc.channel_ready_future(chan).result(timeout=5)
    lobby = ServerLobby_pb2_grpc.ServerLobbyStub(chan)

    app = QApplication(sys.argv)
    wnd = LoginWindow(lobby, client_address)
    wnd.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python ClientGUI.py ServerHost:Port")
        sys.exit(1)
    threading.Thread(target=serve_grpc, daemon=True).start()
    run_gui(sys.argv[1])
