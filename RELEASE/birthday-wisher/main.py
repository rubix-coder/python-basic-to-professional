# To run and test the code you need to update 4 places:
# 1. Change MY_EMAIL/MY_PASSWORD to your own details.
# 2. Go to your email provider and make it allow less secure apps.
# 3. Update the SMTP ADDRESS to match your email provider.
# 4. Update birthdays.csv to contain today's month and day.
# See the solution video in the 100 Days of Python Course for explainations.


from datetime import datetime
import pandas
import random
import smtplib

MY_EMAIL = "*****@mail.com"
MY_PASSWORD = "*(d7ZO!Si449!QjNI"

today = datetime.now()
today_tuple = (today.month, today.day)

data = pandas.read_csv("birthdays.csv")
birthdays_dict = {data_row["name"]: (data_row["month"], data_row["day"]) for (index, data_row) in data.iterrows()}

birthday_buddies = [name for name in birthdays_dict.keys() if birthdays_dict[name] == today_tuple]

for buddy in birthday_buddies:
    file_path = f"letter_templates/letter_{random.randint(1, 3)}.txt"
    with open(file_path) as letter_file:
        contents = letter_file.read()
        contents = contents.replace("[NAME]", buddy)

    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(MY_EMAIL, MY_PASSWORD)
        connection.sendmail(
            from_addr=MY_EMAIL,
            to_addrs=birthdays_dict[buddy]["email"],
            msg=f"Subject:Happy Birthday! - testing project \n\n{contents}"
        )
