from concurrent import futures
import grpc
import sys
import threading

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QLineEdit,
    QPushButton, QMessageBox, QDialog, QListWidget,
    QVBoxLayout, QHBoxLayout
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

# gRPC server in background thread
def serve_grpc():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    Client_pb2_grpc.add_ClientServicer_to_server(ClientServicer(), server)
    port = server.add_insecure_port("localhost:0")
    server.start()
    print(f"gRPC client‑servicer listening on port {port}")
    server.wait_for_termination()

# Login Window
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
            # Success: open LobbyWindow
            self.hide()
            self.lobby_window = LobbyWindow(self.lobby_stub, username, parent=self)
            self.lobby_window.show()

# Lobby Window
class LobbyWindow(QMainWindow):
    def __init__(self, lobby_stub, username, parent=None):
        super().__init__(parent)
        self.lobby_stub = lobby_stub
        self.username = username
        self.login_window = parent
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"Welcome {self.username}")
        self.setGeometry(100, 100, 400, 300)

        # Create Room button
        self.create_btn = QPushButton("Create Room", self)
        self.create_btn.move(150, 80)
        self.create_btn.clicked.connect(self.on_create_room)

        # Join Room button
        self.join_btn = QPushButton("Join Room", self)
        self.join_btn.move(150, 130)
        self.join_btn.clicked.connect(self.on_join_room)

        # Exit Lobby button
        self.exit_btn = QPushButton("Exit Lobby", self)
        self.exit_btn.move(150, 180)
        self.exit_btn.clicked.connect(self.on_exit_lobby)

    def on_exit_lobby(self):
        # Call LeaveLobby RPC
        try:
            req = ServerLobby_pb2.LeaveLobbyRequest(username=self.username)
            self.lobby_stub.LeaveLobby(req)
        except grpc.RpcError as e:
            print(f"Error leaving lobby: {e}")
        # Return to login screen
        self.login_window.show()
        self.close()

    def on_create_room(self):
        dialog = CreateRoomDialog(self.lobby_stub, self.username, parent=self)
        dialog.exec_()

    def on_join_room(self):
        dialog = JoinRoomDialog(self.lobby_stub, self.username, parent=self)
        dialog.exec_()

# Create Room Dialog
class CreateRoomDialog(QDialog):
    def __init__(self, lobby_stub, username, parent=None):
        super().__init__(parent)
        self.lobby_stub = lobby_stub
        self.username = username
        self.lobby_window = parent
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Create Room")
        self.resize(300, 150)

        layout = QVBoxLayout(self)

        label = QLabel("Enter Desired Room Name:", self)
        layout.addWidget(label)

        self.room_input = QLineEdit(self)
        layout.addWidget(self.room_input)

        btn_layout = QHBoxLayout()
        enter_btn = QPushButton("Enter", self)
        enter_btn.clicked.connect(self.attempt_create)
        btn_layout.addWidget(enter_btn)

        cancel_btn = QPushButton("Cancel", self)
        cancel_btn.clicked.connect(self.close)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

    def attempt_create(self):
        room_name = self.room_input.text().strip()
        if not room_name:
            QMessageBox.warning(self, "Input Error", "Room name cannot be empty.")
            return
        try:
            req = ServerLobby_pb2.StartRoomRequest(name=room_name)
            resp = self.lobby_stub.StartRoom(req)
        except grpc.RpcError as e:
            QMessageBox.critical(self, "RPC Error", f"Could not reach lobby server:\n{e}")
            return

        if resp.status == ServerLobby_pb2.Status.MATCH:
            QMessageBox.information(self, "Name Taken",
                                    f"Room '{room_name}' is already taken.")
        else:
            # Success: open RoomWindow
            self.lobby_window.hide()
            self.close()
            self.room_window = RoomWindow(self.lobby_stub, self.username, room_name, parent=self.lobby_window)
            self.room_window.show()

# Room Window
class RoomWindow(QMainWindow):
    def __init__(self, lobby_stub, username, room_name, parent=None):
        super().__init__(parent)
        self.lobby_stub = lobby_stub
        self.username = username
        self.room_name = room_name
        self.lobby_window = parent
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"Room: {self.room_name}")
        self.setGeometry(100, 100, 600, 400)

        leave_btn = QPushButton("Leave Room", self)
        leave_btn.move(10, 350)
        leave_btn.clicked.connect(self.on_leave_room)

    def on_leave_room(self):
        try:
            req = ServerLobby_pb2.LeaveRoomRequest(username=self.username, roomname=self.room_name)
            self.lobby_stub.LeaveRoom(req)
        except grpc.RpcError as e:
            print(f"Error leaving room: {e}")
        # Return to lobby window
        self.lobby_window.show()
        self.close()

# Join Room Dialog
class JoinRoomDialog(QDialog):
    def __init__(self, lobby_stub, username, parent=None):
        super().__init__(parent)
        self.lobby_stub = lobby_stub
        self.username = username
        self.lobby_window = parent
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Join Room")
        self.resize(400, 300)

        layout = QVBoxLayout(self)

        label = QLabel("Enter Room Code:", self)
        layout.addWidget(label)

        self.room_list = QListWidget(self)
        # Fetch rooms
        try:
            resp = self.lobby_stub.GetRooms(ServerLobby_pb2.GetRoomsRequest())
            for room in resp.rooms:
                self.room_list.addItem(room)
        except grpc.RpcError as e:
            QMessageBox.critical(self, "RPC Error", f"Could not fetch rooms:\n{e}")
        layout.addWidget(self.room_list)

        self.room_input = QLineEdit(self)
        layout.addWidget(self.room_input)

        btn_layout = QHBoxLayout()
        enter_btn = QPushButton("Enter", self)
        enter_btn.clicked.connect(self.attempt_join)
        btn_layout.addWidget(enter_btn)

        cancel_btn = QPushButton("Cancel", self)
        cancel_btn.clicked.connect(self.close)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

    def attempt_join(self):
        room_name = self.room_input.text().strip() or self.room_list.currentItem().text() if self.room_list.currentItem() else None
        if not room_name:
            QMessageBox.warning(self, "Input Error", "Please select or enter a room name.")
            return
        try:
            req = ServerLobby_pb2.JoinRoomRequest(username=self.username, roomname=room_name)
            resp = self.lobby_stub.JoinRoom(req)
        except grpc.RpcError as e:
            QMessageBox.critical(self, "RPC Error", f"Could not reach lobby server:\n{e}")
            return

        if resp.status == ServerLobby_pb2.Status.ERROR:
            QMessageBox.information(self, "Join Failed",
                                    f"Room '{room_name}' does not exist.")
        else:
            QMessageBox.information(self, "Join Success",
                                    f"Joined room '{room_name}' (placeholder).")
            self.close()

# Main GUI runner
def run_gui(server_address):
    channel = grpc.insecure_channel(server_address)
    try:
        grpc.channel_ready_future(channel).result(timeout=5)
    except grpc.FutureTimeoutError:
        print(f"Failed to connect to lobby at {server_address}")
        sys.exit(1)
    lobby_stub = ServerLobby_pb2_grpc.ServerLobbyStub(channel)

    app = QApplication(sys.argv)
    login = LoginWindow(lobby_stub)
    login.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python ClientGUI.py ServerHost:Port")
        sys.exit(1)
    server_address = sys.argv[1]

    # start the gRPC servicer in a daemon thread
    t = threading.Thread(target=serve_grpc, daemon=True)
    t.start()

    # then launch the login GUI
    run_gui(server_address)
