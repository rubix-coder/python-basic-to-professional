from tkinter import *
import requests

Kanye_quote_API = "https://api.kanye.rest"
sun_rise_set_API = "https://api.sunrise-sunset.org/json?lat=36.7201600&lng=-4.4203400&formatted=0"
def get_quote():
    response = requests.get(url=Kanye_quote_API)
    canvas.itemconfig(quote_text, text=response.json()["quote"])
    # Write your code here.


window = Tk()
window.title("Kanye Says...")
window.config(padx=50, pady=50)

canvas = Canvas(width=300, height=414)
background_img = PhotoImage(file="background.png")
canvas.create_image(150, 207, image=background_img)
quote_text = canvas.create_text(150, 207, text="Kanye Quote Goes HERE", width=250, font=("Arial", 20, "bold"),
                                fill="white")
canvas.grid(row=0, column=0)

kanye_img = PhotoImage(file="kanye.png")
kanye_button = Button(image=kanye_img, highlightthickness=0, command=get_quote)
kanye_button.grid(row=1, column=0)

window.mainloop()
