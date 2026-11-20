import socket
import threading
from datetime import datetime

# -----------------------------------------
# PROJECT: CHAT APPLICATION - SERVER
# Oasis Infobyte Python Programming Internship - Task 5
# -----------------------------------------
# Run this file first. Then run the client file (once for each user).

HOST = "127.0.0.1"   # localhost: only this device. Use "0.0.0.0" to allow other devices on the same Wi-Fi.
PORT = 5000

MAX_NAME_LENGTH = 20
MAX_MESSAGE_LENGTH = 500

# All connected users: {connection: name}
clients = {}

# A lock stops two threads from changing the "clients" dictionary at the same time
clients_lock = threading.Lock()


def get_time():
    return datetime.now().strftime("%H:%M")


def send_line(client, text):
    # Every message is sent as one line that ends with a new line character.
    # Returns True if it was sent, False if the connection is broken.
    try:
        client.sendall((text + "\n").encode("utf-8"))
        return True
    except OSError:
        return False


def broadcast(text, skip=None):
    # Send a message to everyone (except the "skip" connection)
    with clients_lock:
        targets = [client for client in clients if client != skip]

    for client in targets:
        if not send_line(client, text):
            remove_client(client)


def remove_client(client):
    # Remove a user, close the connection and tell the others
    with clients_lock:
        name = clients.pop(client, None)

    try:
        client.close()
    except OSError:
        pass

    # Only tell the others if this user had really joined
    if name:
        print(f"{name} has left the chat.")
        broadcast(f"[{get_time()}] * {name} has left the chat.")


def handle_client(client):
    # This function runs in its own thread for every connected user
    try:
        reader = client.makefile("r", encoding="utf-8", errors="replace")

        # The first line sent by a client is its name
        name = reader.readline().strip()[:MAX_NAME_LENGTH]

        if not name:
            send_line(client, "A name is required. Please connect again.")
            return

        # Add the user, but only if the name is not already used
        with clients_lock:
            used_names = [n.lower() for n in clients.values()]
            name_is_free = name.lower() not in used_names

            if name_is_free:
                others = list(clients.values())
                clients[client] = name

        if not name_is_free:
            send_line(client, "That name is already taken. Please connect again with another name.")
            return

        # Welcome the new user
        if others:
            send_line(client, f"Welcome, {name}! Online now: {', '.join(others)}")
        else:
            send_line(client, f"Welcome, {name}! You are the only one online right now.")

        send_line(client, "Type your message and press Enter. Type /quit to leave.")

        print(f"{name} joined the chat.")
        broadcast(f"[{get_time()}] * {name} joined the chat.", skip=client)

        # Keep reading messages until the user leaves
        for line in reader:
            message = line.strip()

            if not message:
                continue

            message = message[:MAX_MESSAGE_LENGTH]
            formatted = f"[{get_time()}] {name}: {message}"

            print(formatted)
            broadcast(formatted)

    except OSError:
        # The connection broke (for example the user closed the app)
        pass

    finally:
        remove_client(client)


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Lets us restart the server quickly without an "address already in use" error
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server.bind((HOST, PORT))
    except OSError as error:
        print("Could not start the server:", error)
        print("Is another server already running on this port?")
        return

    server.listen()

    print("Chat server started!")
    print(f"Listening on {HOST}:{PORT}")
    print("Waiting for clients...")

    try:
        while True:
            client, address = server.accept()
            print(f"New connection: {address}")

            thread = threading.Thread(
                target=handle_client,
                args=(client,),
                daemon=True
            )
            thread.start()

    except KeyboardInterrupt:
        print("\nServer shutting down.")

    finally:
        with clients_lock:
            connected = list(clients)

        for client in connected:
            send_line(client, "The server is shutting down.")
            try:
                client.close()
            except OSError:
                pass

        server.close()


if __name__ == "__main__":
    start_server()
