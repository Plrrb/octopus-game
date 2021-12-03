import pickle
import socket
import threading
import time


class Client:
    def __init__(self, conn, id, database):
        self.conn = conn
        self.database = database
        self.id = id
        self.database.append(None)

    def listen(self):
        try:
            while True:
                incoming_data = self.conn.recv(2048)

                self.database[self.id] = pickle.loads(incoming_data)

                data = pickle.dumps(self.get_database_exclude_self())
                self.conn.send(data)

        except socket.error:
            self.conn.close()
            print(self.id, "Has Left")

    def get_database_exclude_self(self):
        return self.database[0 : self.id] + self.database[self.id + 1 :]


class Server:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((socket.gethostname(), 5555))

        self.clients = []
        self.database = []

    def listen_for_clients(self):
        while True:
            conn, addr = self.socket.accept()
            print(addr[0], "Connected")

            c = Client(conn, len(self.database), self.database)
            t = threading.Thread(target=c.listen, daemon=True)
            t.start()

    def connect(self):
        self.socket.listen()


def main():

    server = Server()
    server.connect()

    t = threading.Thread(target=server.listen_for_clients, daemon=True)
    t.start()

    print(socket.gethostbyname(socket.gethostname()))

    while True:
        time.sleep(10)


if __name__ == "__main__":
    main()
