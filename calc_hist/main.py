def his():
    with open('history.txt') as f:
        lin = f.readlines()
        if len(lin) == 0:
            print('No History Found\n')
        else:
            for x in reversed(lin):
                print(x.strip())

def clear_his():
    with open('history.txt','w') as f:
        pass
    print('History Cleared\n')

# Essentially this code is You can uncomment and use - lines 16 to 19 and use the function in line 73
# def savehis(eqn,res):
#     file = open('history.txt','a')
#     file.write(eqn + ' ' + '=' + ' ' + str( res) + '\n')
#     file.close()

def calculate(u_in):
    parts = u_in.split()
    if len(parts) != 3:
        print('Invalid Input : Use Format Num Opern Num (N O N)\n')
        return

    else:
        num1 = float(parts[0])
        op = parts[1]
        num2 = float(parts[2])

        if op == '+':
            res = num1 + num2
        
        elif op == '-':
            res = num1 - num2
        
        elif op == '*':
            res = num1 * num2
        
        elif op == '/':
            if num2 == 0:
                print("Invalid Operation \nCan't Divide by Zero\n")
                return

            res = num1 / num2
        
        elif op == '**' or op == '^':
            res = num1 ** num2
        
        elif op == '//':
            if num2 == 0:
                print("Invalid Operation \nCan't Divide by Zero\n")
                return
            res = num1 // num2

        elif op == '%':
            if num2 == 0:
                print("Invalid Operation \nCan't Divide by Zero\n")
                return
            res = num1 % num2
        
        else:
            print("Invalid Operator -> Use only +,-,*,/,^,**,//,% (For now)\n")
            return
        
        if int(res) == res:
            res = int(res)
        else:
            res = round(res,2)

        print(f"The Result is : {res}")
        with open('history.txt','a') as f:
            f.write(str(num1) + ' ' + op + ' ' + str(num2) + ' ' + '=' + ' ' + str(res) + '\n') 
        # savehis(u_in , res)

def main():
    attmpt = 0
    print("Simple Calculator by RSNPIIT (Ramrup Satpati)\n")

    while True:
        u_ch = input('Enter a Calculation in Number Opeerator Number Format or Enter Commands (show/clear/exit) : ').strip().lower()
        attmpt += 1

        if u_ch == 'clear':
            clear_his()

        elif u_ch == 'show':
            his()
        
        elif u_ch == 'exit':
            print('Goodbye \nPlease Visit Again\n')
            print(f'App Used For {attmpt} times\n')
            break
        
        else:
            calculate(u_ch)

main()