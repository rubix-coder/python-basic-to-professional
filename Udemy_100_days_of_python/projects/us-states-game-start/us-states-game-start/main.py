import turtle
import pandas as pd

screen = turtle.Screen()
screen.title("U.S. States Game")
screen.addshape("blank_states_img.gif")
turtle.shape("blank_states_img.gif")

is_game_on = True

states_df = pd.read_csv("50_states.csv")
score = 0
answered = []
with open("missing_states.csv", mode="w") as file:
    file.write("")


def is_state_present(state):
    if state in list(states_df["state"]):
        answered.append(state)
        global score
        score += 1
        return True
    else:
        return False


def plot_state(state):
    plot = turtle.Turtle()
    select_state = states_df[states_df["state"] == state]
    x_cor = int(select_state["x"])
    y_cor = int(select_state["y"])
    plot.penup()
    plot.hideturtle()
    plot.goto(x_cor, y_cor)
    plot.write(state)


def export_unanswered():
    global answer_state
    unanswered = set(states_df["state"]).symmetric_difference(set(answered))
    for state in unanswered:
        with open("missing_states.csv", mode="a") as new_file:
            new_file.write(f"{state}\n")


while is_game_on:
    answer_state = screen.textinput(title=f'{score}/{states_df["state"].count()} Guessed',
                                    prompt="What's another state's name?").title()
    if answer_state == "Exit" or score == states_df["state"].count():
        export_unanswered()
        is_game_on = False
    if answer_state:
        if is_state_present(answer_state):
            plot_state(answer_state)
