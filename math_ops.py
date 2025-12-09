# math_ops.py
# Looping interactive calculator in Python
# Exit only when user types 'q' or 'Q'

while True:
    # Prompt for first number
    num1_input = input("Enter first number (or q to quit): ")
    
    if num1_input.lower() == 'q':
        print("\nExiting calculator. Goodbye!")
        break

    # Validate num1
    try:
        num1 = float(num1_input)
    except ValueError:
        confirm = input("Did you mean to quit? (q to exit, any other key to continue): ")
        if confirm.lower() == 'q':
            print("\nExiting calculator. Goodbye!")
            break
        else:
            continue

    # Prompt for second number
    num2 = float(input("Enter second number: "))

    # Show menu
    print("\nChoose an operation:")
    print("1: Addition")
    print("2: Subtraction")
    print("3: Multiplication")
    print("4: Division")
    print("5: Modulus (Remainder)")
    print("q: Quit")

    choice = input("Enter choice (1-5 or q): ")

    if choice.lower() == 'q':
        print("\nExiting calculator. Goodbye!")
        break

    # Perform operation
    result = None

    try:
        choice = int(choice)
        if choice == 1:
            result = num1 + num2
        elif choice == 2:
            result = num1 - num2
        elif choice == 3:
            result = num1 * num2
        elif choice == 4:
            result = num1 / num2 if num2 != 0 else "Error: Division by zero"
        elif choice == 5:
            result = num1 % num2 if num2 != 0 else "Error: Modulus by zero"
        else:
            result = "Invalid choice"
    except ValueError:
        result = "Invalid choice"

    print("\nResult:", result, "\n")