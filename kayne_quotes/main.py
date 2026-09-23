import tkinter as tk
import requests as rq

URL = 'https://api.kanye.rest'
my_text = 'Failed !!'
def get_quote():
    res = rq.get(url = URL)
    if res.status_code == 200:
        js_val = res.json()
        canvas.itemconfig(quote_text , text = f'{js_val['quote']}')
    else:
        canvas.itemconfig(quote_text , text = f'{my_text}')
        res.raise_for_status()

sc = tk.Tk()
sc.title("Kanye Says...")
sc.config(padx=50, pady=50)

canvas = tk.Canvas(width=300, height=414)
background_img = tk.PhotoImage(file="background.png")
canvas.create_image(150, 207, image=background_img)
quote_text = canvas.create_text(150, 207, text="Kanye Quote Goes HERE", width=250, font=("Arial", 30, "bold"), fill="white")
canvas.grid(row=0, column=0)

kanye_img = tk.PhotoImage(file="kanye.png")
kanye_button = tk.Button(image=kanye_img, highlightthickness=0, command=get_quote)
kanye_button.grid(row=1, column=0)

sc.mainloop()