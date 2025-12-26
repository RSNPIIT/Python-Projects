#Working with the date time module
import datetime as dt

now = dt.datetime.now()
print(f'The Current Date and Time as per IST is :- {now}')
# print(type(now))

yr = now.year
print(f'The Current Year is :- {yr}')

if yr == 2025:
    print("\nIt's 2025 Baby !!\n")
elif yr == 2026:
    print("\nIt's 2026 Baby !!\n")
else:
    print("\nAah Nvm Forget it\n")

week_day = now.weekday()
print(f"The Day of the week_day is : {week_day}")

match week_day:
    case 0:
        print("Monday\n")
    case 1:
        print("Tuesday\n")
    case 2:
        print("Wednesday\n")
    case 3:
        print("Thursday\n")
    case 4:
        print("Friday\n")
    case _:
        print("Weekend\n")
        if week_day == 5:
            print("Saturday\n")
        elif week_day == 6:
            print("Sunday\n")
        else:
            print("ERROR (Though I'm Sure This will happen only when CPU Error)\n")
        
my_birth = dt.datetime(year = 2006 , month = 1 , day = 9)
print("D.O.B. => {Whoa it's Close} ",my_birth)