import requests
import pandas as pd
import smtplib
import os
MY_EMAIL = "******.*****@mail.com"
MY_PASSWORD = "*(d7ZO!Si449!QjNI"
API_KEY = "*********************************"

URL = f"https://api.openweathermap.org/data/2.5/onecall"

contacts = pd.read_csv("contacts.csv")

email_dict = {values["name"]: [values["email"], (values["lat"], values["lon"])] for member, values in
              contacts.iterrows()}

for member in email_dict:
    parameters = {
        "lat": email_dict[member][1][0],
        "lon": email_dict[member][1][1],
        "appid": API_KEY,
        "exclude": "current,minutely,daily"
    }

    response = requests.get(URL, params=parameters)
    response.raise_for_status()
    weather_data = pd.DataFrame(response.json()["hourly"][0:12])
    rainy = [True for hour in range(12) if weather_data["weather"][hour][0]["id"] < 700]
    if rainy:
        contents = f"Hey {member.title()}! \nIt's gonna rain. \nBring an Umbrella."
    else:
        contents = f"There is no rain. \nHave a nice day {member.title()}"

    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(MY_EMAIL, MY_PASSWORD)
        connection.sendmail(
            from_addr=MY_EMAIL,
            to_addrs=email_dict[member][0],
            msg=f"Subject:Rain check update from Jesal \n\n{contents}"
        )
    print(f"Hey {member.title()}! \nIt's gonna rain. \nBring an Umbrella.") if rainy else print(
        f"There is no rain. \nHave a nice day {member.title()}")
