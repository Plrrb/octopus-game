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
            print("New Connection From:", addr)
            self.connections.append(conn)

            t = threading.Thread(target=self.threaded_client, args=(conn,), daemon=True)
            t.start()

    def send_to_other_clients(self, data, excluded_client):
        for client in self.connections:
            if client is not excluded_client:
                client.send(data)

    def threaded_client(self, conn):
        try:
            while True:
                data = conn.recv(1024)
                # this could cause a problem, where we send double data to a client
                # maybe try a loop that sends and recv's for each client
                self.send_to_other_clients(data, conn)

        except ConnectionResetError:
            print(conn, "Has Left")
            self.connections.remove(conn)
            conn.close()
            return


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

# import pickle
# import threading
# import socket
# import time


# class Client:
#     def __init__(self, conn, id, database):
#         self.conn = conn
#         self.database = database
#         self.id = id

#     def listen(self):
#         try:
#             while True:
#                 incoming_data = self.conn.recv(2048)
#                 self.database[self.id] = incoming_data

#                 # self.database[self.id] = pickle.loads(incoming_data)

#                 self.conn.send(pickle.dumps(self.database))

#         except socket.error:
#             self.conn.close()
#             print(self.id, "Has Left")

##not really nedded
# class Server:
#     def __init__(self, socket):
#         self.socket = socket
#         self.connections = []
#         self.database = []

#         t = threading.Thread(target=self.listen_for_clients, daemon=True)
#         t.start()

#     def listen_for_clients(self):
#         while True:
#             conn, addr = self.socket.accept()
#             print("New Connection From:", addr)

#             index = len(self.connections)
#             self.connections.append(index)
#             self.database.append(None)

#             t = threading.Thread(
#                 target=self.threaded_client, args=(conn, index), daemon=True
#             )
#             t.start()

#     def threaded_client(self, conn, index):
#         try:
#             while True:
#                 data = conn.recv(512)
#                 self.database[index] = data

#                 msg = pickle.dumps(self.get_database_exclude_index(index))
#                 conn.send(msg)

#         except socket.error:
#             print(index, "Has Left")
#             del self.database[index]
#             self.connections.remove(index)
#             conn.close()
#             return

#     def get_database_exclude_index(self, index):
#         return self.database[0:index] + self.database[index:-1]


# class New_Server:
#     def __init__(self):
#         self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.socket.bind((socket.gethostname(), 5555))

#         self.clients = []
#         self.database = {}

#     def listen_for_clients(self):
#         while True:
#             conn, addr = self.socket.accept()
#             print(addr[0], "Connected")

#             c = Client(conn, len(self.clients), self.database)
#             t = threading.Thread(target=c.listen, daemon=True)
#             t.start()

#     def connect(self):
#         self.socket.listen()


# def main():

#     server = New_Server()
#     server.connect()

#     t = threading.Thread(target=server.listen_for_clients, daemon=True)
#     t.start()

#     print(socket.gethostbyname(socket.gethostname()))

#     while True:
#         time.sleep(10)


# if __name__ == "__main__":
#     main()
