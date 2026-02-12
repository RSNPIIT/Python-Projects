class BalanceExcept(Exception):
    pass

class BankAccount:
    def __init__(self, InitAmnt, AccntName):
        self.balance = InitAmnt
        self.name = AccntName
        print(f"\nAccount {self.name} created Successfully")

    def getBalance(self):
        print(f"\nAccount {self.name} -> \nIt has a balance of ₹{self.balance:.2f}")

    def deposit(self ,amt):
        self.balance += amt
        print("Deposit Completed")
        self.getBalance()

    def viable_trnm(self ,amt):
        if self.balance >= amt:
            return
        else:
            raise BalanceExcept(
                f'{self.balance} is less than {amt} amount'
            )

    def withdraw(self ,amt):
        try:
            self.viable_trnm(amt)
            self.balance -= amt
            print('\nWithdraw Complete')
            self.getBalance()
        except BalanceExcept as b:
            print(f"\nFor {self.name} the withdraw is interrupted as {b}")

    def transfer(self ,amt , acct):
        try:
            print("\nBeginning Transaction...")
            self.viable_trnm(amt)
            self.withdraw(amt)
            acct.deposit(amt)
            print('\nTransfer Complete')
        except BalanceExcept as e:
            print("\nTransaction Canceled")
            print(f'\nFor {self.name} {e}')

class InterestTransfer(BankAccount):
    def deposit(self ,amount):
        self.balance += (amount * 1.05)
        print("\nSuccessful Interest Execution")
        self.getBalance()

class SavingsAccount(InterestTransfer):
    def __init__(self ,InitAmnt , AccntName):
        super().__init__(InitAmnt , AccntName)
        self.fee = 5

    def withdraw(self ,amount):
        try:
            self.viable_trnm(amount + self.fee)
            self.balance -= (amount + self.fee)
            print('\nWithdraw Completed')
            self.getBalance()
        except BalanceExcept as be:
            print(f'Withdraw Interrupted for {self.name} {be}')