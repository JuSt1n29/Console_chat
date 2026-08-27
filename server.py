import socket
import threading
import os

HOST = '0.0.0.0'
PORT = 5000
MAX_CLIENTS = 25

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
                client_sock.sendall(message)
            except:
                remove_client(client_sock)


def remove_client(client_sock):
    if client_sock in clients:
        nickname = clients[client_sock]
        del clients[client_sock]
        client_sock.close()
        broadcast(f"\033[91m[Система] {nickname} покинул чат.\033[0m\n".encode('utf-8'))
        print(f"[-] Отключился: {nickname}")


def handle_client(client_sock, address):
    nickname = "Unknown"
    try:
        client_sock.sendall(b"NICK_REQ")
        nickname = client_sock.recv(1024).decode('utf-8').strip()

        if len(clients) >= MAX_CLIENTS:
            client_sock.sendall(b"FULL")
            client_sock.close()
            return

        clients[client_sock] = nickname
        print(f"[+] Подключился {nickname} ({address[0]})")
        broadcast(f"\033[92m[Система] {nickname} присоединился к чату.\033[0m\n".encode('utf-8'), client_sock)

        while True:
            header_len_bytes = client_sock.recv(4)
            if not header_len_bytes:
                break
            header_len = int.from_bytes(header_len_bytes, 'big')
            header = client_sock.recv(header_len).decode('utf-8')

            if header.startswith("TEXT:"):
                msg_len = int(header.split(":")[1])
                encrypted_msg = client_sock.recv(msg_len)
                full_packet = header_len_bytes + header.encode('utf-8') + encrypted_msg
                broadcast(full_packet, client_sock)

            elif header.startswith("FILE:"):
                _, filename, filesize = header.split(":")
                filesize = int(filesize)
                filepath = os.path.join("server_storage", filename)

                # Принимаем файл от отправителя
                with open(filepath, "wb") as f:
                    received = 0
                    while received < filesize:
                        chunk = client_sock.recv(min(filesize - received, 65536))
                        if not chunk:
                            break
                        f.write(chunk)
                        received += len(chunk)

                print(f"[+] Получен файл '{filename}' от {nickname}")

                # Рассылаем уведомление и сам файл всем остальным клиентам
                notif_text = f"\033[96m[Файл] {nickname} отправил файл: {filename} ({round(filesize / 1024, 1)} KB)\033[0m"
                notif_bytes = notif_text.encode('utf-8')

                for client in clients:
                    if client != client_sock:
                        try:
                            client.sendall(b"MSG:" + notif_bytes)
                            client.sendall(
                                b"DL_PROMPT:" + filename.encode('utf-8') + b":" + str(filesize).encode('utf-8'))
                        except:
                            pass

                # Отправляем файл получателям по запросу или сразу (в данной реализации - шлем поток байтов для скачивания по требованию)
    except:
        pass
    finally:
        remove_client(client_sock)


while True:
    client_sock, address = server_socket.accept()
    if len(clients) >= MAX_CLIENTS:
        client_sock.sendall(b"FULL")
        client_sock.close()
        continue
    threading.Thread(target=handle_client, args=(client_sock, address), daemon=True).start()