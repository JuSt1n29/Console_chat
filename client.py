import socket
import threading
import os
import sys

SERVER_IP = input("Введите IP сервера: ")
PORT = 5000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client.connect((SERVER_IP, PORT))
except Exception as e:
    print(f"Ошибка подключения: {e}")
    sys.exit()


def receive_messages():
    while True:
        try:
            message = client.recv(1024)
            if not message:
                break
            if message == b"NICK":
                nickname = input("Введите ваш никнейм: ")
                client.send(nickname.encode('utf-8'))
            elif message == b"FULL":
                print("[!] Чат переполнен (максимум 10 участников).")
                client.close()
                sys.exit()
            else:
                print(message.decode('utf-8'), end="")
        except:
            print("\n[!] Соединение с сервером разорвано.")
            client.close()
            break


threading.Thread(target=receive_messages, daemon=True).start()

print("\n--- Групповой чат активирован ---")
print("Команды:")
print("• Текст: просто введите сообщение и нажмите Enter")
print("• Файл: /file путь_к_файлу\n")

while True:
    try:
        text = input()
        if not text.strip():
            continue
        if text.startswith("/file "):
            filepath = text.split(" ", 1)[1].strip()
            if os.path.exists(filepath):
                filename = os.path.basename(filepath)
                filesize = os.path.getsize(filepath)
                client.send(f"FILE:{filename}:{filesize}".encode('utf-8'))

                with open(filepath, "rb") as f:
                    while True:
                        chunk = f.read(4096)
                        if not chunk:
                            break
                        client.sendall(chunk)
                print(f"[+] Файл {filename} успешно отправлен в чат.")
            else:
                print("[-] Указанный файл не найден!")
        else:
            client.send(b"TEXT:")
            client.send(text.encode('utf-8'))
    except KeyboardInterrupt:
        client.close()
        sys.exit()