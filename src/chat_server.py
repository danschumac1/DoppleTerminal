# chat_server.py
import socket
import selectors
import json
from utils.constants import BLANK_GS, BLANK_PS
from game import play_game
from utils.states import ScreenState

class ChatServer:
    def __init__(self, host="127.0.0.1", port=65432):
        self.host = host
        self.port = port
        self.sel = selectors.DefaultSelector()
        self.clients = {}
        self.gs = BLANK_GS
        self.ps_map = {}  # key: code_name, value: PlayerState
        self.ss = ScreenState.PLAY

    def accept_connection(self, sock):
        conn, addr = sock.accept()
        print(f"New connection from {addr}")
        conn.setblocking(False)
        self.sel.register(conn, selectors.EVENT_READ)
        self.clients[conn] = addr

    def handle_client(self, sock):
        try:
            data = sock.recv(4096)
            if data:
                msg = json.loads(data.decode())
                if msg["type"] == "player_input":
                    code_name = msg["player_code_name"]
                    user_msg = msg["message"]

                    if code_name not in self.ps_map:
                        # For now just clone BLANK_PS and assign code_name
                        ps = BLANK_PS
                        ps.code_name = code_name
                        self.ps_map[code_name] = ps
                        self.gs.players.append(ps)

                    ps = self.ps_map[code_name]
                    self.ss, ps, self.gs = play_game(self.ss, ps, self.gs, user_msg)

                    # Send updated chat log to everyone
                    chat_update = {
                        "type": "chat_update",
                        "messages": self.gs.chat_this_round
                    }

                    for client in list(self.clients):  # make a copy to avoid mutation while iterating
                        try:
                            client.sendall(json.dumps(chat_update).encode())
                        except Exception as e:
                            print(f"Failed to send to {self.clients.get(client)}: {e}")
                            self.disconnect_client(client)


                    self.gs.chat_this_round.clear()  # clear after broadcasting
            else:
                self.disconnect_client(sock)

        except Exception as e:
            print("Error:", e)
            self.disconnect_client(sock)

    def disconnect_client(self, sock):
        self.sel.unregister(sock)
        sock.close()
        if sock in self.clients:
            del self.clients[sock]

    def run(self):
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((self.host, self.port))
        server_sock.listen()
        server_sock.setblocking(False)
        self.sel.register(server_sock, selectors.EVENT_READ)

        print(f"Server running on {self.host}:{self.port}")
        try:
            while True:
                events = self.sel.select()
                for key, _ in events:
                    if key.data is None:
                        self.accept_connection(key.fileobj)
                    else:
                        self.handle_client(key.fileobj)
        except KeyboardInterrupt:
            print("Server shutting down.")

if __name__ == "__main__":
    server = ChatServer()
    server.run()