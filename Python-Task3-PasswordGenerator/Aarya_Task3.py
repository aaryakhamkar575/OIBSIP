import tkinter as tk
import string
import secrets

# -----------------------------------------
# PROJECT: RANDOM PASSWORD GENERATOR
# Oasis Infobyte Python Programming Internship - Task 3
# -----------------------------------------

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

COLOR_WEAK = "#D66B70"
COLOR_MEDIUM = "#E6A23C"
COLOR_STRONG = "#299D78"

MIN_LENGTH = 8
MAX_LENGTH = 40


# -----------------------------------------
# PASSWORD FUNCTIONS
# -----------------------------------------

def make_password(length, groups):
    # groups = the lists of characters the user selected

    # 1. Take ONE character from each selected list
    #    (this guarantees every selected type is used)
    password_chars = []

    for group in groups:
        password_chars.append(secrets.choice(group))

    # 2. Fill the remaining spots with random characters
    all_characters = "".join(groups)

    while len(password_chars) < length:
        password_chars.append(secrets.choice(all_characters))

    # 3. Mix the order so the password is not predictable
    secrets.SystemRandom().shuffle(password_chars)

    return "".join(password_chars)


def get_strength(length, types_count):
    # Points for length
    if length >= 16:
        points = 3
    elif length >= 12:
        points = 2
    else:
        points = 1

    # Points for variety (2, 3 or 4 character types)
    points = points + (types_count - 1)

    if points >= 5:
        return "Strong", COLOR_STRONG
    elif points == 4:
        return "Medium", COLOR_MEDIUM
    else:
        return "Weak", COLOR_WEAK


# -----------------------------------------
# BUTTON ACTIONS
# -----------------------------------------

def update_length(value):
    length_label.config(
        text="Password length: " + str(int(float(value)))
    )


def show_error(message):
    # Show the error and clear the old password, so the screen never
    # shows a password that does not match the current options
    error_label.config(text=message)
    password_var.set("")
    strength_label.config(text="Strength: -", fg=TEXT_COLOR)
    copy_button.config(text="COPY TO CLIPBOARD")


def generate():

    length = length_slider.get()

    # Collect the character lists the user selected
    groups = []

    if upper_var.get():
        groups.append(string.ascii_uppercase)

    if lower_var.get():
        groups.append(string.ascii_lowercase)

    if numbers_var.get():
        groups.append(string.digits)

    if symbols_var.get():
        groups.append(string.punctuation)

    # Validation
    if length < MIN_LENGTH:
        show_error("Length must be at least 8 characters.")
        return

    if len(groups) < 2:
        show_error("Please select at least 2 character types.")
        return

    # Everything is fine, so make the password
    error_label.config(text="")

    password = make_password(length, groups)
    password_var.set(password)

    strength, color = get_strength(length, len(groups))

    strength_label.config(
        text="Strength: " + strength,
        fg=color
    )

    copy_button.config(text="COPY TO CLIPBOARD")


def copy_password():

    password = password_var.get()

    if not password:
        error_label.config(
            text="Generate a password first."
        )
        return

    root.clipboard_clear()
    root.clipboard_append(password)
    root.update()

    error_label.config(text="")
    copy_button.config(text="COPIED!")


# -----------------------------------------
# MAIN WINDOW
# -----------------------------------------

root = tk.Tk()
root.title("Password Generator")

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

root.geometry(
    f"{screen_width}x{screen_height}+0+0"
)

root.configure(bg=BG_COLOR)


# -----------------------------------------
# SCALING (so everything fits the screen)
# -----------------------------------------
# The page is designed for 800 px width and then scaled to the real screen.

DESIGN_WIDTH = 800

SCALE = screen_width / DESIGN_WIDTH
SCALE = max(0.5, min(SCALE, 1.3))


def s(value):
    return max(1, int(value * SCALE))


def font(size, bold=False):
    if bold:
        return ("Arial", -s(size), "bold")
    return ("Arial", -s(size))


# Variables connected to the checkboxes and the password box
upper_var = tk.BooleanVar(value=True)
lower_var = tk.BooleanVar(value=True)
numbers_var = tk.BooleanVar(value=True)
symbols_var = tk.BooleanVar(value=False)
password_var = tk.StringVar(value="")


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

    # Do not scroll when touching buttons, boxes, checkboxes or the slider
    if widget_type in ("Entry", "Button", "Scale", "Checkbutton"):
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
# HEADER
# -----------------------------------------

title = tk.Label(
    content,
    text="PASSWORD GENERATOR",
    bg=BG_COLOR,
    fg=DARK_BLUE,
    font=font(38, True)
)

title.pack(pady=(s(40), 0))

subtitle = tk.Label(
    content,
    text="Create strong, random passwords",
    bg=BG_COLOR,
    fg=PRIMARY_BLUE,
    font=font(22)
)

subtitle.pack(pady=(s(6), s(20)))


# -----------------------------------------
# CARD 1: OPTIONS
# -----------------------------------------

options_card = tk.Frame(
    content,
    bg=WHITE,
    highlightthickness=s(2),
    highlightbackground=LIGHT_BLUE,
    highlightcolor=LIGHT_BLUE
)

options_card.pack(
    fill="x",
    padx=s(40),
    pady=s(10)
)

options_title = tk.Label(
    options_card,
    text="YOUR OPTIONS",
    bg=WHITE,
    fg=PRIMARY_BLUE,
    font=font(19, True)
)

options_title.pack(
    anchor="w",
    padx=s(28),
    pady=(s(24), s(10))
)

length_label = tk.Label(
    options_card,
    text="Password length: 12",
    bg=WHITE,
    fg=DARK_BLUE,
    font=font(23, True)
)

length_label.pack(
    anchor="w",
    padx=s(28),
    pady=(s(8), s(4))
)

length_slider = tk.Scale(
    options_card,
    from_=MIN_LENGTH,
    to=MAX_LENGTH,
    orient="horizontal",
    showvalue=False,
    sliderlength=s(70),
    width=s(36),
    bg=WHITE,
    troughcolor=LIGHT_BLUE,
    activebackground=PRIMARY_BLUE,
    highlightthickness=0,
    bd=0,
    command=update_length
)

length_slider.set(12)

length_slider.pack(
    fill="x",
    padx=s(28),
    pady=(0, s(10))
)

types_label = tk.Label(
    options_card,
    text="Include (choose at least 2):",
    bg=WHITE,
    fg=DARK_BLUE,
    font=font(23, True)
)

types_label.pack(
    anchor="w",
    padx=s(28),
    pady=(s(14), s(6))
)


def make_checkbox(text, variable):

    box = tk.Checkbutton(
        options_card,
        text=text,
        variable=variable,
        bg=WHITE,
        fg=TEXT_COLOR,
        activebackground=WHITE,
        selectcolor=ENTRY_BG,
        font=font(21),
        anchor="w"
    )

    box.pack(
        fill="x",
        padx=s(24),
        pady=s(3)
    )


make_checkbox("Uppercase letters (A-Z)", upper_var)
make_checkbox("Lowercase letters (a-z)", lower_var)
make_checkbox("Numbers (0-9)", numbers_var)
make_checkbox("Symbols (!@#$...)", symbols_var)

generate_button = tk.Button(
    options_card,
    text="GENERATE PASSWORD",
    command=generate,
    bg=DARK_BLUE,
    fg=WHITE,
    font=font(22, True),
    relief="flat",
    activebackground=LIGHT_BLUE,
    activeforeground=DARK_BLUE,
    pady=s(16)
)

generate_button.pack(
    fill="x",
    padx=s(28),
    pady=(s(22), s(10))
)

error_label = tk.Label(
    options_card,
    text="",
    bg=WHITE,
    fg=COLOR_WEAK,
    font=font(18),
    wraplength=s(620)
)

error_label.pack(
    padx=s(28),
    pady=(0, s(20))
)


# -----------------------------------------
# CARD 2: RESULT
# -----------------------------------------

result_card = tk.Frame(
    content,
    bg=WHITE,
    highlightthickness=s(2),
    highlightbackground=LIGHT_BLUE,
    highlightcolor=LIGHT_BLUE
)

result_card.pack(
    fill="x",
    padx=s(40),
    pady=s(10)
)

result_title = tk.Label(
    result_card,
    text="YOUR PASSWORD",
    bg=WHITE,
    fg=PRIMARY_BLUE,
    font=font(19, True)
)

result_title.pack(
    anchor="w",
    padx=s(28),
    pady=(s(24), s(10))
)

# Read-only box: you can also long-press the text to copy it
password_entry = tk.Entry(
    result_card,
    textvariable=password_var,
    state="readonly",
    readonlybackground=ENTRY_BG,
    fg=DARK_BLUE,
    font=("Courier", -s(24), "bold"),
    justify="center",
    relief="flat",
    highlightthickness=s(2),
    highlightbackground=LIGHT_BLUE,
    highlightcolor=PRIMARY_BLUE
)

password_entry.pack(
    fill="x",
    padx=s(28),
    ipady=s(14)
)

strength_label = tk.Label(
    result_card,
    text="Strength: -",
    bg=WHITE,
    fg=TEXT_COLOR,
    font=font(23, True)
)

strength_label.pack(
    pady=(s(16), s(6))
)

copy_button = tk.Button(
    result_card,
    text="COPY TO CLIPBOARD",
    command=copy_password,
    bg=PRIMARY_BLUE,
    fg=WHITE,
    font=font(22, True),
    relief="flat",
    activebackground=LIGHT_BLUE,
    activeforeground=DARK_BLUE,
    pady=s(16)
)

copy_button.pack(
    fill="x",
    padx=s(28),
    pady=(s(10), s(28))
)


# -----------------------------------------
# FOOTER
# -----------------------------------------

footer = tk.Label(
    content,
    text="Made with Python | Ocean Breeze Edition",
    bg=BG_COLOR,
    fg=PRIMARY_BLUE,
    font=font(16)
)

footer.pack(
    pady=(s(10), s(35))
)


# -----------------------------------------
# RUN APPLICATION
# -----------------------------------------

root.mainloop()
