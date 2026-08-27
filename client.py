import socket
import threading
import os
import sys
from cryptography.fernet import Fernet

SECRET_KEY = b'12345678901234567890123456789012='  # Замените на общий ключ
cipher = Fernet(SECRET_KEY)

SERVER_IP = input("Введите IP сервера: ")
PORT = 5000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client.connect((SERVER_IP, PORT))
except Exception as e:
    print(f"Ошибка подключения: {e}")
    sys.exit()

nickname = ""


def receive_messages():
    global nickname
    while True:
        try:
            prefix = client.recv(10)
            if not prefix:
                break

            if prefix.startswith(b"NICK_REQ"):
                nickname = input("Введите ваш никнейм: ")
                client.sendall(nickname.encode('utf-8'))
            elif prefix.startswith(b"FULL"):
                print("[!] Чат заполнен (максимум 25 участников).")
                client.close()
                sys.exit()
            elif prefix.startswith(b"TEXT:"):
                # Читаем длину заголовка
                # Восстановление логики чтения пакета текста
                pass
            # Упрощенный стабильный прием сообщений через потоки:
        except:
            break