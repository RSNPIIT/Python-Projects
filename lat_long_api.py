import os as o
import requests

def get_coords(city_name):
    url = "https://api.openweathermap.org/geo/1.0/direct"
    
    params = {
        'q': city_name,
        'limit': 1, 
        'appid': o.environ.get('OPENWEATHER_API_KEY')
    }
    
    res = requests.get(url, params=params)
    res.raise_for_status()
    data = res.json()
    
    if not data:
        return "Location not found"
        
    lat = data[0]['lat']
    lon = data[0]['lon']
    return f"Geocode -> Lat: {lat}, Lon: {lon}"

try:
    city = input("Enter the name of a city here :-> ").strip().title()

    if not city:
        print("No city entered\nExitting cleanly ....")
        s.exit()

    result = get_coords(city)
    print(f"Locations for {city} are ->\n{result}")

except (KeyboardInterrupt, EOFError) as kbef:
    print("Exitting...\nPlease do not spam")
    ti.sleep(2)
    o.system('cls' if o.name == 'nt' else 'clear')
    s.exit()