from tkinter import *
import ctypes
import webbrowser
ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 6)

window = Tk()
# window.minsize(width=300, height=100)
window.config(padx=20, pady=20)
window.title("Mile to Km Converter")

# 1 Mile = 1.60934 Km
KM = 1.60934

def web_page():
    webbrowser.open_new_tab(r"https://www.linkedin.com/in/jesalpatelindia/")

def calculate():
    # Output Label
    to_km = round(float(input_box.get()) * KM, 4)
    output.config(text=to_km)


# Entry box
input_box = Entry(width=7)
input_box.grid(column=1, row=0)

# Miles Label
miles = Label(text="Miles")
miles.grid(column=2, row=0)

# Km Label
miles = Label(text="Km")
miles.grid(column=2, row=1)

# is equal to Label
equals = Label(text="is equal to")
equals.grid(column=0, row=1)

output = Label(text="0")
output.grid(column=1, row=1)

# calculate button
button_calc = Button(text="Calculate", command=calculate)
button_calc.grid(column=1, row=2)

# Dev Label
dev = Button(text="help",
             font=("Courier", 8, "bold"), fg="blue", bg="white", command=web_page)
dev.bind("link",webbrowser)
dev.grid(row=3,column=0)

window.mainloop()
