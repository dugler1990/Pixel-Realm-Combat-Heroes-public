import socket

# Define host and port
HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

# Create a socket object
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    # Bind the socket to the address and port
    server_socket.bind((HOST, PORT))
    
    # Listen for incoming connections
    server_socket.listen()

    print(f"Server listening on {HOST}:{PORT}")

    # Accept connections
    connection, address = server_socket.accept()

    with connection:
        print('Connected by', address)

        # Receive data from the client
        while True:
            data = connection.recv(1024)
            if not data:
                break
            print(f"Received from client: {data.decode()}")

            # Send a response back to the client
            connection.sendall(data)
