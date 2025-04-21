import signal
import atexit
import sys
import os
import socket
import threading
import time

from concurrent import futures
import grpc

from Client.ClientPlayer import ClientPlayerStart

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
from Server.ServerConstants import MAX_GRPC_OPTION


#Shutdown Handler
def TerminationHandler(TerminateCommand):
    def _handle_signal(signum, frame):
        TerminateCommand.set()
        sys.exit(0)
    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    atexit.register(TerminateCommand.set)

    def _excepthook(exc_type, exc_value, exc_tb):
        TerminateCommand.set()
        sys.__excepthook__(exc_type, exc_value, exc_tb)
    sys.excepthook = _excepthook

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
                ServerLobby_pb2.JoinLobbyRequest(username=username, MusicPlayerAddress=self.client_address)
            )
        except grpc.RpcError as e:
            QMessageBox.critical(self, "RPC Error", f"Could not reach lobby:\n{e}")
            return
        if resp.status == ServerLobby_pb2.Status.MATCH:
            QMessageBox.information(self, "Username Taken",
                                    f"Username '{username}' taken.")
        else:
            # QMessageBox.information(self, "Username Available",
            #                         f"Username '{username}' available.")
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
            self.list.addItem(r[6:])
        layout.addWidget(self.list)
        self.input = QLineEdit()
        layout.addWidget(self.input)
        btns = QHBoxLayout()
        join = QPushButton("Join"); join.clicked.connect(self.on_join)
        cancel = QPushButton("Cancel"); cancel.clicked.connect(self.reject)
        btns.addWidget(join); btns.addWidget(cancel)
        layout.addLayout(btns)
        self.setLayout(layout)

    def on_join(self):
        roomname = "Room: " + self.input.text().strip()
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
        self.input = QLineEdit(self); self.input.move(20, 50); self.input.resize(260, 25)
        btn = QPushButton("Create", self); btn.move(100, 100); btn.clicked.connect(self.on_create)

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
        self.lobby_stub     = lobby_stub
        self.username       = username
        self.room_name      = room_name
        self.room_address   = room_address
        self.parent_lobby   = parent_lobby
        self.client_address = client_address
        self.room_stub      = None

        self.init_room_connection()
        self.init_ui()
        self.refresh_room()

    def init_room_connection(self):
        channel = grpc.insecure_channel(self.room_address, options = MAX_GRPC_OPTION)
        self.room_stub = ServerRoomMusic_pb2_grpc.ServerRoomMusicStub(channel)
        grpc.channel_ready_future(channel).result(timeout=1)
        print(f"Client connected to {self.room_name} at {self.room_address}")

        join = self.room_stub.JoinRoom(
            ServerRoomMusic_pb2.JoinRoomRequest(
                username=self.username,
                ClientMusicAddress=self.client_address
            )
        )
        if not join.success:
            QMessageBox.critical(self, "Join Failed", "Refused by server.")
            return

    def init_ui(self):
        self.setWindowTitle(self.room_name)
        self.setGeometry(150, 150, 900, 600)
        cen = QWidget(self); self.setCentralWidget(cen)
        hbox = QHBoxLayout()
        # Left panel
        lv = QVBoxLayout()
        lv.addWidget(QLabel("Users In Room"))
        self.users_list = QListWidget(); lv.addWidget(self.users_list, stretch=1)
        leave = QPushButton("Leave Room"); leave.clicked.connect(self.on_leave); lv.addWidget(leave)
        # Middle panel
        mv = QVBoxLayout(); mv.addStretch()
        play = QPushButton("Play"); play.clicked.connect(self.on_play); mv.addWidget(play)
        pause= QPushButton("Pause"); pause.clicked.connect(self.on_pause); mv.addWidget(pause)
        skip = QPushButton("Skip Song"); skip.clicked.connect(self.on_skip_song); mv.addWidget(skip)
        # Right panel
        rv = QVBoxLayout()
        rv.addWidget(QLabel("Song Queue"))
        self.queue_list = QListWidget(); rv.addWidget(self.queue_list, stretch=1)
        upl = QPushButton("Upload Song mp3"); upl.clicked.connect(self.on_upload); rv.addWidget(upl)
        # separators
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
            if not resp.success:
                QMessageBox.information(self, "Sorry!", f"Can't Start Song Right Now!")
        except grpc.RpcError as e:
            QMessageBox.critical(self, "Error", f"StartSong RPC failed:\n{e}")

    def on_pause(self):
        try:
            resp = self.room_stub.StopSong(ServerRoomMusic_pb2.StopSongRequest())
            if not resp.success:
                QMessageBox.information(self, "Sorry!", f"Can't Stop Song Right Now!")
        except grpc.RpcError as e:
            QMessageBox.critical(self, "Error", f"PauseSong RPC failed:\n{e}")

    def on_skip_song(self):
        try:
            resp = self.room_stub.SkipSong(ServerRoomMusic_pb2.SkipSongRequest())
            if not resp.success:
                QMessageBox.information(self, "Sorry!", f"Can't Skip Song Right Now!")
        except grpc.RpcError as e:
            QMessageBox.critical(self, "Error", f"DeleteSong RPC failed:\n{e}")

    def on_upload(self):
        dl = QStandardPaths.writableLocation(QStandardPaths.DownloadLocation)
        path, _ = QFileDialog.getOpenFileName(self, "Select MP3", dl, "MP3 Files (*.mp3)")
        if not path: return
        data = open(path, "rb").read()
        try:
            name = os.path.basename(path)
            resp = self.room_stub.AddSong(
                ServerRoomMusic_pb2.AddSongRequest(
                    name=name,
                    AudioData=data
                )
            )
            if not resp.success:
                raise grpc.RpcError(f"Can't Add Song Right Now!")
            QMessageBox.information(self, "Uploaded:", name)
        except grpc.RpcError as e:
            QMessageBox.critical(self, "Error", f"AddSong RPC failed:\n{e}")

    def refresh_room(self):
        if not self.room_stub:
            return
        try:
            resp = self.room_stub.CurrentState(ServerRoomMusic_pb2.CurrentStateRequest())

            # Users
            self.users_list.clear()
            for u in resp.usernames:
                self.users_list.addItem(u)

            # Queue
            self.queue_list.clear()
            for song_name in resp.MusicList:
                i = song_name.find(".mp3")
                self.queue_list.addItem(song_name[:i])

        except Exception as e:
            print("Error refreshing room state:", e)

    def on_leave(self):
        self.lobby_stub.LeaveRoom(ServerLobby_pb2.LeaveRoomRequest(
                username=self.username, roomname=self.room_name
            ))
        self.room_stub.LeaveRoom(ServerRoomMusic_pb2.LeaveRoomRequest(username=self.username))
        self.timer.stop()
        self.close()
        self.parent_lobby.show()

def run_gui(server_address, TerminateCommand):
    while True:
        try:
            channel = grpc.insecure_channel(server_address)
            lobby = ServerLobby_pb2_grpc.ServerLobbyStub(channel)
            grpc.channel_ready_future(channel).result(timeout=1)
            print(f"Client connected to Lobby at {server_address}")
            break
        except grpc.FutureTimeoutError:
            time.sleep(0.5)
            print("Waiting to connect to Lobby")

    # Get hostname
    hostname = socket.gethostbyname(socket.gethostname())

    # Set up MusicPlayer
    ClientPlayer = grpc.server(futures.ThreadPoolExecutor(max_workers=2),options = MAX_GRPC_OPTION)
    ClientPlayerAddress =  hostname + ":" + str(ClientPlayer.add_insecure_port(f"{hostname}:0"))

    Thread = threading.Thread(target=ClientPlayerStart, args=(ClientPlayer, ClientPlayerAddress, TerminateCommand,))
    Thread.start()

    app = QApplication(sys.argv)
    app.aboutToQuit.connect(TerminateCommand.set)
    wnd = LoginWindow(lobby, ClientPlayerAddress)
    wnd.show()

    try:
        return app.exec_()
    finally:
        TerminateCommand.set()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python ClientGUI.py ServerHost:Port")
        sys.exit(1)
    
    TerminateCommand = threading.Event()
    TerminationHandler(TerminateCommand)
    try:
        run_gui(sys.argv[1], TerminateCommand)
    finally:
        TerminateCommand.set()
    sys.exit(0)