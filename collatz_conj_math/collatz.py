# Starting Loop - The User Inputs until (s)he gets a perfect number
GUARDRAIL = 500000

while True:
    try:
        num = abs(int(input("Enter a Number Here : ")))
    except (KeyboardInterrupt , EOFError) as kb:
        print("\nExiting the App is not allowed \nThis is for security reasons---")
        continue
    except ValueError as v:
        print("\nWrong Value Given --Please go again.")
        continue
    except Exception as e:
        print(f"\nAn Exception Occurred |--> {e}")
        continue
    else:
        if num == 0:
            print(f"A value of {num} is not allowed here")
        elif num >= GUARDRAIL:
            print(f"While You are techinically correct\nA Large Value may be given but try to understand -- It will take time and waste lots of resources on your device so this failsafe is added\nPlease (RE)Enter")
            continue
        else:
            break

# Static Variables
STEPS = 0
PEK = num
ORN = num

# Calculating the steps it will take to fall to 1
while num != 1:
    if num % 2 == 0:
        num //= 2
    else:
        num = (3 * num) + 1
    print(f"In Step -> {STEPS + 1} | The Num is -> {num}")
    STEPS += 1

    # Re-callibrate the peak if the num is greater than peak
    if num > PEK:
        PEK = num

# Finally Displaying the Results
print(f"The Status is :->\nStarting Number -> {ORN}\nSteps taken to fall to the 1 is -> {STEPS}\nWith the Peak being -> {PEK}")
print("I thank Siddhi Mittal (https://www.linkedin.com/in/siddhi-mittal-058829370/) for giving the starting boiler plate introduction to the same")