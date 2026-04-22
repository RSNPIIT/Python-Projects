def process_payment(bal , amt , lim = 10000):
    if amt <= 0:
        return (False , 'Invalid Amount')
    elif amt > lim:
        return (False , 'Exceeds Limit Amount')
    elif amt > bal:
        return (False , 'Insufficient Funds')
    else:
        rem = bal - amt
        return (True , rem)

def analyzer(succ , msg):
    if succ:
        print(f"Transaction Successful\nNew Balance is -> {msg}")
    else:
        print(f"Transaction Failed\nError Message is -> {msg}")

analyzer(*process_payment(500 , 100))