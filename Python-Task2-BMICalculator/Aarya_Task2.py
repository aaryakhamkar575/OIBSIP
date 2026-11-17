import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime
import math

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

COLOR_UNDER = "#438BA8"
COLOR_NORMAL = "#299D78"
COLOR_OVER = "#E6A23C"
COLOR_OBESE = "#D66B70"

DB_FILE = "bmi_records.db"


# -----------------------------------------
# DATABASE FUNCTIONS
# -----------------------------------------

def setup_database():
    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    weight REAL,
                    height REAL,
                    bmi REAL,
                    category TEXT,
                    date TEXT
                )
            """)
    except sqlite3.Error as error:
        messagebox.showerror("Database Error", str(error))


def save_record(name, weight, height, bmi, category):
    try:
        with sqlite3.connect(DB_FILE) as conn:
            now = datetime.now().strftime("%d-%m-%Y %H:%M")

            conn.execute("""
                INSERT INTO records
                (name, weight, height, bmi, category, date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, weight, height, bmi, category, now))

        return True

    except sqlite3.Error as error:
        messagebox.showerror("Database Error", str(error))
        return False


def get_records(name):
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT date, weight, bmi, category
                FROM records
                WHERE name = ? COLLATE NOCASE
                ORDER BY id DESC
            """, (name,))

            return cursor.fetchall()

    except sqlite3.Error as error:
        messagebox.showerror("Database Error", str(error))
        return []


# -----------------------------------------
# BMI CALCULATION
# -----------------------------------------

def calculate_bmi(weight, height):
    return weight / (height ** 2)


def get_category(bmi):

    if bmi < 18.5:
        return "Underweight", COLOR_UNDER

    elif bmi < 25:
        return "Normal", COLOR_NORMAL

    elif bmi < 30:
        return "Overweight", COLOR_OVER

    else:
        return "Obese", COLOR_OBESE


def healthy_weight_range(height):
    # Weight range that gives a Normal BMI (18.5 to 24.9)
    low = 18.5 * height ** 2
    high = 24.9 * height ** 2
    return round(low, 1), round(high, 1)


# -----------------------------------------
# CALCULATE BUTTON ACTION
# -----------------------------------------

def calculate():

    name = name_entry.get().strip()
    weight_text = weight_entry.get().strip()
    height_text = height_entry.get().strip()

    if not name:
        messagebox.showwarning(
            "Missing Name",
            "Please enter your name."
        )
        return

    try:
        weight = float(weight_text)
        height_input = float(height_text)

    except ValueError:
        messagebox.showwarning(
            "Invalid Input",
            "Please enter valid numbers for weight and height."
        )
        return

    if not math.isfinite(weight) or not math.isfinite(height_input):
        messagebox.showwarning(
            "Invalid Input",
            "Please enter valid numerical values."
        )
        return

    if weight <= 0 or height_input <= 0:
        messagebox.showwarning(
            "Invalid Values",
            "Weight and height must be greater than zero."
        )
        return

    if weight > 500:
        messagebox.showwarning(
            "Invalid Weight",
            "Please enter weight in kilograms."
        )
        return

    # Accept height in centimetres or metres
    if height_input > 3:
        height = height_input / 100
    else:
        height = height_input

    if height < 0.5 or height > 2.8:
        messagebox.showwarning(
            "Invalid Height",
            "Please enter a valid height in cm or metres."
        )
        return

    bmi = round(calculate_bmi(weight, height), 2)
    category, color = get_category(bmi)

    bmi_label.config(
        text=f"{bmi:.2f}",
        fg=color
    )

    category_label.config(
        text=category,
        fg=color
    )

    low, high = healthy_weight_range(height)

    range_label.config(
        text=f"Healthy weight for your height:\n{low} - {high} kg"
    )

    if save_record(name, weight, height, bmi, category):
        show_history()


# -----------------------------------------
# HISTORY FUNCTION
# -----------------------------------------

def show_history():

    name = name_entry.get().strip()

    if not name:
        messagebox.showwarning(
            "Missing Name",
            "Please enter your name first."
        )
        return

    history_list.delete(0, tk.END)

    rows = get_records(name)

    if not rows:
        history_list.insert(
            tk.END,
            "No previous records found."
        )
        return

    for row in rows:
        date, weight, bmi, category = row

        history_list.insert(
            tk.END,
            f"{date} | {weight:g} kg | BMI {bmi:.2f} | {category}"
        )


# -----------------------------------------
# BMI PROGRESS GRAPH
# -----------------------------------------

def show_graph():

    name = name_entry.get().strip()

    if not name:
        messagebox.showwarning(
            "Missing Name",
            "Please enter your name first."
        )
        return

    rows = get_records(name)

    if len(rows) < 2:
        messagebox.showinfo(
            "Not Enough Data",
            "Save at least 2 BMI records to view your graph."
        )
        return

    try:
        import matplotlib.pyplot as plt

    except ImportError:
        messagebox.showerror(
            "Missing Library",
            "Please install matplotlib using Pip."
        )
        return

    # Display records from oldest to newest
    rows.reverse()

    bmis = [row[2] for row in rows]

    # Record numbers (1, 2, 3...) so the line is always drawn correctly
    x_values = list(range(1, len(bmis) + 1))

    plt.figure(figsize=(9, 5))

    plt.plot(
        x_values,
        bmis,
        marker="o",
        linewidth=2,
        color=PRIMARY_BLUE
    )

    plt.title("BMI Progress - " + name)
    plt.xlabel("Record number")
    plt.ylabel("BMI")
    plt.grid(True, alpha=0.3)
    plt.xticks(x_values)
    plt.tight_layout()
    plt.show()


# -----------------------------------------
# MAIN WINDOW
# -----------------------------------------

root = tk.Tk()
root.title("Advanced BMI Calculator")

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

root.geometry(
    f"{screen_width}x{screen_height}+0+0"
)

root.configure(bg=BG_COLOR)

setup_database()


# -----------------------------------------
# DESKTOP-SITE SCALING
# -----------------------------------------
# The whole page is designed for a wide desktop screen (1000 px wide)
# and then shrunk to fit the real screen, like "Desktop site" in Chrome.
# So every size below goes through s() and every font through font().

DESIGN_WIDTH = 1000

SCALE = screen_width / DESIGN_WIDTH
SCALE = max(0.5, min(SCALE, 1.3))


def s(value):
    # Scale a size (padding, border, width...)
    return max(1, int(value * SCALE))


def font(size, bold=False):
    # Negative size means pixels, so it shrinks together with the layout
    if bold:
        return ("Arial", -s(size), "bold")
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
# NATURAL FINGER-DRAG SCROLLING
# -----------------------------------------

drag_start_y = [0]
start_position = [0.0]
drag_allowed = [False]


def start_scroll(event):

    widget_type = event.widget.winfo_class()

    # Do not interfere with buttons and input fields
    if widget_type in ("Entry", "Button", "Listbox"):
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

    region = main_canvas.cget("scrollregion")

    if not region:
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


# Mouse wheel support
def mouse_scroll(event):

    if event.delta:
        main_canvas.yview_scroll(
            int(-event.delta / 120),
            "units"
        )


main_canvas.bind_all(
    "<MouseWheel>",
    mouse_scroll,
    add="+"
)


# -----------------------------------------
# HEADER
# -----------------------------------------

header = tk.Frame(
    content,
    bg=BG_COLOR
)

header.pack(
    fill="x",
    padx=s(20),
    pady=(s(35), s(12))
)

title = tk.Label(
    header,
    text="BMI CALCULATOR",
    bg=BG_COLOR,
    fg=DARK_BLUE,
    font=font(46, True)
)

title.pack()

subtitle = tk.Label(
    header,
    text="Your personal health tracker",
    bg=BG_COLOR,
    fg=PRIMARY_BLUE,
    font=font(26)
)

subtitle.pack(pady=(s(6), 0))

tagline = tk.Label(
    header,
    text="A healthier you starts here",
    bg=BG_COLOR,
    fg=TEXT_COLOR,
    font=font(19)
)

tagline.pack(pady=(s(4), 0))


# -----------------------------------------
# DESKTOP LAYOUT: TWO COLUMNS OF CARDS
# -----------------------------------------

body = tk.Frame(
    content,
    bg=BG_COLOR
)

body.pack(
    fill="both",
    expand=True,
    padx=s(40),
    pady=(s(5), s(10))
)

# Two equal columns
body.columnconfigure(0, weight=1, uniform="columns")
body.columnconfigure(1, weight=1, uniform="columns")


def make_card(parent):

    return tk.Frame(
        parent,
        bg=WHITE,
        highlightthickness=s(2),
        highlightbackground=LIGHT_BLUE,
        highlightcolor=LIGHT_BLUE
    )


# Left card: inputs
left_card = make_card(body)

left_card.grid(
    row=0,
    column=0,
    sticky="nsew",
    padx=(0, s(15)),
    pady=s(10)
)

# Right card: result
right_card = make_card(body)

right_card.grid(
    row=0,
    column=1,
    sticky="nsew",
    padx=(s(15), 0),
    pady=s(10)
)

# Bottom card: records (full width)
history_card = make_card(body)

history_card.grid(
    row=1,
    column=0,
    columnspan=2,
    sticky="nsew",
    pady=s(10)
)


# -----------------------------------------
# INPUT FIELD FUNCTION
# -----------------------------------------

def make_field(parent, label_text, hint):

    label = tk.Label(
        parent,
        text=label_text,
        bg=WHITE,
        fg=DARK_BLUE,
        font=font(23, True),
        wraplength=s(380),
        justify="left"
    )

    label.pack(
        anchor="w",
        padx=s(28),
        pady=(s(18), s(6))
    )

    entry = tk.Entry(
        parent,
        font=font(25),
        bg=ENTRY_BG,
        fg=TEXT_COLOR,
        relief="flat",
        highlightthickness=s(2),
        highlightbackground=LIGHT_BLUE,
        highlightcolor=PRIMARY_BLUE
    )

    entry.pack(
        fill="x",
        padx=s(28),
        ipady=s(12)
    )

    hint_label = tk.Label(
        parent,
        text=hint,
        bg=WHITE,
        fg=PRIMARY_BLUE,
        font=font(17),
        wraplength=s(380),
        justify="left"
    )

    hint_label.pack(
        anchor="w",
        padx=s(30),
        pady=(s(5), 0)
    )

    return entry


# -----------------------------------------
# BUTTON FUNCTION
# -----------------------------------------

def make_button(parent, text, command, bg, fg):

    return tk.Button(
        parent,
        text=text,
        command=command,
        bg=bg,
        fg=fg,
        font=font(21, True),
        relief="flat",
        activebackground=LIGHT_BLUE,
        activeforeground=DARK_BLUE,
        cursor="hand2",
        wraplength=s(380),
        pady=s(16)
    )


# -----------------------------------------
# LEFT CARD: YOUR DETAILS
# -----------------------------------------

section_label = tk.Label(
    left_card,
    text="YOUR DETAILS",
    bg=WHITE,
    fg=PRIMARY_BLUE,
    font=font(21, True)
)

section_label.pack(
    anchor="w",
    padx=s(28),
    pady=(s(24), 0)
)

name_entry = make_field(
    left_card,
    "Your Name",
    "Enter your name or profile name"
)

weight_entry = make_field(
    left_card,
    "Weight (kg)",
    "Example: 55"
)

height_entry = make_field(
    left_card,
    "Height (cm or metres)",
    "Example: 172 or 1.72"
)

calc_button = make_button(
    left_card,
    "CALCULATE BMI",
    calculate,
    DARK_BLUE,
    WHITE
)

calc_button.pack(
    fill="x",
    padx=s(28),
    pady=(s(28), s(28))
)


# -----------------------------------------
# RIGHT CARD: RESULT
# -----------------------------------------

result_title = tk.Label(
    right_card,
    text="YOUR BMI RESULT",
    bg=WHITE,
    fg=PRIMARY_BLUE,
    font=font(21, True)
)

result_title.pack(
    anchor="w",
    padx=s(28),
    pady=(s(24), 0)
)

bmi_label = tk.Label(
    right_card,
    text="--",
    bg=WHITE,
    fg=PRIMARY_BLUE,
    font=font(80, True)
)

bmi_label.pack(pady=(s(20), s(4)))

category_label = tk.Label(
    right_card,
    text="Your result will appear here",
    bg=WHITE,
    fg=TEXT_COLOR,
    font=font(23, True),
    wraplength=s(380),
    justify="center"
)

category_label.pack(pady=(0, s(10)))

range_label = tk.Label(
    right_card,
    text="",
    bg=WHITE,
    fg=TEXT_COLOR,
    font=font(18),
    wraplength=s(380),
    justify="center"
)

range_label.pack(pady=(0, s(16)))

history_button = make_button(
    right_card,
    "VIEW BMI HISTORY",
    show_history,
    LIGHT_BLUE,
    DARK_BLUE
)

history_button.pack(
    fill="x",
    padx=s(28),
    pady=(s(10), s(10))
)

graph_button = make_button(
    right_card,
    "VIEW BMI PROGRESS GRAPH",
    show_graph,
    PRIMARY_BLUE,
    WHITE
)

graph_button.pack(
    fill="x",
    padx=s(28),
    pady=(0, s(28))
)


# -----------------------------------------
# BOTTOM CARD: PREVIOUS RECORDS
# -----------------------------------------

history_title = tk.Label(
    history_card,
    text="PREVIOUS RECORDS",
    bg=WHITE,
    fg=PRIMARY_BLUE,
    font=font(21, True)
)

history_title.pack(
    anchor="w",
    padx=s(28),
    pady=(s(24), s(12))
)

history_list = tk.Listbox(
    history_card,
    height=8,
    bg=ENTRY_BG,
    fg=TEXT_COLOR,
    font=font(20),
    relief="flat",
    highlightthickness=s(2),
    highlightbackground=LIGHT_BLUE
)

history_list.pack(
    fill="both",
    expand=True,
    padx=s(28),
    pady=(0, s(28))
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
    pady=(s(10), s(30))
)


# -----------------------------------------
# RUN APPLICATION
# -----------------------------------------

root.mainloop()
