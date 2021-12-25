import pickle
import socket
import threading
import time

RECV_BYTE_SIZE = 2048


class Network:
    def __init__(self, socket, on_recv, on_send):
        self.socket = socket

        self.on_recv = on_recv
        self.on_send = on_send

        self.incoming_channels = {}

        self.outgoing_channels = {}

    def run(self):
        self.running = True

        self.t = threading.Thread(target=self.listen, daemon=True)
        self.t.start()

    def stop(self):
        self.running = False

    def listen(self):
        try:
            while self.running:
                self.send_data(self.on_send())

                d = self.recv_data()

                self.on_recv(d)

                # time.sleep(1)

        except socket.error:
            print("Server Error!")
            self.socket.close()
            self.stop()

    def recv_data(self):
        data = self.socket.recv(RECV_BYTE_SIZE)
        data = pickle.loads(data)
        self.incoming_channels.update(data)

        return data

    def send_data(self, data):
        self.outgoing_channels.update(data)
        data = pickle.dumps(self.outgoing_channels)

        self.socket.send(data)

    @staticmethod
    def get_local_ip():
        return socket.gethostbyname(socket.gethostname())
