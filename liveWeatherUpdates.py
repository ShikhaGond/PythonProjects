import requests

def get_live_weather(city):
    access_key = 'YOUR_ACCESS_KEY'  
    base_url = "http://api.weatherstack.com/current"
    
    # Prepare parameters for the API request
    params = {
        "access_key": 'ddaa34bd221f6997ead87a1089e3e2c5',
        "query": city,
        "units": "m"  # "m" for metric (°C), change to "f" for Fahrenheit if desired
    }
    
    # Make the request to Weatherstack API
    response = requests.get(base_url, params=params)
    data = response.json()
    
    # Check for errors in the response
    if "error" in data:
        print("Error retrieving weather data:", data["error"]["info"])
        return
    
    # Extracting location and current weather data
    location = data.get("location", {})
    current = data.get("current", {})
    
    city_name = location.get("name", "Unknown")
    country = location.get("country", "Unknown")
    localtime = location.get("localtime", "Unknown")
    
    temperature = current.get("temperature", "Unknown")
    weather_descriptions = current.get("weather_descriptions", [])
    wind_speed = current.get("wind_speed", "Unknown")
    humidity = current.get("humidity", "Unknown")
    
    # Print out the weather information
    print(f"Location: {city_name}, {country}")
    print(f"Local Time: {localtime}")
    print(f"Temperature: {temperature}°C")
    print("Weather Description(s):", ", ".join(weather_descriptions))
    print(f"Wind Speed: {wind_speed} km/h")
    print(f"Humidity: {humidity}%")

if __name__ == '__main__':
    city = input("Enter the name of any city: ")
    get_live_weather(city)
