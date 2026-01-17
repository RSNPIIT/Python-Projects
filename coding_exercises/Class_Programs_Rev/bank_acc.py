class Bank:
    def __init__(self ,bal):
        self.__bal = bal

    def deposit(self , amt):
        self.__bal += amt
        # print("Amount Added Successfully")
    
    def withdraw(self , ant):
        if ant <= self.__bal:
            self.__bal -= ant
            # print("Amount Withdrawen Successfully\n")
        else:
            print("Insufficient Funds\nWithdrawal Unsuccessfull")
    
    def get_bal(self):
        return self.__bal
    
axis = Bank(1000)
axis.deposit(560)
axis.deposit(12350)
axis.withdraw(451)

print("Correct Method")
print(f"The Balance Amount is : {axis.get_bal()}")

print("Wrong Method :")
try:
    print(axis.__bal)
except AttributeError as e:
    print(f"Error : {e}")