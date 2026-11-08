import socket
import threading

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("127.0.0.1", 5000))
server.listen()

clients = []

def broadcast(message, sender_socket):
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message)
            except:
                client.close()
                clients.remove(client)

def handle(client):
    while True:
        try:
            msg = client.recv(1024)
            broadcast(msg, client)
        except:
            clients.remove(client)
            client.close()
            break

print("Сервер запущено...")
while True:
    client, _ = server.accept()
    clients.append(client)
    threading.Thread(target=handle, args=(client,), daemon=True).start()