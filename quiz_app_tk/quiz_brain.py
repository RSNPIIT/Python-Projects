import html

class QuizBrain:

    def __init__(self, q_list):
        self.question_number = 0
        self.score = 0
        self.is_corr = None
        self.question_list = q_list
        self.current_question = None

    def still_has_questions(self):
        return self.question_number < len(self.question_list)

    def next_question(self):
        self.current_question = self.question_list[self.question_number]
        self.question_number += 1
        my_tex = html.unescape(self.current_question.text)
        return f"Q.{self.question_number}: {my_tex}"
        # user_answer = input(f""Q.{self.question_number}: {my_tex} (True/False): ").strip().lower()
        # self.check_answer(user_answer)

    def check_answer(self, user_answer):
        correct_answer = self.current_question.answer
        if user_answer.lower() == correct_answer.lower():
            self.score += 1
            self.is_corr = True
            # msg.showinfo(title = 'GREAT' , message = 'CORRECT ANSWER')
        else:
            self.score += 0
            self.is_corr = False
            # msg.showinfo(title = 'OH NO !' , message = 'WRONG ANSWER')
