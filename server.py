import threading
import socket


class Server:
    def __init__(self, socket):
        self.connections = []
        self.socket = socket

    def listen_for_clients(self):
        while True:
            conn, addr = self.socket.accept()
            print(addr)
            self.connections.append(conn)
            t = threading.Thread(target=self.threaded_client, args=(conn,))
            t.start()

    def send_to_other_clients(self, data, excluded_client):
        data = data.encode("ascii")

        for client in self.connections:
            if client is not excluded_client:
                client.send(data)

    def threaded_client(self, conn):
        while True:
            data = conn.recv(1024)
            self.send_to_other_clients(data, conn)


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((socket.gethostname(), 5555))
    s.listen()

    server = Server(s)
    server.listen_for_clients()


if __name__ == "__main__":
    main()
