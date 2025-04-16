from concurrent import futures
import grpc
import sys
import threading

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel,
    QLineEdit, QPushButton, QMessageBox
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

# gRPC server for client callbacks (if needed)
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

        # Welcome label
        self.welcome_label = QLabel("Welcome", self)
        self.welcome_label.move(170, 20)

        # "Enter Username:" label
        self.username_label = QLabel("Enter Username:", self)
        self.username_label.move(50, 80)

        # Text box for username
        self.username_input = QLineEdit(self)
        self.username_input.move(160, 75)
        self.username_input.resize(180, 25)

        # Submit button
        self.submit_btn = QPushButton("Submit", self)
        self.submit_btn.move(160, 120)
        self.submit_btn.clicked.connect(self.on_submit)

    def on_submit(self):
        username = self.username_input.text().strip()
        if not username:
            QMessageBox.warning(self, "Input Error", "Username cannot be empty.")
            return

        # Call the JoinLobby RPC
        try:
            req = ServerLobby_pb2.JoinLobbyRequest(username=username)
            resp = self.lobby_stub.JoinLobby(req)
        except grpc.RpcError as e:
            QMessageBox.critical(self, "RPC Error", f"Could not reach lobby server:\n{e}")
            return

        # Check response status
        if resp.status == ServerLobby_pb2.Status.MATCH:
            QMessageBox.information(self, "Username Taken",
                                    f"Username '{username}' is already taken.")
        else:
            # Proceed to lobby window
            self.lobby_window = LobbyWindow(self.lobby_stub, username)
            self.lobby_window.show()
            self.hide()

class LobbyWindow(QMainWindow):
    def __init__(self, lobby_stub, username):
        super().__init__()
        self.lobby_stub = lobby_stub
        self.username = username
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Lobby")
        self.setGeometry(100, 100, 400, 250)

        # Welcome <username> label
        self.welcome_label = QLabel(f"Welcome {self.username}", self)
        self.welcome_label.move(150, 20)

        # Create Room button
        self.create_btn = QPushButton("Create Room", self)
        self.create_btn.move(150, 70)
        self.create_btn.clicked.connect(self.on_create_room)

        # Join Room button
        self.join_btn = QPushButton("Join Room", self)
        self.join_btn.move(150, 110)
        self.join_btn.clicked.connect(self.on_join_room)

        # Exit Lobby button
        self.exit_btn = QPushButton("Exit Lobby", self)
        self.exit_btn.move(150, 150)
        self.exit_btn.clicked.connect(self.on_exit_lobby)

    def on_create_room(self):
        QMessageBox.information(self, "Create Room",
                                "If this code was implemented we would have created the room.")

    def on_join_room(self):
        QMessageBox.information(self, "Join Room",
                                "If this code was implemented we would have joined a room.")

    def on_exit_lobby(self):
        # Call LeaveLobby RPC
        try:
            req = ServerLobby_pb2.LeaveLobbyRequest(username=self.username)
            self.lobby_stub.LeaveLobby(req)
        except grpc.RpcError as e:
            QMessageBox.critical(self, "RPC Error", f"Could not reach lobby server to leave:\n{e}")
        # Return to login screen
        self.login_window = LoginWindow(self.lobby_stub)
        self.login_window.show()
        self.close()

def run_gui(server_address):
    # Set up gRPC channel and lobby stub
    channel = grpc.insecure_channel(server_address)
    try:
        grpc.channel_ready_future(channel).result(timeout=5)
    except grpc.FutureTimeoutError:
        print(f"Failed to connect to lobby at {server_address}")
        sys.exit(1)
    lobby_stub = ServerLobby_pb2_grpc.ServerLobbyStub(channel)

    # Launch the Qt application
    app = QApplication(sys.argv)
    window = LoginWindow(lobby_stub)
    window.show()
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