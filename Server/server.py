import socket
import threading
import time
import msgpack
from common import GameState, Player

class ClientHandler:
    def __init__(self, send_socket, recv_socket, game_state):
        self.send_socket = send_socket
        self.recv_socket = recv_socket
        self.game_state = game_state
        self.player_id = None
        print(f"New ClientHandler created with {send_socket}, {recv_socket}")

    def handle_recv(self):
        while True:
            try:
                data = self.recv_socket.recv(1024)
                if data:
                    print(f"Received data: {data}")
                    self.process_message(msgpack.unpackb(data, raw=False))
                else:
                    break
            except Exception as e:
                print(f"Receive error: {e}")
                break

    def handle_send(self):
        while True:
            state_update = {
                'type': 'state_update', 
                'players': {pid: vars(player) for pid, player in self.game_state.players.items()}
            }
            try:
                self.send_socket.sendall(msgpack.packb(state_update))
                print(f"Sent state update: {state_update}")
            except Exception as e:
                print(f"Send error: {e}")
                break
            time.sleep(0.016) 

    def process_message(self, message):
        print(f"Received message: {message}")
        if message['type'] == 'connect':
            player_id = message['player']['id']
            new_player = Player(player_id, message['player']['name'], message['player']['position'])
            self.game_state.players[player_id] = new_player
        elif message['type'] == 'input':
            player_id = message['player_id']
            if player_id in self.game_state.players:
                self.game_state.players[player_id].handle_input(message['input'])
        elif message['type'] == 'disconnect':
            player_id = message['player_id']
            if player_id in self.game_state.players:
                del self.game_state.players[player_id]

class GameServer:
    def __init__(self, host='localhost', send_port=12345, recv_port=12346):
        self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.send_socket.bind((host, send_port))
        self.send_socket.listen()

        self.recv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.recv_socket.bind((host, recv_port))
        self.recv_socket.listen()
        
        self.game_state = GameState()
        self.client_handlers = []
        print("Server started and listening")

    def run(self):
        while True:
            send_socket, addr = self.send_socket.accept()
            print(f"Accepted connection from {addr}")
            recv_socket, addr = self.recv_socket.accept()
            print(f"Accepted second connection from {addr}")
            client_handler = ClientHandler(send_socket, recv_socket, self.game_state)
            self.client_handlers.append(client_handler)
            threading.Thread(target=client_handler.handle_recv).start()
            threading.Thread(target=client_handler.handle_send).start()

if __name__ == "__main__":
    server = GameServer()
    server.run()
