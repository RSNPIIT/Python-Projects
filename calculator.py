print(r"""

                                                                                                       
                                                                                                    
                                                                                                    
   :####:            ####                          ####                                             
   ######            ####                          ####                  ##                         
 :##:  .#              ##                            ##                  ##                         
 ##         :####      ##         ####:  ##    ##    ##       :####    #######    .####.    ##.#### 
 ##.        ######     ##       #######  ##    ##    ##       ######   #######   .######.   ####### 
 ##         #:  :##    ##       ##:  :#  ##    ##    ##       #:  :##    ##      ###  ###   ###.    
 ##          :#####    ##      ##.       ##    ##    ##        :#####    ##      ##.  .##   ##      
 ##.       .#######    ##      ##        ##    ##    ##      .#######    ##      ##    ##   ##      
 ##        ## .  ##    ##      ##.       ##    ##    ##      ## .  ##    ##      ##.  .##   ##      
 :##:  .#  ##:  ###    ##:      ##:  .#  ##:  ###    ##:     ##:  ###    ##.     ###  ###   ##      
   ######  ########    #####    #######   #######    #####   ########    #####   .######.   ##      
   :####:    ###.##    .####      ####:    ###.##    .####     ###.##    .####    .####.    ##      
                                                                                                    
                                                                                                    
""")
def sum(a1,a2):
    return a1 + a2
def subtract(a1,a2):
    return a1 - a2
def multiply(a1,a2):
    return a1 * a2
def divide(a1,a2):
    return a1 / a2
def modulus(a1,a2):
    return a1 % a2
def floor_div(a1,a2):
    return a1 // a2
attmpt = 0
all_vals = {
    '+': sum,
    '-': subtract,
    '*': multiply,
    '/': divide,
    '%': modulus,
    '//': floor_div
}
accumulate = True
val1 = float(input("Enter the First Operand Here : "))
while accumulate:
    print("The Operations Are : \n")
    for i in all_vals:
        print(i)
    symbol = input("Enter the Operator symbol Here : ")
    if symbol not in all_vals:
        print(f"Error , This Symbol {symbol} not found.\nPlease Select a Valid Symbol")
        continue
    else:
        val2 = float(input("Enter the Second Operand Here : "))
        if ((symbol == '/') or (symbol == '%') or (symbol == '//')) and val2 == 0:
            print("ERROR : Can't Divide by Zero \n")
            continue
        
        else:
            ans = all_vals[symbol](val1 , val2)
            print(f"{val1} {symbol} {val2} = {ans}")
            attmpt += 1
            print("Do You Wanna Continue (Note the Values Will Be Auto Accumulated)")
            ch = input("Enter Y or N , in order to make your choice -- To or Not to accumulate : ").strip().lower()
            if ch == 'y':
                print(f"----Your Choice is {ch.title()}----")
                val1 = ans
                continue
            elif ch == 'n':
                print(f"----Your Choice is {ch.title()}----")
                print(f"So far {attmpt} operations have been performed")
                accumulate = False
                break
            else:
                print("Your Choice is Wrong ,\nEnter the correct choice Please")
                val1 = ans
                continue