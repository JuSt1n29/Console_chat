import socket
import threading
import sys
from cryptography.fernet import Fernet

SECRET_KEY = b'12345678901234567890123456789012='  # Замените на общий ключ
cipher = Fernet(SECRET_KEY)

PORT = 5000

SERVER_IP = input("Введите IP сервера: ").strip()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client.connect((SERVER_IP, PORT))
except Exception as e:
    print(f"[!] Ошибка подключения: {e}")
    sys.exit(1)


def recv_exact(sock, size):
    data = b""

    while len(data) < size:
        chunk = sock.recv(size - len(data))

        if not chunk:
            return None

        data += chunk

    return data


def receive_messages():
    while True:
        try:

            request = recv_exact(client, 8)

            if not request:
                print("\n[!] Сервер отключил соединение.")
                break

            if request == b"NICK_REQ":
                nickname = input("Введите ваш никнейм: ").strip()

                if not nickname:
                    nickname = "Anonymous"

                client.sendall(nickname.encode("utf-8"))

                print(f"[*] Вы вошли как {nickname}")
                print("[*] Можно писать сообщения.")
                print()
                
                threading.Thread(
                    target=message_loop,
                    daemon=True
                ).start()

            elif request == b"FULL":
                print("[!] Чат заполнен.")
                client.close()
                sys.exit(0)

            else:
                header_len_bytes = request[:4]

                if len(header_len_bytes) < 4:
                    break

                header_len = int.from_bytes(header_len_bytes, "big")

                remaining = request[4:]

                if len(remaining) < header_len:
                    extra = recv_exact(
                        client,
                        header_len - len(remaining)
                    )

                    if extra is None:
                        break

                    header_bytes = remaining + extra
                else:
                    header_bytes = remaining[:header_len]

                header = header_bytes.decode("utf-8")

                if header.startswith("TEXT:"):
                    msg_len = int(header.split(":")[1])

                    encrypted_msg = recv_exact(client, msg_len)

                    if encrypted_msg is None:
                        break

                    try:
                        message = cipher.decrypt(encrypted_msg).decode("utf-8")
                        print(message)
                    except Exception:
                        print("[!] Не удалось расшифровать сообщение.")

        except Exception as e:
            print(f"\n[!] Ошибка при получении: {e}")
            break


def message_loop():
    while True:
        try:
            message = input("> ")

            if not message:
                continue

            if message.lower() == "/exit":
                client.close()
                sys.exit(0)

            encrypted_message = cipher.encrypt(
                message.encode("utf-8")
            )

            header = f"TEXT:{len(encrypted_message)}".encode("utf-8")
            header_len = len(header).to_bytes(4, "big")

            packet = header_len + header + encrypted_message

            client.sendall(packet)

        except (BrokenPipeError, ConnectionResetError):
            print("\n[!] Соединение с сервером потеряно.")
            break

        except EOFError:
            break

        except Exception as e:
            print(f"[!] Ошибка отправки: {e}")
            break

receive_messages()
