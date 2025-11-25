#Celcius To Fahrenheit Converter project
import tkinter as tk

#Function
def do_it():
    cel = float(e1.get())
    fah = str(round(1.8 * cel + 32 , 3))
    l2.config(text = fah)

#Screen Setup
sc = tk.Tk()
sc.title('Converter')
sc.config(padx = 40, pady = 40)

#Entry
e1 = tk.Entry(width = 10)
e1.grid(column = 1,row = 0)

#Label
l1 = tk.Label(text = 'Celcius', font = ('Arial',24,'bold'))
l1.grid(column = 2,row = 0)

#Label
l2 = tk.Label(text = '0', font = ('Arial',24,'bold'))
l2.grid(column = 1,row = 1)

#Label
l3 = tk.Label(text = 'Fahrenheit', font = ('Arial',24,'bold'))
l3.grid(column = 2,row = 1)

#Button
bu = tk.Button(text = 'Convert', command = do_it)
bu.grid(column = 2,row = 2)

sc.mainloop()