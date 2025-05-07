
from __future__ import annotations
import socket
import subprocess
import logging
import time
import json
import threading

logger = logging.getLogger(__name__)

MAX_MSG_SIZE = 2**18

class Client(dict):
    def __init__(self, server_socket: socket.socket, addr, pid: int = 0):
        self.server_socket = server_socket
        self.addr = addr
        self.pid = pid
        self.new_data_avail = False
        self["steer"] = 0
        self["acc"] = -1
        self["brake"] = -1
        self["enable_clutch"] = False
        self["clutch"] = -1
        self["enable_gear_shift"] = False
        self["shift_up"] = False
        self["shift_down"] = False
        self.initialized = False

    def send_reply(self, msg):
        """
        Send a reply to the client
        """
        self.server_socket.sendto(msg.encode(), self.addr)

    def release_lock(self):
        self.lock = False

    def locked_held(self):
        return self.lock

    def get_lock(self):
        if self.lock:
            return False
        self.lock = True
        return True

    def set_lock(self, lock):
        self.lock = lock

    def update(self, data):
        super().update(data)
        self.new_data_avail = True

    def get(self):
        self.new_data_avail = False
        return self

    def export(self):
        return json.dumps(self)

class EgoClient:
    def __init__(self):
        # server info
        self.host_name = "localhost"
        self.port = 2345
        self.socket: socket.socket = None

    def reply_to_server(self, msg: str):
        if not self.socket:
            return
        try:
            self.socket.sendto(msg.encode(), (self.host_name, self.port))
        except socket.error as emsg:
            logger.error(f"Error sending to server: {emsg}")
            raise TimeoutError

    def setup_server_connection(self, sched_server, schedule: function):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(2)
        print(f"Scheduler. Listening to ego at host: {self.host_name} port: {self.port}")

        while True:
            self.reply_to_server("connect")
            try:
                # Receive data from server
                data, _ = self.socket.recvfrom(MAX_MSG_SIZE)
                data = data.decode()
                if data == "identified":
                    print(f"Scheduler connected on {self.port}")
                    break
            except socket.timeout:
                continue
        self.get_servers_input(sched_server, schedule)

    def get_servers_input(self, sched_server: SchedServer, schedule: function):
        if not self.socket:
            return

        while True:
            try:
                # Receive data from server
                data, _ = self.socket.recvfrom(MAX_MSG_SIZE)
                data = data.decode()

                # print("[SCHED] Received data from [EGO]")

                if data == "disconnect":
                    print("Server stopped the connection")
                elif data == "identified":
                    print("Server identified")
                else:
                    # model switching
                    sched_server.current_client = schedule(sched_server.clients, data)
                    # print(sched_server.current_client.pid)

                # print("[SCHED] Sending to [CLIENT]")
                # forward to client
                sched_server.current_client.send_reply(data)
            except socket.timeout:
                continue

class SchedServer:
    def __init__(self):
        self.host_name = "localhost"
        self.port = 2348
        self.socket = None
        self.current_client: Client = None
        self.socket_open = False
        self.clients: list[Client] = []

    def start(self, ego_client):
        self.thread = threading.Thread(target=self.start_server, args=[ego_client])
        self.thread.daemon = True
        self.thread.start()

    def close(self):
        time.sleep(0.5)

        if self.socket and self.socket_open:
            self.socket.close()
            self.socket_open = False

    def start_server(self, ego_client: EgoClient):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_open = True  # Flag to indicate socket is open
        self.socket.bind((self.host_name, self.port))
        self.socket.settimeout(1.0)
        print(f"[SCHED SERV] Start scheduler server socket on: {self.host_name}:{self.port}")
        try:
            while self.socket and self.socket_open:
                addr = None
                try:
                    # Receives data from the correct client
                    data, addr = self.socket.recvfrom(1024)
                    data = data.decode()

                    if data[:7] == "connect":
                        if self.current_client:
                            self.current_client = None
                            logger.warning("New client connected while another client was still connected. Switching to new client.")
                        print(f"CLIENT PID: {int(data[-5:])}")
                        self.current_client = Client(self.socket, addr, int(data[-5:])) # start with the lock acquired
                        self.clients.append(self.current_client)
                        self.current_client.send_reply("identified")
                        time.sleep(0.1) # make sure that the identified message is sent before releasing the lock
                        print("Switched to new client {}".format(self.current_client.addr))
                        self.current_client.initialized = True
                    else:
                        # forward to ego
                        ego_client.reply_to_server(data)
                    
                except socket.timeout:
                    continue
                except ConnectionResetError:
                    print("Connection to client {} was lost.".format(addr))
                    self.current_client = None
                except OSError as e:
                    if e.winerror == 10038 and not self.socket_open:
                        # This means the socket was closed while recvfrom() was waiting
                        print("Socket operation attempted on closed socket, exiting loop.")
                        break
                    else:
                        raise
                except Exception:
                    logger.exception("An error occurred")
                    if self.current_client:
                        self.current_client.send_reply("disconnect")
                    break
        except Exception:
            logging.exception("An error occurred in the Ego server thread")
        finally:
            if self.socket_open:
                self.close()
