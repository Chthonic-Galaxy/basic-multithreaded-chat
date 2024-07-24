import threading
import socket

HOST = ""    # Any available IP/HOST
PORT = 63542 # Any free & non-reserved port

def recv_data(socket: socket.socket):
    with socket:
        while True:
            recived_data = socket.recv(1024)
            print(f"\n{recived_data.decode('utf-8')}")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    client_socket.connect((HOST, PORT))
    
    threading.Thread(target=recv_data, args=(client_socket,), daemon=True).start()
    
    while True:
        try:
            client_data = input(">>> ")
            if client_data.lower() == "exit": break
            client_socket.send(client_data.encode("utf-8"))
        except:
            print("Exited")
            break
