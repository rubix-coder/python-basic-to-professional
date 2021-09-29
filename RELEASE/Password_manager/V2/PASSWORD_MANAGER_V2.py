import json
import tkinter.messagebox
from tkinter import *
from tkinter import messagebox
import random
import pyperclip
import ctypes
import webbrowser

ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 6)


# ---------------------------- developer website ------------------------------- #
def web_page():
    webbrowser.open_new_tab(r"https://www.linkedin.com/in/jesalpatelindia/")


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


# ---------------------------- CHECK PATH FILE ------------------------------- #

def check_file():
    try:
        if path.get():
            with open(f"path.txt", mode="r") as file:
                PATH = file.read()
        else:
            PATH = path.get()
            with open(f"path.txt", mode="w") as file:
                file.write(PATH)

    except FileNotFoundError or FileExistsError or OSError:
        messagebox.showinfo(title="Oops", message="The file path doesn't exists.")
    return PATH


# ---------------------------- SAVE PASSWORD ------------------------------- #

def save():
    web = website.get()
    username = user_name.get()
    pwd_val = pwd.get()
    new_data = {
        web: {
            'email': username,
            'password': pwd_val,
        }
    }
    if len(web) == 0 or len(username) == 0 or len(pwd_val) == 0:
        messagebox.showwarning(title="Oops", message="Please don't leave any fields empty")
    else:
        try:
            with open(f"data.json", mode="r") as data_file:
                data = json.load(data_file)
                data.update(new_data)

        except FileNotFoundError:
            with open(f"data.json", mode="w") as data_file:
                json.dump(new_data, data_file, indent=4)

        else:
            with open(f"data.json", mode="w") as data_file:
                json.dump(data, data_file, indent=4)

        finally:
            website.delete(0, END)
            user_name.delete(0, END)
            pwd.delete(0, END)


# ---------------------------- LOAD PASSWORD ------------------------------- #
def search():
    if website.get():
        try:
            with open(f"data.json", mode="r") as data_file:
                data = json.load(data_file)
                pyperclip.copy(data[website.get()]['password'])
                messagebox.showinfo(title=f"{website.get()}",
                                    message=f"username/email: {data[website.get()]['email']} \n"
                                            f"password: {data[website.get()]['password']} \n"
                                            f"\npassword copied to clipboard use ctrl+p to use.")
        except KeyError:
            messagebox.showerror(title="Error", message=f"No data found for website: {website.get()}")
            
        except FileNotFoundError:
            messagebox.showerror(title="Error", message=f"No data found for website: {website.get()}")
    else:
        messagebox.showwarning(title="Oops", message="Please enter the website")


# ---------------------------- UI SETUP ------------------------------- #

window = Tk()
window.title("Password Manager")
window.config(padx=25, pady=25)

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

# path_label = Label(text="path: ")
# path_label.grid(row=4, column=0)

# Entry
website = Entry(width=32)
website.grid(row=1, column=1)
website.focus()

user_name = Entry(width=52)
user_name.grid(row=2, column=1, columnspan=2)
user_name.insert(END, "username@emaildomain.com")

pwd = Entry(width=32)
pwd.grid(row=3, column=1, padx=0)


# Buttons
generate_button = Button(text="Generate Password", width=15, command=generate_password)
generate_button.grid(row=3, column=2, padx=0)

add_button = Button(text="Add", width=44, command=save)
add_button.grid(row=5, column=1, columnspan=2)

search_button = Button(text="Search", width=15, command=search)
search_button.grid(row=1, column=2, padx=0)

# Dev Label
dev = Button(text="help",
             font=("Courier", 8, "bold"), fg="blue", bg="white", command=web_page)
dev.bind("link", webbrowser)
dev.grid(row=6, column=0)

window.mainloop()
