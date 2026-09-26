import socket
import sys as s

HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONN_MSG = "!exit"

client = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)
client.connect(ADDR)

def send(msg):
    message = msg.encode(FORMAT)
    msg_len = len(message)
    send_len = str(msg_len).encode(FORMAT)
    send_len += b' ' * (HEADER - len(send_len))
    client.send(send_len)
    client.send(message)

try:
    print("[CLIENT] connected successfully\nPlease Type your message and hit enter/return\nTo close please hit a '!exit' message\n")
    teller = True
    while teller:
        user_input = input(">>> ").strip()
        if not user_input:
            continue
        send(user_input)

        if user_input == DISCONN_MSG:
            teller = False

except KeyboardInterrupt:
    print("\nDisconnected Abruptly by the client\n")
    send(DISCONN_MSG)

except BrokenPipeError:
    print("\nServer has been closed or disconnected\n")
    s.exit()

finally:
    client.close()