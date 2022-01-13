import pickle
import socket
import threading
import time


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

            c = self.Client(conn, self.clients_connected, self.database)
            t = threading.Thread(target=c.listen)
            t.start()

            self.clients_connected += 1

    class Client:
        def __init__(self, socket, index, database):
            self.index = index
            self.socket = socket
            self.database = database
            self.database[self.index] = {}

        def listen(self):
            try:
                while True:
                    data = self.recv_data()

                    self.database[self.index].update(data)

                    self.send_data(self.get_database_exclude_self())

            except socket.error:
                print(self.index, "has left")
                self.socket.close()

        def get_database_exclude_self(self):
            return {i: self.database[i] for i in self.database if i != self.index}

        def send_data(self, data):
            data = pickle.dumps(data)
            self.socket.send(data)

        def recv_data(self):
            data = self.socket.recv(512)
            data = pickle.loads(data)

            return data


def main():
    s = Server()
    s.run()
    print("server local ip", socket.gethostbyname(socket.gethostname()))

    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("finished")


if __name__ == "__main__":
    main()
