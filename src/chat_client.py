# chat_client.py
import socket
import threading
import json

class ChatClient:
    def __init__(self, host="127.0.0.1", port=65432):
        self.host = host
        self.port = port
        self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def receive_messages(self):
        try:
            while True:
                data = self.client_sock.recv(4096).decode()
                if not data:
                    break

                response = json.loads(data)
                if response["type"] == "chat_update":
                    for msg in response["messages"]:
                        print(msg)
        except Exception as e:
            print("Connection lost:", e)

    def start(self, player_code_name):
        self.client_sock.connect((self.host, self.port))
        print("Connected to chat server. Type 'exit' to quit.")

        threading.Thread(target=self.receive_messages, daemon=True).start()

        try:
            while True:
                msg = input()
                if msg.strip().lower() == "exit":
                    break

                payload = {
                    "type": "player_input",
                    "player_code_name": player_code_name,
                    "message": msg
                }
                self.client_sock.sendall(json.dumps(payload).encode())
        finally:
            self.client_sock.close()
