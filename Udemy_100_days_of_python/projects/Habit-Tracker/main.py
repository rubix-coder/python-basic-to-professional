import requests
from datetime import datetime

pixela_endpoint = "https://pixe.la/v1/users"
USERNAME = "rubix"
TOKEN = "#I2ngFkYi%j9(84Q!"
GRAPH_ID = "graph1"
user_params = {
    "token": TOKEN,
    "username": USERNAME,
    "agreeTermsofService": "yes",
    "notMinor": "yes",
}
# response = requests.post(url=pixela_endpoint, json=user_params)
# print(response.text)

graph_endpoint = f"{pixela_endpoint}/{USERNAME}/graphs"

graph_config = {
    "id": GRAPH_ID,
    "name": "Book Reading Graph",
    "unit": "pages",
    "type": "int",
    "color": "sora",
}

headers = {
    "X-USER-TOKEN": TOKEN
}

# response = requests.post(url=graph_endpoint, json=graph_config, headers=headers)
# print(response.text)

y = datetime(year=2021, month=10, day=6)
t = datetime.now()
today = t.strftime("%Y%m%d")
yesterday = y.strftime("%Y%m%d")

pixel_endpoint = f"{graph_endpoint}/{GRAPH_ID}"
pixel_data = {
    "date": yesterday,
    "quantity": "8",
}
#
# response = requests.post(url=pixel_endpoint, json=pixel_data, headers=headers)
# print(response.text)

response = requests.delete(url=f"{pixel_endpoint}/{yesterday}", headers=headers)
print(response.text)
