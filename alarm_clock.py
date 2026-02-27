import time as ti
import os as o

def alarm(seconds):
    time_elapsed = 0

    while time_elapsed < seconds:
        ti.sleep(1)
        time_elapsed += 1

        time_left = seconds - time_elapsed
        minutes_left = time_left // 60
        seconds_left = time_left % 60
        o.system('cls' if o.name == 'nt' else 'clear')
        print(f"Alarm Will Sound in =======> ======>{minutes_left:02d}  : {seconds_left:02d}")
    
    #Note this will work only for Linux and BSD based systems not on Windows and Mac
    o.system("aplay ~/Music/alarm.wav")

try:
    minutes = abs(int(input("Enter the Minutes to wait here : ")))
    seconds = abs(int(input("Enter the Seconds to wait here : ")))
except (KeyboardInterrupt , EOFError) as kb:
    print("\nNo Spamming ....")
    exit()
except ValueError as v:
    print("\nNon Integer Values Given ....\n")
else:
    tot_time = minutes * 60 + seconds
    alarm(tot_time)
finally:
    print("Thankyou for using my App\nAlarm () GPL-3 Copylefted under Tux Corporations")