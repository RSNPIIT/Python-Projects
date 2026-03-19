import numpy as np

#Transformation of array
lis = [x for x in range(1,11)]
attmpt = 0

while True:
    attmpt += 1
    try:
        a = abs(int(input("Enter the X axis of reshaping : ")))
        b = abs(int(input("Enter the Y axis of reshaping : ")))
    except (KeyboardInterrupt , EOFError) as kb:
        print(f"No you cant exit...\nExit blocked to prevent App Misbehaviour")
        continue
    except ValueError as v:
        print(f"Please Enter a Valid Integral value\nString Values are not allowed here\n")
        continue
    else:
        if a > 0 and b > 0 and a * b == len(lis):
            myl = np.array(lis).reshape(a ,b)
        else:
            print(f"The Given X axis- {a} and the Y axis- {b} dont match\nRedirecting to standard output")
            myl = np.array(lis)
        print(f"The {myl.ndim}D Array status :-\nList :- {lis}\nArray :- {myl}\nSize :- {myl.size}\nShape (i.e - The Elements in each dimension) :- {myl.shape}\nDatatype of the elements :- {myl.dtype}\n")
        
        print("Wanna Continue :- (y/n) ")
        x = input("Make your choice here : ").strip().lower()
        if x == 'n':
            print(f"Thankyou for using the app\nYou used it for {attmpt} times\nPlease come back")
            break
        else:
            print(f"User Choice is y -- We continue the app")
            continue
    finally:
        print("Made by RSNPIIT (Ramrup Satpati) at IIT Madras")