import math
from tkinter import *
import winsound
import webbrowser

# ---------------------------- CONSTANTS ------------------------------- #
PINK = "#e2979c"
RED = "#e7305b"
GREEN = "#9bdeac"
YELLOW = "#f7f5dd"
FONT_NAME = "Courier"
WORK_MIN = 25
SHORT_BREAK_MIN = 5
LONG_BREAK_MIN = 20
reps = 0
timer = None


# ---------------------------- OPEN WEBSITE ------------------------------ #
def web_page():
    webbrowser.open_new_tab(r"https://www.linkedin.com/in/jesalpatelindia/")


# ---------------------------- NOTIFY BEEP ------------------------------- #
def play_beep(times):
    frequency = 1000  # Set Frequency To 2500 Hertz
    duration = 200  # Set Duration To 1000 ms == 1 second
    for _ in range(times):
        winsound.Beep(frequency, duration)


# ---------------------------- TIMER RESET ------------------------------- #
def reset_timer():
    window.after_cancel(timer)
    global reps
    reps = 0
    canvas.itemconfig(timer_text, text="00:00")
    timer_label.config(text="Timer")
    marks = ""
    tick_label.config(text=marks)


# ---------------------------- TIMER MECHANISM ------------------------------- #
def start_timer():
    global reps
    reps += 1
    if reps in [1, 3, 5, 7]:
        timer_label.config(text="Work", fg=GREEN)
        count_down(WORK_MIN * 60)
        play_beep(1)

    elif reps in [2, 4, 6]:
        timer_label.config(text="Break", fg=PINK)
        count_down(SHORT_BREAK_MIN * 60)
        play_beep(1)

    elif reps == 8:
        timer_label.config(text="Break", fg=RED)
        count_down(LONG_BREAK_MIN * 60)
        play_beep(2)

    elif reps == 9:
        timer_label.config(text="Great!", fg=RED)
        play_beep(4)

    # print(f"reps: {reps}")


# ---------------------------- COUNTDOWN MECHANISM ------------------------------- #
def count_down(count):
    count_min = math.floor(count / 60)
    count_sec = count % 60
    if count_sec < 10:
        count_sec = f"0{count_sec}"
    if count_min < 10:
        count_min = f"0{count_min}"

    canvas.itemconfig(timer_text, text=f"{count_min}:{count_sec}")
    if count > 0:
        global timer
        timer = window.after(1000, count_down, count - 1)
    else:
        start_timer()
        marks = ""
        work_sessions = math.floor(reps / 2)
        for _ in range(work_sessions):
            marks += "✔"
        tick_label.config(text=marks)


# ---------------------------- UI SETUP ------------------------------- #
window = Tk()
window.title("Pomodoro")
window.config(padx=25, pady=50, bg=YELLOW)

canvas = Canvas(width=200, height=224, bg=YELLOW, highlightthickness=0)
tomato_img = PhotoImage(file="tomato.png")
canvas.create_image(100, 112, image=tomato_img)
timer_text = canvas.create_text(100, 130, text="00:00", fill="white", font=(FONT_NAME, 25, "bold"))
canvas.grid(column=1, row=1)

# Timer Label
timer_label = Label(text="Timer", font=(FONT_NAME, 25, "bold"), fg=GREEN, bg=YELLOW)
timer_label.grid(column=1, row=0)

# Start button
start_button = Button(text="Start", highlightthickness=0, command=start_timer)
start_button.grid(column=0, row=2)

# Reset button
reset_button = Button(text="Reset", highlightthickness=0, command=reset_timer)
reset_button.grid(column=2, row=2)

# Tick Label
tick_label = Label(font=(FONT_NAME, 20, "bold"), fg=GREEN, bg=YELLOW)
tick_label.grid(column=1, row=3)

# disclaimer Label
disc = Label(text="Once you get 4 x ✔, \nhit 'reset' and then \n'start' to continue ",
             font=(FONT_NAME, 10, "bold"), fg=RED, bg=YELLOW)
disc.grid(column=1, row=4)

# Dev Label
dev = Button(text="Dev: Jesal P.",
             font=(FONT_NAME, 8, "bold"), fg="blue", bg=YELLOW, command=web_page)
dev.bind("link",webbrowser)
dev.grid(column=1, row=5)

window.mainloop()
