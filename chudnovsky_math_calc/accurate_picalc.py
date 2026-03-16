import decimal as dc
import math as m
import time as ti
import os as o
import sys as s
import turtle as t
import datetime as dt

#Static Variables
now = dt.datetime.now()
yr = now.year
ALIGNV = 'center'
FONT = ('Arial' , 25 , 'bold')

#The Function to get an accurate Pi upto a large number of digits
def the_accurate_pizza(digi):
    try:
        dc.getcontext().prec = digi + 2
    except OverflowError as l:
        print(f"\nToo Large Value Given\n{l}\n")
        s.exit()

    #Chudnovsky Constant for Incrementing Values
    chud_cons = (digi // 14) + 1
    pi_v = dc.Decimal(0)

    for k in range(chud_cons):
        numerator = ((-1) **k) * m.factorial(6 *k) * (13591409 + 545140134 *k)

        denominator = m.factorial(3 *k) * (m.factorial(k) ** 3) * 640320 ** (3 * k)

        pi_v += dc.Decimal(numerator) / dc.Decimal(denominator)

    const_for_cal = dc.Decimal(426880) * (dc.Decimal(10005)) ** (dc.Decimal(0.5))
    pi_val = const_for_cal / pi_v
    return +pi_val

#User Input
print("\nWelcome to the Python and Linux Pi Accurate Digit Simulator\nTo Get Started Please Enter the Number of Digits to see pi to\nRECOMMENDED :- (15 digits to 1500 digits)\n")
try:
    dig = abs(int(input("Enter the Number of Digits You wanna calculate Pi to :-> ")))

    if dig == 0:
        print("Cant Show Pi Upto 0 Decimal Places\nPlease Re-Enter\n")
        ti.sleep(1)
        o.system('cls' if o.name == 'nt' else 'clear')
        s.exit()

    elif dig > 1500:
        print("\nFor Safety reasons we have capped all of it at 1500 digits so as to avoid CPU Lags and stutters\n")
        ti.sleep(1)
        o.system('cls' if o.name == 'nt' else 'clear')
        s.exit()
    
except (KeyboardInterrupt , EOFError) as kb:
    print("\nExitting the Code\nPlease Dont Spam....\n")
    ti.sleep(1)
    o.system('cls' if o.name == 'nt' else 'clear')
    s.exit()
except ValueError as v:
    print("\nNon Integral Values are not allowed\nPlease Re-Enter\n")
    ti.sleep(1)
    o.system('cls' if o.name == 'nt' else 'clear')
    s.exit()
else:
    giv_val = the_accurate_pizza(dig)
    print(f"For {dig} decimal place(s) the Pi Value is :- \n{giv_val}\n")

    ti.sleep(1)
    print("Making the Circle...")

    # Screen Setup
    sc = t.Screen()
    sc.setup(800,800)
    sc.title('The Accurate Pizza')
    sc.bgcolor('black')

    # Turtle Object Setup
    timmy = t.Turtle()
    timmy.shape('turtle')
    timmy.color('yellow')
    timmy.pensize(3)
    timmy.hideturtle()
    timmy.circle(150)
    ti.sleep(1)
    timmy.home()
    timmy.clear()
    timmy.write(f'The [PI]zza is Served\nHappy Pi Day {yr}' , align = ALIGNV , font = FONT)

    sc.exitonclick()
    print(f"The Circle is Made\nHappy PI Day {yr}")

finally:
    print("\n🄯 Ramrup Satpati (RSNPIIT) | IIT Madras")
    print("Licensed under GNU GPL-3 (Copyleft)")
    print("Thankyou....\n")