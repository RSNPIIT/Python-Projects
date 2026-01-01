#Static Variables
BLACK = '#000000'
WHITE = '#FFFFFF'
TICK_FILE = 'images/true.png'
CROSS_FILE = 'images/false.png'
TRUE = 'true'
FALSE = 'false'
AST = 'normal'
ST = 'disabled'
GREEN = '#008000'
RED = '#D2042D'

#File Starts Here
import tkinter as tk
from tkinter import messagebox as msg
from quiz_brain import QuizBrain

#The Class Starts Here
class TK_UI:
    
    def __init__(self , quizbrain : QuizBrain):
        self.quiz = quizbrain
        self.sc = tk.Tk()
        self.sc.title('Quizzler')
        self.sc.config(padx = 20 , pady = 20 , bg = BLACK)
        
        #Label UI
        self.score_l = tk.Label(master = self.sc , text = f"Score : {self.quiz.score}" , fg = WHITE , bg = BLACK)
        self.score_l.grid(column = 1 , row = 0)

        #Canvas UI that will have the Label
        self.cv = tk.Canvas(master = self.sc , width = 300 , height = 300 , bg = WHITE )
        self.txr = self.cv.create_text(150 , 150 , width = 280 , text = 'Some Sample Text' , fill = BLACK)
        self.cv.grid(column = 1 , row = 1)

        tick = tk.PhotoImage(file = TICK_FILE)
        self.tb = tk.Button(master = self.sc , image = tick , command = self.tick_keypress , highlightthickness = 0)
        self.tb.grid(column = 0 , row = 2)

        cross = tk.PhotoImage(file = CROSS_FILE)
        self.tc = tk.Button(master = self.sc , image = cross , command = self.cross_keypress , highlightthickness = 0)
        self.tc.grid(column = 2 , row = 2)

        self.get_next()
        self.sc.mainloop()

    def get_next(self):
        q_text = self.quiz.next_question()
        self.cv.itemconfig(self.txr , text = q_text)

    def tick_keypress(self):
        self.tb.config(state = ST)
        self.tc.config(state = ST)
        self.quiz.check_answer(TRUE)
        self.show_feedback()
        self.update_score()
        # self.get_next()
        # if self.quiz.question_number == 10:
        #     self.source_of_truth()

    def cross_keypress(self):
        self.tb.config(state = ST)
        self.tc.config(state = ST)
        self.quiz.check_answer(FALSE)
        self.show_feedback()
        self.update_score()
        # self.get_next()
        # if self.quiz.question_number == 10:
        #     self.source_of_truth()

    def update_score(self):
        self.score_l.config(text=f"Score : {self.quiz.score}")

    def source_of_truth(self):
        self.cv.itemconfig(self.txr , text = 'NO MORE QUESTIONS')
        msg.showinfo(title = "TIME's UP" , message = f"SCORE : {self.quiz.score}\nACCURACY : {(self.quiz.score/10)*100}%")        
        self.tb.config(state = ST)
        self.tc.config(state = ST)
    
    def show_feedback(self):
        if self.quiz.is_corr:
            self.cv.config(bg = GREEN)
            self.sc.after(1000 , self.reset)
        else:
            self.cv.config(bg = RED)
            self.sc.after(1000 , self.reset)
    
    def reset(self):
        self.cv.config(bg = WHITE)
        self.tb.config(state = AST)
        self.tc.config(state = AST)
        if self.quiz.still_has_questions():
            self.get_next()
        else:
            self.source_of_truth()