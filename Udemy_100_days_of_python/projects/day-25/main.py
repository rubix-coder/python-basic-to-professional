# # with open("weather_data.csv") as data_file:
# #     data = data_file.readlines()
# #     print(data[1:])
#
#
# # import csv
# #
# # with open("weather_data.csv") as data_file:
# #     data = csv.reader(data_file)
# #     temperature = []
# #     for row in data:
# #         if row[1] != "temp":
# #             temperature.append(int(row[1]))
#
import pandas as pd

#
# data = pd.read_csv("weather_data.csv")
# data["temp"] = data["temp"].astype('int')
# print(f'Average temperature: {data["temp"].mean()}')
# print(f'Maximum temperature: {data["temp"].max()}')
# print(data[data["temp"] == data["temp"].max()])
#
# monday = data[data["day"] == "Monday"]
# monday_temp = int(monday["temp"])
# monday_temp_f = monday_temp * (9/5) +35
# print(f"Temp: {monday_temp_f}F")

# TODO: csv with squirrel count - fur colours | count squirrel
data = pd.read_csv("2018_Central_Park_Squirrel_Census_-_Squirrel_Data.csv")
squirrel_df = pd.DataFrame()

squirrel_df["Count"] = data["Primary Fur Color"].groupby(data["Primary Fur Color"]).agg('count')
print(squirrel_df)
squirrel_df.to_csv("squirrel_data.csv")
