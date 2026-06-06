from tkinter import *


def button_clicked():
    my_label.config(text=input.get())
    print("I got clicked")


window = Tk()
window.title("My first GUI")
window.minsize(width=500, height=300)

window.config(padx=100, pady= 200)
# Label
my_label = Label(text="I am a Label", font=("Arial", 24))
my_label.grid(column=0, row=0)

# Button
button = Button(text="Button 1", command=button_clicked)
button.grid(column=1, row=1)
button.config(padx=50, pady=50)
# Button_new
button_new = Button(text="Button 2", command=button_clicked)
button_new.grid(column=2, row=0)

# Entry
input = Entry(width=10)
input.grid(column=3, row=2)

print(input.get())

window.mainloop()
