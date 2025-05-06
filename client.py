
import socket
import logging
# from config import config

logger = logging.getLogger(__name__)
MAX_MSG_SIZE = 2**18
HOST = "localhost"
PORT = 2458

def reply_to_server(msg: str):
    if not sock:
        return
    try:
        sock.sendto(msg.encode(), (HOST, PORT))
    except socket.error as emsg:
        logger.error(f"Error sending to server: {emsg}")
        raise TimeoutError

# establish connection with scheduler
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
while True:
    reply_to_server("connect")
    try:
        # Receive data from server
        data, _ = sock.recvfrom(MAX_MSG_SIZE)
        data = data.decode()
        logger.debug(f"Got from server: {data}")
        if data == "identified":
            print(f"Client connected on {PORT}")
            break
    except socket.timeout:
        continue
