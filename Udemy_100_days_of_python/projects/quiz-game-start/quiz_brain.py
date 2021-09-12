class QuizBrain:

    def __init__(self, question_list):
        self.question_number = 0
        self.score = 0
        self.question_list = question_list

    def still_has_questions(self):
        return self.question_number < len(self.question_list)

    def next_question(self):
        question = self.question_list[self.question_number]
        self.question_number += 1
        user_ans = input(f"Q.{self.question_number}: {question.text} (True/False)?: ")
        self.check_answer(user_ans, question.answer)

    def check_answer(self, user_answer, correct_answer):
        if user_answer.lower() == correct_answer.lower():
            self.score += 1
            print("You got it right!")
        else:
            print("That's wrong.")
        print(f"The correct answer is {correct_answer}")
        print(f"Your score is: {self.score}/{self.question_number}.\n")


# TODO: asking the questions

# TODO: checking if the answer was correct

# TODO: checking if we're the end of the game
