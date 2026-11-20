import socket
import threading

# -----------------------------------------
# PROJECT: CHAT APPLICATION - CLIENT
# Oasis Infobyte Python Programming Internship - Task 5
# -----------------------------------------
# Start the server file first. Then run this file once for each user.

HOST = "127.0.0.1"   # the server's address. Use the server device's Wi-Fi address to chat across devices.
PORT = 5000

# running is a list so that both parts of the program can change it
running = [True]


def receive_messages(connection):
    # Runs in its own thread: prints every message the server sends
    reader = connection.makefile("r", encoding="utf-8", errors="replace")

    try:
        for line in reader:
            print(line.rstrip())
    except OSError:
        pass

    # If we get here and we did not choose to leave, the server closed the connection
    if running[0]:
        print("\nDisconnected from the server. Press Enter to exit.")

    running[0] = False


def main():
    name = ""

    while not name:
        name = input("Enter your name: ").strip()

    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        connection.connect((HOST, PORT))
    except OSError:
        print("Could not connect to the server. Is the server running?")
        return

    # The first thing we send is our name
    connection.sendall((name + "\n").encode("utf-8"))

    thread = threading.Thread(
        target=receive_messages,
        args=(connection,),
        daemon=True
    )
    thread.start()

    try:
        while running[0]:
            text = input()

            if not running[0]:
                break

            if text.strip() == "/quit":
                break

            if text.strip():
                connection.sendall((text + "\n").encode("utf-8"))

    except (KeyboardInterrupt, EOFError):
        pass

    except OSError:
        print("Lost the connection to the server.")

    finally:
        running[0] = False

        try:
            connection.close()
        except OSError:
            pass

    print("You left the chat.")


if __name__ == "__main__":
    main()
