import pickle
import socket
import threading
import time

RECV_BYTE_SIZE = 2048


class Server:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((socket.gethostname(), 5555))
        self.clients_connected = 0

        self.database = {}

    def run(self):
        self.socket.listen()

        t = threading.Thread(target=self.listen_for_clients, daemon=True)
        t.start()

    def listen_for_clients(self):
        while True:
            conn, addr = self.socket.accept()
            print(addr[0], "Connected")

            self.clients_connected += 1

            c = self.Client(conn, self)
            t = threading.Thread(target=c.listen)
            t.start()

    class Client:
        def __init__(self, socket, server):
            self.index = server.clients_connected
            self.socket = socket
            self.database = server.database
            self.server = server

        def listen(self):
            try:
                data = self.recv_data()

                self.database[self.index] = data

                while True:
                    if self.get_database_exclude_self() != {}:
                        self.send_data(self.get_database_exclude_self())
                        break

                while True:
                    data = self.recv_data()

                    self.database[self.index].update(data)

                    self.send_data(self.get_database_exclude_self())

                    # time.sleep(1)

            except ConnectionResetError:
                self.conn.close()
                print(self.index, "has left")

        def get_database_exclude_self(self):
            d = self.database.copy()
            del d[self.index]
            return d

        def send_data(self, data):
            data = pickle.dumps(data)
            self.socket.send(data)

        def recv_data(self):
            data = self.socket.recv(RECV_BYTE_SIZE)
            data = pickle.loads(data)
            return data


def main():
    s = Server()
    s.run()
    print(socket.gethostbyname(socket.gethostname()))

    while True:
        time.sleep(10)


if __name__ == "__main__":
    main()
