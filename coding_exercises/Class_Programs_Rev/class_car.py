# Create a class named Car with attributes make, model, and year. 
# Create an object of the class and print its attributes.

# Add a method named start_engine to the Car class that prints a message when the engine starts. 
# Create an object of the class and call the method.
import datetime as dt

S_Y = 1885
ow = dt.datetime.now()
ytr = ow.year

class Car:
    def __init__(self , make, model, year):
        self.make = make
        self.model = model
        self.year = year

    def start_engine(self):
        print("Car Starts\nLet's Go To a Race")
        
c_m = input("Enter the Car's Make here :- ").strip().title()
c_md = input("Enter the Car's Model Here :- ").strip().title()

try:
    c_y = abs(int(input("Enter the Car's Build Year in :- ")))
except ValueError as v:
    print("Error Peice of Code\nWhy is there something else in place of a number")
    exit()

if c_y < S_Y or c_y > ytr:
    c_y = "Manufacturing Date Not Found or Undisclosed"
    print(f"The Car's Year is Wrong\nEither Before {S_Y} it popped into Existense Which without Time Machine is Impossible\nOr Formed in the Future")
else:
    c_y += 0

niss = Car(c_m , c_md ,c_y)
print("Car Object Formed\n")
print(f"Car Make : {niss.make}")
print(f"Car Model : {niss.model}")
print(f"Car Built Year : {niss.year}")
niss.start_engine()