import threading
import socket
import time


class Server:
    def __init__(self, socket):
        self.connections = []
        self.socket = socket

        t = threading.Thread(target=self.listen_for_clients, daemon=True)
        t.start()

    def listen_for_clients(self):
        while True:
            conn, addr = self.socket.accept()
            print(addr)
            self.connections.append(conn)
            t = threading.Thread(target=self.threaded_client, args=(conn,), daemon=True)
            t.start()

    def send_to_other_clients(self, data, excluded_client):
        # data = data.encode("ascii")

        for client in self.connections:
            if not (client is excluded_client):
                client.send(data)

    def threaded_client(self, conn):

        character = conn.recv(1024)
        time.sleep(10)

        self.send_to_other_clients(character, conn)
        print(character.decode("ascii"))

        conn.send("(0, 0)".encode("ascii"))

        while True:
            data = conn.recv(1024)
            print(data.decode("ascii"))
            self.send_to_other_clients(data, conn)


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((socket.gethostname(), 5555))
    s.listen()

    server = Server(s)
    print(socket.gethostbyname(socket.gethostname()))
    # server.listen_for_clients()

    while True:
        time.sleep(10)


if __name__ == "__main__":
    main()
