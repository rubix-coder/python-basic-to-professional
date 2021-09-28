import tkinter.messagebox
from tkinter import *
from tkinter import messagebox
import random
import pyperclip
import ctypes
ctypes.windll.user32.ShowWindow( ctypes.windll.kernel32.GetConsoleWindow(), 6 )

# ---------------------------- PASSWORD GENERATOR ------------------------------- #
def generate_password():
    pwd.delete(0, END)
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
               'v',
               'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q',
               'R',
               'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    symbols = ['!', '#', '$', '%', '&', '(', ')', '*', '+']

    password_list = []

    password_list += [random.choice(letters) for _ in range(random.randint(8, 10))]
    password_list += [random.choice(numbers) for _ in range(random.randint(2, 4))]
    password_list += [random.choice(symbols) for _ in range(random.randint(2, 4))]

    random.shuffle(password_list)

    password = "".join(password_list)
    pwd.insert(0, f"{password}")
    pyperclip.copy(password)


# ---------------------------- SAVE PASSWORD ------------------------------- #

def save():
    try:
        if not path.get():
            with open(f"path.txt", mode="r") as file:
                PATH = file.read()
        else:
            PATH = path.get()
            with open(f"path.txt", mode="w") as file:
                file.write(PATH)

        web = website.get()
        username = user_name.get()
        pwd_val = pwd.get()

        if len(web) and len(username) and len(pwd_val) != 0:
            yes_no = messagebox.askyesno(title="Save",
                                         message=f"Website: {web} \nUsername/Email: {username} \n"
                                                 f"Password: {pwd_val} \n Would you like to continue? ")
            if yes_no:
                with open(f"{PATH}/data.csv", mode="a") as data_file:
                    data_file.write(f"{web} | {username} | {pwd_val}\n")
                    website.delete(0, END)
                    user_name.delete(0, END)
                    pwd.delete(0, END)
                    print("saved")

        else:
            messagebox.showinfo(title="Oops", message="Please don't leave any fields empty")

    except FileNotFoundError or FileExistsError or OSError:
        print("error")
        messagebox.showinfo(title="Oops", message="The file path doesn't exists.")


# ---------------------------- UI SETUP ------------------------------- #

window = Tk()
window.title("Password Manager")
window.config(padx=50, pady=50)

canvas = Canvas(width=200, height=200, highlightthickness=0)
logo_img = PhotoImage(file="logo.png")
canvas.create_image(100, 100, image=logo_img)
canvas.grid(row=0, column=1)

# Labels
web_label = Label(text="Website: ")
web_label.grid(row=1, column=0)

username_label = Label(text="Email/Username: ")
username_label.grid(row=2, column=0)

pwd_label = Label(text="Password: ")
pwd_label.grid(row=3, column=0)

path_label = Label(text="path: ")
path_label.grid(row=4, column=0)

# Entry
website = Entry(width=52)
website.grid(row=1, column=1, columnspan=2)
website.focus()

user_name = Entry(width=52)
user_name.grid(row=2, column=1, columnspan=2)
user_name.insert(END, "username@emaildomain.com")

pwd = Entry(width=32)
pwd.grid(row=3, column=1, padx=0)

path = Entry(width=52)
path.grid(row=4, column=1, columnspan=4)
path.insert(END, "C:\\users\\SKS\\Documents\\GitHub\\")
path.focus()

# Buttons
generate_button = Button(text="Generate Password", width=15, command=generate_password)
generate_button.grid(row=3, column=2, padx=0)

add_button = Button(text="Add", width=44, command=save)
add_button.grid(row=5, column=1, columnspan=2)

window.mainloop()
