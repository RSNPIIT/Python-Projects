import requests
import sys as s
import time as ti
import os as o

API_KEY = o.environ.get('OPENWEATHER_API_KEY')

def get_weather(city):
    URL = 'https://api.openweathermap.org/data/2.5/weather'
    PARAMETERS = {
        'q' : city,
        'appid' : API_KEY,
        'units' : 'metric'
    }

    try:
        res = requests.get(
            URL,
            params = PARAMETERS
        )
        data = res.json()
        res.raise_for_status()
    
    except requests.exceptions.HTTPError as http_error:
        if res.status_code == 404:
            return f"Error:-> City Name = {city} not found or is not in the list\n"
        elif res.status_code == 401:
            return "Invalid API Key. Please enter the correct codec"
        return f"HTTP Error occurred\nDetails -> {http_error}"
    
    except requests.exceptions.ConnectionError as cnnt:
        return f"Network Error\nPlease check your network connection\nDetails -> {cnnt}"
    
    except Exception as exc:
        return f"Error Occurred\nDetails -> {exc}"
    
    else:
        summary = {
            "Temperature" : data['main']['temp'],
            "Feels_Like" : data['main']['feels_like'],
            "Description" : data['weather'][0]['description'].title()
        }

        return summary

try:
    city = input("Enter the name of a city here :-> ").strip().title()

    if not city:
        print("No city entered\nExitting cleanly ....")
        s.exit()

    result = get_weather(city)

    if isinstance(result, str):
        print(result)
    else:
        print(f"Weather Report for {city} is ->\n")
        print(f"Temperature = {result['Temperature']}°C")
        print(f"Feels Like = {result['Feels_Like']}°C")
        print(f"Additional Disclosure = {result['Description']}")

except (KeyboardInterrupt, EOFError) as kbef:
    print("Exitting...\nPlease do not spam")
    ti.sleep(2)
    o.system('cls' if o.name == 'nt' else 'clear')
    s.exit()