class Person:
    def __init__(self ,age ,name):
        self.age = age
        self.name = name
    
    def this_p(self):
        print("This is a Person")

class Employee(Person):
    def __init__(self ,age ,name ,emp_id):
        super().__init__(age ,name)
        self.emp_id = emp_id
    
    def the_emp_sp(self):
        print(f"The Employee with \nAge :- {self.age} \nName :- {self.name} \nEmployee ID :- {self.emp_id}")

tim = Employee(25 ,"Jake" ,456)
tim.this_p()
tim.the_emp_sp()