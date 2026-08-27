# Console_chat

![logo](images/5BEF9730-C540-43A6-BF39-1342B8281EF5.png)

A simple console chat application written in Python.

The application uses a client-server architecture. Multiple clients can connect to one server and exchange messages and files through the terminal.

## Features

* TCP client-server communication
* Multiple users
* Usernames
* Group chat
* File transfer
* Terminal-based interface
* Simple Python implementation

## How It Works

The project consists of two main parts:

```text
             ┌──────────────┐
             │    Server    │
             │   Port 5000  │
             └──────┬───────┘
                    │
          ┌─────────┼─────────┐
          │         │         │
          ▼         ▼         ▼
       Client    Client    Client
```

### Server

The server listens for incoming TCP connections on port `5000`.

When a client connects:

1. The server asks for a username.
2. The username is saved on the server.
3. The client joins the chat.
4. The server receives messages from the client.
5. Messages are sent to the other connected users.
6. When a client disconnects, the server notifies the other users.

The server can handle multiple clients at the same time using Python threads.

### Client

The client connects to the server using its IP address.

After connecting:

1. The client enters a username.
2. A separate thread listens for incoming messages.
3. The main thread waits for user input.
4. Normal text is sent to the server.
5. The server broadcasts the message to other clients.

This allows the client to send and receive messages at the same time.

## File Transfer

Files can also be sent through the chat.

Use:

```text
/file path/to/file
```

For example:

```text
/file ./test.txt
```

The client sends information about the file to the server and then sends the file data.

The server receives the file and stores it in its storage directory.

## Requirements

* Python 3
* Network connection
* TCP port `5000`

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Start the server

```bash
python server.py
```

The server will start listening for connections.

### Start a client

```bash
python client.py
```

Enter the server IP address and your username.

For example:

```text
Server IP: 192.168.1.100
Username: user
```

## Network

The server uses:

```text
Protocol: TCP
Port: 5000
```

Clients must be able to reach the server over the network.

The application can be used on a local network or through a VPN/network such as Tailscale.

## License

This project is licensed under the MIT License.
