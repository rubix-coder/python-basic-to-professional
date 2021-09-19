# with open("my_file.txt") as f:
#     print(f.read())

with open("new_file.txt", mode="a") as f:
    print(f.write("New text \n"))
