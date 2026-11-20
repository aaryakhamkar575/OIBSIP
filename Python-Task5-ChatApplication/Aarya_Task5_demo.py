import tkinter as tk
import socket
import threading
import queue
import time

# -----------------------------------------
# PROJECT: CHAT APPLICATION - ONE-PHONE DEMO
# Oasis Infobyte Python Programming Internship - Task 5
# -----------------------------------------
# Pydroid can only run one program at a time, so this file starts the
# chat server (from Aarya_Task5_server.py) in the background and shows
# TWO chat windows on one screen. Each window is a real client that
# connects to the server with a real socket connection.
#
# IMPORTANT: save this file in the SAME folder as Aarya_Task5_server.py

try:
    import Aarya_Task5_server as chat_server
except ImportError:
    chat_server = None

if chat_server is not None:
    HOST = chat_server.HOST
    PORT = chat_server.PORT
else:
    HOST = "127.0.0.1"
    PORT = 5000

# -----------------------------------------
# OCEAN BREEZE COLOUR PALETTE
# -----------------------------------------

BG_COLOR = "#EDF4F8"
LIGHT_BLUE = "#B8D8E8"
PRIMARY_BLUE = "#438BA8"
DARK_BLUE = "#24566F"
WHITE = "#FFFFFF"
ENTRY_BG = "#F4F9FB"
TEXT_COLOR = "#344B59"
GRAY_COLOR = "#7A8B96"
GOOD_COLOR = "#299D78"
ERROR_COLOR = "#D66B70"


# -----------------------------------------
# THE CONNECTION (no screen code here)
# -----------------------------------------

class ChatConnection:
    # One person connected to the chat server

    def __init__(self):
        self.sock = None
        self.reader = None
        self.connected = False

        # Messages from the server wait here until the screen shows them
        self.incoming = queue.Queue()

    def join(self, name):
        # Returns (True, welcome message) or (False, error message)

        try:
            sock = socket.create_connection((HOST, PORT), timeout=3)
        except OSError:
            return False, "Could not connect to the server."

        try:
            reader = sock.makefile("r", encoding="utf-8", errors="replace", newline="\n")

            # The first thing we send is our name
            sock.sendall((name + "\n").encode("utf-8"))
            first = reader.readline().strip()
        except OSError:
            sock.close()
            return False, "The server did not answer."

        if not first.startswith("Welcome,"):
            # The server refused us (for example, the name is taken)
            sock.close()
            return False, first or "The server closed the connection."

        sock.settimeout(None)

        self.sock = sock
        self.reader = reader
        self.connected = True
        self.incoming.put(first)

        thread = threading.Thread(target=self.listen, daemon=True)
        thread.start()

        return True, first

    def listen(self):
        # Runs in its own thread and collects everything the server sends
        try:
            for line in self.reader:
                self.incoming.put(line.rstrip("\n"))
        except (OSError, ValueError):
            pass

        if self.connected:
            self.connected = False
            self.incoming.put("-- Disconnected from the server --")

    def send(self, text):
        if not self.connected:
            return False

        try:
            self.sock.sendall((text + "\n").encode("utf-8"))
            return True
        except OSError:
            self.connected = False
            return False

    def leave(self):
        self.connected = False

        if self.sock is not None:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass

            try:
                self.sock.close()
            except OSError:
                pass

            self.sock = None


# -----------------------------------------
# GUI PART
# -----------------------------------------

# Start the chat server in the background
if chat_server is not None:
    server_thread = threading.Thread(target=chat_server.start_server, daemon=True)
    server_thread.start()
    time.sleep(0.5)

root = tk.Tk()
root.title("Chat Application Demo")

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

root.geometry(
    f"{screen_width}x{screen_height}+0+0"
)

root.configure(bg=BG_COLOR)


# -----------------------------------------
# SCALING (so everything fits the screen)
# -----------------------------------------

DESIGN_WIDTH = 800

SCALE = screen_width / DESIGN_WIDTH
SCALE = max(0.5, min(SCALE, 1.3))


def s(value):
    return max(1, int(value * SCALE))


def font(size, bold=False, italic=False):
    style = []

    if bold:
        style.append("bold")

    if italic:
        style.append("italic")

    if style:
        return ("Arial", -s(size), " ".join(style))

    return ("Arial", -s(size))


# -----------------------------------------
# SCROLLABLE SCREEN
# -----------------------------------------

main_canvas = tk.Canvas(
    root,
    bg=BG_COLOR,
    highlightthickness=0
)

main_canvas.pack(
    fill="both",
    expand=True
)

content = tk.Frame(
    main_canvas,
    bg=BG_COLOR
)

canvas_window = main_canvas.create_window(
    (0, 0),
    window=content,
    anchor="nw"
)


def update_scroll(event=None):
    main_canvas.configure(
        scrollregion=main_canvas.bbox("all")
    )


def resize_content(event):
    main_canvas.itemconfig(
        canvas_window,
        width=event.width
    )


content.bind("<Configure>", update_scroll)
main_canvas.bind("<Configure>", resize_content)


# -----------------------------------------
# FINGER-DRAG SCROLLING
# -----------------------------------------

drag_start_y = [0]
start_position = [0.0]
drag_allowed = [False]


def start_scroll(event):

    widget_type = event.widget.winfo_class()

    # Do not scroll when touching buttons, input boxes or the message boxes
    if widget_type in ("Entry", "Button", "Text"):
        drag_allowed[0] = False
        return

    drag_allowed[0] = True
    drag_start_y[0] = event.y_root

    position = main_canvas.yview()
    start_position[0] = position[0]


def move_scroll(event):

    if not drag_allowed[0]:
        return

    difference = drag_start_y[0] - event.y_root

    if abs(difference) < 2:
        return

    box = main_canvas.bbox("all")

    if not box:
        return

    content_height = max(1, box[3] - box[1])
    visible_height = main_canvas.winfo_height()

    max_position = max(
        0,
        1 - visible_height / content_height
    )

    new_position = (
        start_position[0] +
        difference / content_height
    )

    new_position = max(
        0,
        min(max_position, new_position)
    )

    main_canvas.yview_moveto(new_position)


def stop_scroll(event):
    drag_allowed[0] = False


main_canvas.bind_all(
    "<ButtonPress-1>",
    start_scroll,
    add="+"
)

main_canvas.bind_all(
    "<B1-Motion>",
    move_scroll,
    add="+"
)

main_canvas.bind_all(
    "<ButtonRelease-1>",
    stop_scroll,
    add="+"
)


# -----------------------------------------
# ONE CHAT WINDOW (a "panel")
# -----------------------------------------

class ChatPanel:

    def __init__(self, parent, title_text, default_name):

        self.connection = ChatConnection()
        self.name = ""

        card = tk.Frame(
            parent,
            bg=WHITE,
            highlightthickness=s(2),
            highlightbackground=LIGHT_BLUE,
            highlightcolor=LIGHT_BLUE
        )

        card.pack(
            fill="x",
            padx=s(40),
            pady=s(10)
        )

        title = tk.Label(
            card,
            text=title_text,
            bg=WHITE,
            fg=PRIMARY_BLUE,
            font=font(19, True)
        )

        title.pack(
            anchor="w",
            padx=s(28),
            pady=(s(20), s(8))
        )

        # Row 1: name and Join / Leave button
        top_row = tk.Frame(card, bg=WHITE)

        top_row.pack(
            fill="x",
            padx=s(28)
        )

        self.name_entry = tk.Entry(
            top_row,
            font=font(22),
            bg=ENTRY_BG,
            fg=TEXT_COLOR,
            relief="flat",
            highlightthickness=s(2),
            highlightbackground=LIGHT_BLUE,
            highlightcolor=PRIMARY_BLUE,
            disabledbackground=LIGHT_BLUE,
            disabledforeground=DARK_BLUE
        )

        self.name_entry.insert(0, default_name)

        self.join_button = tk.Button(
            top_row,
            text="JOIN",
            command=self.toggle_join,
            bg=DARK_BLUE,
            fg=WHITE,
            font=font(20, True),
            relief="flat",
            activebackground=LIGHT_BLUE,
            activeforeground=DARK_BLUE,
            width=7
        )

        self.join_button.pack(side="right", padx=(s(12), 0), ipady=s(6))
        self.name_entry.pack(side="left", fill="x", expand=True, ipady=s(10))

        self.status_label = tk.Label(
            card,
            text="Type a name and press JOIN",
            bg=WHITE,
            fg=GRAY_COLOR,
            font=font(17),
            wraplength=s(620),
            justify="left"
        )

        self.status_label.pack(
            anchor="w",
            padx=s(30),
            pady=(s(6), s(8))
        )

        # The messages
        self.text_box = tk.Text(
            card,
            height=8,
            wrap="word",
            bg=ENTRY_BG,
            fg=TEXT_COLOR,
            font=font(19),
            relief="flat",
            highlightthickness=s(2),
            highlightbackground=LIGHT_BLUE,
            state="disabled"
        )

        self.text_box.tag_config("notice", foreground=GRAY_COLOR, font=font(18, italic=True))
        self.text_box.tag_config("mine", foreground=PRIMARY_BLUE, font=font(19, bold=True))

        self.text_box.pack(
            fill="x",
            padx=s(28)
        )

        # Row 2: message box and Send button
        bottom_row = tk.Frame(card, bg=WHITE)

        bottom_row.pack(
            fill="x",
            padx=s(28),
            pady=(s(12), s(22))
        )

        self.message_entry = tk.Entry(
            bottom_row,
            font=font(22),
            bg=ENTRY_BG,
            fg=TEXT_COLOR,
            relief="flat",
            highlightthickness=s(2),
            highlightbackground=LIGHT_BLUE,
            highlightcolor=PRIMARY_BLUE
        )

        self.send_button = tk.Button(
            bottom_row,
            text="SEND",
            command=self.send_message,
            bg=PRIMARY_BLUE,
            fg=WHITE,
            font=font(20, True),
            relief="flat",
            activebackground=LIGHT_BLUE,
            activeforeground=DARK_BLUE,
            width=7
        )

        self.send_button.pack(side="right", padx=(s(12), 0), ipady=s(6))
        self.message_entry.pack(side="left", fill="x", expand=True, ipady=s(10))

        # Pressing Enter on a keyboard also sends
        self.message_entry.bind("<Return>", lambda event: self.send_message())

        # Start checking for new messages
        self.check_messages()

    # ----- helper functions -----

    def set_status(self, text, color):
        self.status_label.config(text=text, fg=color)

    def add_line(self, line):
        # Decide how the line should look
        tag = ""

        if not line.startswith("["):
            tag = "notice"
        elif " * " in line:
            tag = "notice"
        elif self.name and ("] " + self.name + ": ") in line:
            tag = "mine"

        self.text_box.config(state="normal")
        self.text_box.insert(tk.END, line + "\n", tag)
        self.text_box.config(state="disabled")
        self.text_box.see(tk.END)

    def show_left_state(self):
        # Screen when we are not connected
        self.join_button.config(text="JOIN")
        self.name_entry.config(state="normal")

    # ----- buttons -----

    def toggle_join(self):

        if self.connection.connected:
            self.leave()
        else:
            self.join()

    def join(self):

        name = self.name_entry.get().strip()

        if not name:
            self.set_status("Please type a name first.", ERROR_COLOR)
            return

        self.set_status("Connecting...", DARK_BLUE)
        root.update()

        ok, message = self.connection.join(name)

        if not ok:
            self.set_status(message, ERROR_COLOR)
            return

        self.name = name

        # Start with a clean message box
        self.text_box.config(state="normal")
        self.text_box.delete("1.0", tk.END)
        self.text_box.config(state="disabled")

        self.name_entry.config(state="disabled")
        self.join_button.config(text="LEAVE")
        self.set_status("Connected as " + name, GOOD_COLOR)

        self.check_messages(once=True)

    def leave(self):
        self.connection.leave()
        self.show_left_state()
        self.set_status("You left the chat.", GRAY_COLOR)

    def send_message(self):

        text = self.message_entry.get().strip()

        if not text:
            return

        if text.lower() == "/quit":
            self.message_entry.delete(0, tk.END)
            self.leave()
            return

        if not self.connection.connected:
            self.set_status("You are not connected. Press JOIN first.", ERROR_COLOR)
            return

        if self.connection.send(text):
            self.message_entry.delete(0, tk.END)
        else:
            self.set_status("The message could not be sent.", ERROR_COLOR)

    # ----- checking for new messages -----

    def check_messages(self, once=False):

        while True:
            try:
                line = self.connection.incoming.get_nowait()
            except queue.Empty:
                break

            self.add_line(line)

        # If the server closed the connection, update the screen
        if not self.connection.connected and self.join_button.cget("text") == "LEAVE":
            self.show_left_state()
            self.set_status("Disconnected from the server.", ERROR_COLOR)

        if not once:
            root.after(150, self.check_messages)


# -----------------------------------------
# HEADER
# -----------------------------------------

title = tk.Label(
    content,
    text="CHAT APPLICATION",
    bg=BG_COLOR,
    fg=DARK_BLUE,
    font=font(38, True)
)

title.pack(pady=(s(40), 0))

subtitle = tk.Label(
    content,
    text="Two people, one phone (demo)",
    bg=BG_COLOR,
    fg=PRIMARY_BLUE,
    font=font(22)
)

subtitle.pack(pady=(s(6), s(14)))

if chat_server is None:
    problem_label = tk.Label(
        content,
        text="Aarya_Task5_server.py was not found.\n"
             "Save it in the same folder as this file and run again.",
        bg=BG_COLOR,
        fg=ERROR_COLOR,
        font=font(19, True),
        wraplength=s(680)
    )

    problem_label.pack(pady=s(10))


# -----------------------------------------
# THE TWO CHAT WINDOWS
# -----------------------------------------

panel_one = ChatPanel(content, "PERSON 1", "Aarya")
panel_two = ChatPanel(content, "PERSON 2", "Friend")


# -----------------------------------------
# FOOTER
# -----------------------------------------

footer = tk.Label(
    content,
    text="The chat server runs inside this app | Made with Python",
    bg=BG_COLOR,
    fg=PRIMARY_BLUE,
    font=font(16)
)

footer.pack(
    pady=(s(10), s(35))
)


# -----------------------------------------
# CLOSING THE APP
# -----------------------------------------

def close_app():
    panel_one.connection.leave()
    panel_two.connection.leave()
    root.destroy()


root.protocol("WM_DELETE_WINDOW", close_app)


# -----------------------------------------
# RUN APPLICATION
# -----------------------------------------

root.mainloop()
          
