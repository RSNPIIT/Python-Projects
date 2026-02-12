from bank_accnt import *

ram = BankAccount(1000 , 'Ram')
rem = BankAccount(2000 , 'Remi')

ram.deposit(450)
rem.deposit(125)

ram.withdraw(50)
rem.withdraw(45000)

ram.transfer(50, ram)
rem.transfer(50000, ram)

jim = InterestTransfer(10000 , 'jim')
jim.deposit(500)
jim.transfer(54, ram)

blaze = SavingsAccount(30000 , 'blaze')
blaze.deposit(56)
blaze.withdraw(16)