import socket
import threading
import pygame
import msgpack
from common import GameState, Player
import time
import uuid

class GameClient:
    def __init__(self, host='localhost', rec_port=12345, send_port=12346):
        self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.send_socket.connect((host, send_port))
        print("Connected to server for sending")
        time.sleep(1)
        self.recv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.recv_socket.connect((host, rec_port))
        print("Connected to server for receiving")
        self.game_state = GameState()
        self.player_id = str(uuid.uuid4())  # Generate a unique player ID
        self.player_name = "Player1"  # Replace with actual player name or input

    def send_input(self, input_data):
        message = {'type': 'input', 'input': input_data, 'player_id': self.player_id}
        self.send_socket.sendall(msgpack.packb(message))
        print(f"Sent input: {input_data}")

    def receive_game_state(self):
        print("Started receiving game state")
        buffer = b''  # Initialize an empty buffer
        
        while True:
            try:
                data = self.recv_socket.recv(1024)
                if data:
                    print(f"Data received from server: {data}")
                    buffer += data  # Add received data to buffer
                    
                    while True:
                        try:
                            unpacker = msgpack.Unpacker()
                            unpacker.feed(buffer)
                            message = unpacker.unpack()  # Unpack one message from the buffer
                            print(f"Unpacked message: {message}")
                            if message['type'] == 'state_update':
                                print("Processing state update")
                                self.game_state.players = {pid: Player(**pdata) for pid, pdata in message['players'].items()}
                                print("Updated game state")
                            
                            # Update the buffer to remove the processed message
                            buffer = buffer[unpacker.tell():]
                        except msgpack.exceptions.OutOfData:
                            break
            except Exception as e:
                print(f"Receive error: {e}")
                break


    def run(self):
        pygame.init()
        screen = pygame.display.set_mode((800, 600))

        connect_message = {
            'type': 'connect',
            'player': {
                'id': self.player_id,
                'name': self.player_name,
                'position': [100, 100]
            }
        }
        self.send_socket.sendall(msgpack.packb(connect_message))
        print(f"Sent connect message: {connect_message}")

        receive_thread = threading.Thread(target=self.receive_game_state)
        receive_thread.start()

        clock = pygame.time.Clock()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    disconnect_message = {'type': 'disconnect', 'player_id': self.player_id}
                    self.send_socket.sendall(msgpack.packb(disconnect_message))
                    print("Sent disconnect message")
                    return
                if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                    input_data = {
                        'key': event.key,
                        'type': event.type,
                    }
                    self.send_input(input_data)

            screen.fill((0, 0, 0))
            # Render the game state
            for player in self.game_state.players.values():
                pygame.draw.rect(screen, (100, 100, 100), pygame.Rect(player.position[0], player.position[1], 50, 50))

            pygame.display.flip()
            clock.tick(60)

if __name__ == "__main__":
    client = GameClient()
    client.run()
