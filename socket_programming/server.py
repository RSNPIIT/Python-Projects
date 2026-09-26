import socket
import threading # Essentially it is a way of creating multiple 'threads' within one python Program

HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONN_MSG = "!exit"

server = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)
server.bind(ADDR)

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} CONNECTED !")
    
    connected = True
    while connected:
        try:
            raw_msg_len = conn.recv(HEADER).decode(FORMAT)
            if not raw_msg_len:
                break
            msg_len = int(raw_msg_len)
            msg = conn.recv(msg_len).decode(FORMAT)
            if msg == DISCONN_MSG:
                connected = False

            print(f"[{addr}] -> {msg}")
            conn.send(
                "\nMessage Received by the server herein..."
                .encode(FORMAT)
            )
        except (ConnectionResetError, ValueError):
            break

    conn.close()

def start():
    server.listen()
    print(f"[SERVER] is listening on {SERVER}")
    while True:
        try:
            conn, addr = server.accept()
            thread = threading.Thread(
                target = handle_client,
                args = (conn, addr)
            )
            thread.daemon = True
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
        except KeyboardInterrupt:
            print("\nExiting server loop cleanly...")
            break

if __name__ == "__main__":
    print("[SERVER] is starting ...")
    try:
        start()
    except KeyboardInterrupt as kb:
        print("\nExitting....\nPlease don't spam")
    finally:
        server.close()