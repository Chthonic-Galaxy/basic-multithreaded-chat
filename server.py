import threading
import socket

HOST = ""    # Any available IP/HOST
PORT = 63542 # Any free & non-reserved port

thr_locker = threading.Lock()

queue = set()


def client_service(client_socket, addr):
    print(f"Client connected from: {addr} => {threading.current_thread().name}")
    with client_socket:
        try:
            while True:
                # recive data from client
                data=client_socket.recv(1024)
                
                # if not data -> break
                if not data or not (data.decode("utf-8")):
                    with thr_locker:
                        queue.discard(client)
                    break
                
                # try to send data to all clients
                for client in queue:
                    if client != client_socket:
                        try:
                            client.send(f"({addr}): {data}".encode("utf-8"))
                        except Exception as err:
                            with thr_locker:
                                print(f"{threading.current_thread().name} => {err}")
                                queue.discard(client)
        except:
            print("Exited by the user")
            with thr_locker:
                queue.remove(client_socket)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
    server_sock.bind((HOST, PORT))
    
    server_sock.listen()
    
    while True:
        client_socket, addr = server_sock.accept()
        queue.add(client_socket)
        threading.Thread(target=client_service, args=(client_socket, addr,), name=f"Thread for - ({addr})", daemon=True).start()
