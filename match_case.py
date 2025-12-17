print("Welcome to Ramrup's Code \nMade by Ramrup Satpati aka RSNPIIT from IITM\n")
attmpt = 0

def give_match(xode):
    match xode:
        case 200:
            return("\nSearch Successfull\n")
        case 300:
            return("\nMoved Permanently\n")
        case 302:
            return("\nMoved Temporarily\n")
        case 304:
            return("\nNot Moved Location\n")
        case 400:
            return("\nBad Request\n")
        case 401:
            return("\nUnauthorised Page\n")
        case 403:
            return("\nForbidden Page\n")
        case 404:
            return("\nError\n")
        case 429:
            return("\nToo Many Requests\n")
        case 500:
            return("\nInternal Server Error\n")
        case 502:
            return("\nBad Gateway\n")
        case 503:
            return("\nService Unavailable\n")
        case 504:
            return("\nGateway Timeout\n")
        case _:
            return("\nNot Found\n")

while True:
    attmpt += 1
    try:
        web_code = abs(int(input("Enter the HTTP Code You Wanna Test :- ")))
    except ValueError as e:
        print("Wrong Input\nPlease input a number\n")
        continue
    else:
        print(give_match(web_code))
    
    tell_me = input("Wanna Continue [Y/N]\nYou can test multiple situations :- ").strip().lower()
    if tell_me in ['no','n','nyet','nien','quit','exit']:
        print(f"Number of Attempts are {attmpt}\nExit Successfull\nPlease Come Back\n")
        break
    elif tell_me in ['yes','y','da','ja']:
        print("\n--Continuing--\n")
        continue
    else:
        print(f"Number oft Attempts are {attmpt}\nExit Successfull\nPlease Come Back\n")
        break

