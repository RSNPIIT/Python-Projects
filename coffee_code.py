import datetime as dt

# Static Variables
DA = 'y'

# Dynamic Dispatch Variables
now = dt.datetime.now()
day = now.day
mon = now.mon
yr = now.year

fmt = f'{day}-{mon}-{yr}'

class Cofee:
    def __init__(self ,name ,price):
        self.name = name
        self.price = price
    
class CartItem:
    def __init__(self , coffee, quantity):
        self.coffee = coffee
        self.quantity = quantity
    
    def get_total(self):
        return self.coffee.price * self.quantity
    
class CofeeShop:
    def __init__(self):
        self.menu = [
            Cofee('Expresso' , 120),
            Cofee('Capaccino' , 135),
            Cofee('Latte' , 100),
            Cofee('Americano' , 130),
            Cofee('Mocha', 200)
        ]
    
    def show_menu(self):
        print("\n---- Showing Menu ----")
        for idx , c in self.menu:
            print(f"Index -> {idx} || Cofee Name -> {c.name} || Cofee Price -> ₹{c.price}")

    def get_valid_ch(self):
        while True:
            try:
                choice = int(input("\nEnter Coffee Number to order the same -\n"))
                if 1 <= choice <= len(self.menu):
                    return choice - 1
                else:
                    print("\nPlease Choose a valid Number Here\n")
            
            except (KeyboardInterrupt , EOFError) as kb:
                print(f"\nNot allowed to exit by doing such shenanigans\n")
                continue
            
            except ValueError as v:
                print(f"\nNot allowed to use Non-Integer Number\n")
                continue
            
    def get_valid_qty(self):
        while True:
            try:
                qty = int(input("\nEnter a valid quantity to order the same -\n"))
                if qty > 0:
                    return qty
                else:
                    print("\nPlease Choose a valid Number Here\n")
            
            except (KeyboardInterrupt , EOFError) as kb:
                print(f"\nNot allowed to exit by doing such shenanigans\n")
                continue
            
            except ValueError as v:
                print(f"\nNot allowed to use Non-Integer Number\n")
                continue
    
    def take_order(self):
        print("-"*50)
        print("\n====== Welcome to Coffee Shop ======\n")
        cname = input("Enter your name please\n").strip().title()
        cart = []
        while True:
            self.show_menu()
            c_in = self.get_valid_ch()
            qt = self.get_valid_qty()

            sel_cf = self.menu[c_in]
            carter = CartItem(sel_cf , qt)
            cart.append(carter)
            val = input("Do you wanna Order More :-> (Y/N) : ").strip().lower()
            if val != DA:
                break
            else:
                continue       

        self.get_bill(cname , cart)
    
    def get_bill(self , pers , cart):
        print("-"*50)
        print('------- BILL -------\n')
        subt = 0
        print(f"Customer name :-> {pers} | Ordered on :-> {fmt}")
        for i in cart:
            tot = i.get_total()
            subt += tot
            print(f"{i.coffee.name} × {i.quantity} = ₹{i.coffee.price}")
        
        gst = subt * 0.02
        total = subt + gst
        print(f"\nSubtotal :-> ₹{subt:.2f}\nGST (2%) :-> ₹{gst:.2f}\nGrand Total :-> ₹{total:.2f}\nThankyou {cname}\nPlease come again\n")
    
    def start(self):
        while True:
            self.take_order()

def main():
    shp = CofeeShop()
    shop.start()

if __name__ == "__main__":
    main()