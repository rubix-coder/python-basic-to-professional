from tkinter import *

window = Tk()
# window.minsize(width=300, height=100)
window.config(padx=20, pady=20)
window.title("Mile to Km Converter")

# 1 Mile = 1.60934 Km
KM = 1.60934


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
window.mainloop()
