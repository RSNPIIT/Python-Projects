import tkinter as tk

#Function
def my_task():
    xd = float(my_1.get())
    val = str(round(xd  * 3.785 , 3))
    my_3.config(text = val)

#Screen
sc = tk.Tk()
sc.title('Converter')
sc.config(padx = 45,pady = 45)

#Entry
my_1 = tk.Entry(width = 10)
my_1.grid(column = 1,row = 0)

#Label
my_2 = tk.Label(text = 'Gallons(gal)', font = ('Arial',24,'bold'))
my_2.grid(column = 2,row = 0)

#Label
my_3 = tk.Label(text = '0', font = ('Arial',24,'bold'))
my_3.grid(column = 1,row = 1)

#Label
my_4 = tk.Label(text = 'Litres(L)' , font = ('Arial',24,'bold'))
my_4.grid(column = 2,row = 1)

#Conversion Button
bu = tk.Button(text = 'Convert' , command = my_task)
bu.grid(column = 1,row = 2)

sc.mainloop()