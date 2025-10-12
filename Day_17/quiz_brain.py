class QuizBrain:
    def __init__(self,q_list):
        self.question_no = 0
        self.score = 0
        self.question_list = q_list

    def still_has_questions(self):
        if self.question_no < len(self.question_list):
            return True
        else:
            return False

    def next_question(self):
        current_question = self.question_list[self.question_no]
        self.question_no += 1
        user_ans = input(f"Q - {self.question_no} - {current_question.text} (True/False) : ").strip().lower()
        self.check_ans(user_ans , current_question.answer)

    def check_ans(self,user_ans,corr_ans):
        if user_ans == corr_ans.lower():
            self.score += 1
            print(f"You got it right \nThe correct answer is : {user_ans.title()}")
            print(f"Your Score is : {self.score}")
        else:
            self.score += 0
            print(f"You got it wrong \nThe correct answer was {corr_ans.title()}")
            print(f"Your Score is : {self.score}")
