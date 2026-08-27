import socket
import threading
import os

HOST = '0.0.0.0'
PORT = 5000
MAX_CLIENTS = 10

clients = {}  # {client_socket: nickname}
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(MAX_CLIENTS)

os.makedirs("server_storage", exist_ok=True)
print(f"[*] Сервер запущен на порту {PORT}. Максимум клиентов: {MAX_CLIENTS}")


def broadcast(message, sender_socket=None):
    for client_sock in list(clients.keys()):
        if client_sock != sender_socket:
            try:
                client_sock.send(message)
            except:
                remove_client(client_sock)


def remove_client(client_sock):
    if client_sock in clients:
        nickname = clients[client_sock]
        del clients[client_sock]
        client_sock.close()
        broadcast(f"[Система]: {nickname} покинул чат.\n".encode('utf-8'))
        print(f"[-] Клиент отключился: {nickname}")


def handle_client(client_sock, address):
    try:
        client_sock.send("NICK".encode('utf-8'))
        nickname = client_sock.recv(1024).decode('utf-8').strip()

        if len(clients) >= MAX_CLIENTS:
            client_sock.send("FULL".encode('utf-8'))
            client_sock.close()
            return

        clients[client_sock] = nickname
        print(f"[+] Подключился {nickname} с адреса {address}")
        broadcast(f"[Система]: {nickname} присоединился к чату.\n".encode('utf-8'), client_sock)

        while True:
            header = client_sock.recv(102).decode('utf-8')
            if not header:
                break

            if header.startswith("TEXT:"):
                msg = client_sock.recv(1024)
                full_message = f"{nickname}: {msg.decode('utf-8')}".encode('utf-8')
                broadcast(full_message, client_sock)

            elif header.startswith("FILE:"):
                _, filename, filesize = header.split(":")
                filesize = int(filesize)
                filepath = os.path.join("server_storage", filename)

                broadcast(f"[Файл]: {nickname} отправил файл -> {filename}\n".encode('utf-8'), client_sock)

                with open(filepath, "wb") as f:
                    bytes_received = 0
                    while bytes_received < filesize:
                        chunk = client_sock.recv(min(filesize - bytes_received, 4096))
                        if not chunk:
                            break
                        f.write(chunk)
                        bytes_received += len(chunk)
                print(f"[+] Получен файл {filename} от {nickname}")
    except:
        pass
    finally:
        remove_client(client_sock)


while True:
    client_sock, address = server_socket.accept()
    if len(clients) >= MAX_CLIENTS:
        client_sock.send("FULL".encode('utf-8'))
        client_sock.close()
        continue
    threading.Thread(target=handle_client, args=(client_sock, address), daemon=True).start()