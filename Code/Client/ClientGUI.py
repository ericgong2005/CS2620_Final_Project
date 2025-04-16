#!/usr/bin/env python3
# ClientGUI.py

from concurrent import futures
import grpc
import sys
import threading
import time

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QLineEdit, QPushButton,
    QMessageBox, QDialog, QListWidget, QVBoxLayout, QHBoxLayout,
    QWidget, QFrame
)

from Client.ClientGRPC import Client_pb2, Client_pb2_grpc
from Server.ServerLobbyGRPC import ServerLobby_pb2, ServerLobby_pb2_grpc
from Server.ServerRoomGRPC import (
    ServerRoomMusic_pb2, ServerRoomMusic_pb2_grpc,
    ServerRoomTime_pb2, ServerRoomTime_pb2_grpc
)

class ClientServicer(Client_pb2_grpc.ClientServicer):
    def __init__(self):
        pass

    def CurrentState(self, request, context):
        pass

    def LoadSong(self, request, context):
        pass

    def StartSong(self, request, context):
        pass

    def StopSong(self, request, context):
        pass

def serve_grpc():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    Client_pb2_grpc.add_ClientServicer_to_server(ClientServicer(), server)
    port = server.add_insecure_port("localhost:0")
    server.start()
    print(f"gRPC client‑servicer listening on port {port}")
    server.wait_for_termination()

class LoginWindow(QMainWindow):
    def __init__(self, lobby_stub):
        super().__init__()
        self.lobby_stub = lobby_stub
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
            self.lobby_win = LobbyWindow(self.lobby_stub, username, login_window=self)
            self.lobby_win.show()

class LobbyWindow(QMainWindow):
    def __init__(self, lobby_stub, username, login_window):
        super().__init__()
        self.lobby_stub = lobby_stub
        self.username = username
        self.login_window = login_window
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
                parent_lobby=self
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
                parent_lobby=self
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

        self.list = QListWidget(self)
        try:
            resp = self.lobby_stub.GetRooms(ServerLobby_pb2.GetRoomsRequest())
        except grpc.RpcError as e:
            QMessageBox.critical(self, "RPC Error", f"Error retrieving rooms:\n{e}")
            self.reject()
            return

        self.rooms = list(resp.rooms)
        self.addresses = list(resp.addresses)
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

        # Build the protobuf lists into Python lists
        rooms = list(resp.rooms)
        addresses = list(resp.addresses)

        full_room_name = f"Room: {room_name_raw}"
        if full_room_name in rooms:
            idx = rooms.index(full_room_name)
            self.room_name = full_room_name
            self.room_address = addresses[idx]
        else:
            # Fallback if not found
            self.room_name = full_room_name
            self.room_address = None

        self.accept()

class RoomWindow(QMainWindow):
    def __init__(self, lobby_stub, username, room_name, room_address, parent_lobby):
        super().__init__()
        self.lobby_stub = lobby_stub
        self.username = username
        self.room_name = room_name
        self.room_address = room_address
        self.parent_lobby = parent_lobby
        self.room_stub = None
        self.init_room_connection()
        self.init_ui()
        self.refresh_room()

    def init_room_connection(self):
        channel = grpc.insecure_channel(self.room_address)
        try:
            grpc.channel_ready_future(channel).result(timeout=5)
            self.room_stub = ServerRoomMusic_pb2_grpc.ServerRoomMusicStub(channel)
        except grpc.FutureTimeoutError:
            QMessageBox.critical(self, "Error", f"Cannot connect to room server at {self.room_address}")

    def init_ui(self):
        self.setWindowTitle(f"Room: {self.room_name}")
        self.setGeometry(150, 150, 900, 600)
        central = QWidget(self)
        self.setCentralWidget(central)
        hbox = QHBoxLayout()

        left_vbox = QVBoxLayout()
        left_vbox.addWidget(QLabel("Users In Room"))
        self.users_list = QListWidget()
        left_vbox.addWidget(self.users_list, stretch=1)
        self.leave_btn = QPushButton("Leave Room")
        self.leave_btn.clicked.connect(self.on_leave)
        left_vbox.addWidget(self.leave_btn)

        middle_vbox = QVBoxLayout()
        middle_vbox.addStretch()

        right_vbox = QVBoxLayout()
        right_vbox.addWidget(QLabel("Song Queue"))
        self.queue_list = QListWidget()
        right_vbox.addWidget(self.queue_list, stretch=1)
        self.upload_btn = QPushButton("Upload Song mp3")
        self.upload_btn.clicked.connect(self.on_upload)
        right_vbox.addWidget(self.upload_btn)

        line1 = QFrame(); line1.setFrameShape(QFrame.VLine); line1.setFrameShadow(QFrame.Sunken)
        line2 = QFrame(); line2.setFrameShape(QFrame.VLine); line2.setFrameShadow(QFrame.Sunken)

        hbox.addLayout(left_vbox)
        hbox.addWidget(line1)
        hbox.addLayout(middle_vbox)
        hbox.addWidget(line2)
        hbox.addLayout(right_vbox)
        central.setLayout(hbox)

        self.users_list.addItem(self.username)

    def refresh_room(self):
        if self.room_stub:
            try:
                resp = self.room_stub.CurrentState(ServerRoomMusic_pb2.CurrentStateRequest())
                if hasattr(resp, "usernames"):
                    self.users_list.clear()
                    for user in resp.usernames:
                        self.users_list.addItem(user)
            except Exception as e:
                print("Error refreshing room state:", e)

    def on_leave(self):
        req = ServerLobby_pb2.LeaveRoomRequest(username=self.username, roomname=self.room_name)
        self.lobby_stub.LeaveRoom(req)
        self.close()
        self.parent_lobby.show()

    def on_upload(self):
        QMessageBox.information(self, "Upload", "If this were coded, it would upload a song")

def run_gui(server_address):
    channel = grpc.insecure_channel(server_address)
    try:
        grpc.channel_ready_future(channel).result(timeout=5)
    except grpc.FutureTimeoutError:
        print(f"Failed to connect to lobby at {server_address}")
        sys.exit(1)
    lobby_stub = ServerLobby_pb2_grpc.ServerLobbyStub(channel)
    app = QApplication(sys.argv)
    login_win = LoginWindow(lobby_stub)
    login_win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python ClientGUI.py ServerHost:Port")
        sys.exit(1)
    server_address = sys.argv[1]
    t = threading.Thread(target=serve_grpc, daemon=True)
    t.start()
    run_gui(server_address)
