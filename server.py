import threading
import socket
import select

HOST = "0.0.0.0"  # Listen on all interfaces
PORT = 63542      # Any free & (unreserved port > 1023)
MAX_CONNECTIONS = 1000  # Maximum number of simultaneous connections

thr_locker = threading.Lock()
clients = {}  # Dictionary for storing client sockets

def client_service(client_socket, addr):
    print(f"Client connected from: {addr} => {threading.current_thread().name}")
    with client_socket:
        try:
            while True:
                ready = select.select([client_socket], [], [], 1.0)
                if ready[0]:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    
                    message = f"({addr}): {data.decode('utf-8')}"
                    broadcast(message, client_socket)
        except Exception as e:
            print(f"Error in client thread: {e}")
        finally:
            with thr_locker:
                if addr in clients:
                    del clients[addr]
            print(f"Client disconnected: {addr}")

def broadcast(message, sender_socket):
    with thr_locker:
        for addr, client_socket in list(clients.items()):
            if client_socket != sender_socket:
                try:
                    client_socket.send(message.encode('utf-8'))
                except Exception as e:
                    print(f"Error sending to {addr}: {e}")
                    del clients[addr]

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(MAX_CONNECTIONS)
    print(f"Server is listening on {HOST}:{PORT}")

    try:
        while True:
            client_socket, addr = server_socket.accept()
            if len(clients) >= MAX_CONNECTIONS:
                client_socket.send("Server is full. Try again later.".encode('utf-8'))
                client_socket.close()
                continue

            with thr_locker:
                clients[addr] = client_socket

            client_thread = threading.Thread(target=client_service, args=(client_socket, addr), name=f"Thread for - ({addr})", daemon=True)
            client_thread.start()
    except KeyboardInterrupt:
        print("Server is shutting down.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()