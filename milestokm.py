import tkinter as tk

#Function
def mil_to_km():
    mi = float(m_in.get())
    km = round(mi * 1.609,2)
    km_in.config(text = f'{km}')

#Screen
sc = tk.Tk()
sc.title('Miles to Kilometres')
# sc.minsize(800,800)
sc.config(padx = 45 , pady = 45)

#Text Input
m_in = tk.Entry(width = 10)
m_in.grid(column = 1, row = 0)

miles = tk.Label(text = 'Miles')
miles.grid(column = 2, row = 0)

wv = tk.Label(text = 'Is Equal to :')
wv.grid(column = 0, row = 1)

km_in = tk.Label(text = '0')
km_in.grid(column = 1, row = 1)

km_l = tk.Label(text = 'Km')
km_l.grid(column = 2, row = 1)

c_b = tk.Button(text = 'Calculate', command = mil_to_km)
c_b.grid(column = 1, row = 2)


sc.mainloop()