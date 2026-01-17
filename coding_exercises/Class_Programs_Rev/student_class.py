class Student:
    def __init__(self ,name ,age):
        self.name = name
        self.age = age

S_N = input("Name of the Student : ").strip().title()
try:
    AG = abs(int(input("Enter the Age Here : ")))
except ValueError as vl:
    print("Wrong DataType Given\nPlease Correct It\n")
    exit()

my_S = Student(S_N ,AG)
print(f"The Student Name is : {my_S.name}")
print(f"The Student Age is : {my_S.age}")