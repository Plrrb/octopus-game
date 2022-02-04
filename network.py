import pickle
import socket
import sys
import threading
import time


def func_timer(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()

        result = func(*args, **kwargs)

        end = time.perf_counter() - start

        print(func.__name__, end)

        return result

    return wrapper


class Network:
    def __init__(self, socket, on_recv, on_send):
        self.socket = socket

        self.on_recv = on_recv
        self.on_send = on_send

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
            print("Error!")
            self.socket.close()

    @func_timer
    def recv_data(self):
        data = self.socket.recv(512)
        data = pickle.loads(data)

        return data

    @func_timer
    def send_data(self, data):
        data = pickle.dumps(data)
        self.socket.send(data)

    @staticmethod
    def get_local_ip():
        return socket.gethostbyname(socket.gethostname())


def auto_connect(ip):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect((ip, 5555))
