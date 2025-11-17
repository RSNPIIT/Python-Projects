import tkinter as tk

#Function
def you_do():
    gh = float(my_l.get())
    mt = round(gh * 0.3048 , 2)
    mt = str(mt)
    my_k.config(text = mt)

#Screen
sc = tk.Tk()
sc.title('Converter')
sc.config(padx = 45, pady = 45)

#Entry
my_l = tk.Entry(width = 10)
my_l.grid(column = 1,row = 0)

#Label
my_i = tk.Label(text = 'Feet')
my_i.grid(column = 2,row = 0)

#Label
my_k = tk.Label(text = '0')
my_k.grid(column = 1,row = 1)

#Label
my_m = tk.Label(text = 'Metres')
my_m.grid(column = 2, row = 1)

#Button
my_b = tk.Button(text = 'Convert',command = you_do)
my_b.pack()

sc.mainloop()