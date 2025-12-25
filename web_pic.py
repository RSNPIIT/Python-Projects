import tkinter as tk

#Static Elements
LIGHT = '#D3D3D3'
TEAL = '#069494'
GLASS = '#FAF2EC'
COLOR = '#40E0D0'

#Defining the Functions
def get_me():
    try:
        xfce = abs(int(e1.get()))
    
    except KeyboardInterrupt:
        print("Exiting Cleanly\nGoodbye")

    except ValueError:
        l2 = tk.Label(text = 'Please Enter a Positive Number' , highlightthickness = 0)
        l2.grid(column = 1 , row = 3)

    else:
        match xfce:
            case 200:
                l1.config(text ="Search Successfull")
            case 300:
                l1.config(text = "Moved Permanently")
            case 302:
                l1.config(text = "Moved Temporarily")
            case 304:
                l1.config(text = "Not Moved Location")
            case 400:
                l1.config(text = "Bad Request")
            case 401:
                l1.config(text = "Unauthorised Page")
            case 403:
                l1.config(text = "Forbidden Page")
            case 404:
                l1.config(text = "Error")
            case 429:
                l1.config(text = "Too Many Requests")
            case 500:
                l1.config(text = "Internal Server Error")
            case 502:
                l1.config(text = "Bad Gateway")
            case 503:
                l1.config(text = "Service Unavailable")
            case 504:
                l1.config(text = "Gateway Timeout")
            case _:
                l1.config(text = "Not Found")

#Setting the UI
sc = tk.Tk()
sc.title('Web Helper')
sc.config(padx = 50 , pady = 50 , bg = LIGHT )

e1 = tk.Entry(width = 15 , fg = TEAL , highlightthickness = 0)
e1.grid(column = 1 , row = 0)

bu1 = tk.Button(text = 'Check', width = 15 , fg = GLASS , highlightthickness = 0 , command = get_me)
bu1.grid(column = 1 , row = 1)

l1 = tk.Label(text = "0" , highlightthickness = 0)
l1.grid(column = 1 , row = 2)

sc.mainloop()