import os

import requests
import datetime as dt

t = dt.datetime.now()
today = t.strftime("%d/%m/%Y")
today_time = t.strftime("%H:%M:%S")

APP_ID = os.environ["APP_ID"]
API_KEY = os.environ["API_KEY"]
USERNAME = os.environ["USERNAME"]
PROJECT_NAME = "exerciseTracking"
SHEET_NAME = "workouts"
GENDER = "male"
WEIGHT_KG = 80
HEIGHT_CM = 157
AGE = 27
headers = {
    "x-app-id": APP_ID,
    "x-app-key": API_KEY,
}

request_body = {
    "query": input("Tell me which exercises you did: "),
    "gender": GENDER,
    "weight_kg": WEIGHT_KG,
    "height_cm": HEIGHT_CM,
    "age": AGE
}

auth = (os.environ["UNAME"],os.environ["PWD"])
nutritionix_endpoint = "https://trackapi.nutritionix.com/v2/natural/exercise"
sheety_endpoint = f"https://api.sheety.co/{USERNAME}/{PROJECT_NAME}/{SHEET_NAME}"

nutritionix_data = requests.post(url=nutritionix_endpoint, json=request_body, headers=headers)
n = nutritionix_data.json()

for exercise in n["exercises"]:
    msg_body = {
        "workout": {
            "date": today,
            "time": today_time,
            "exercise": exercise["name"].title(),
            "duration": exercise["duration_min"],
            "calories": exercise["nf_calories"]
        }
    }
    sheety_data = requests.post(url=sheety_endpoint, json=msg_body, auth= auth)
    print(sheety_data.text)
