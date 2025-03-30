import requests
import json
import sys
from datetime import datetime

# --- Configuration ---
# Replace 'YOUR_API_KEY' with the key you got from OpenWeatherMap
API_KEY = "YOUR_API_KEY"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"

# --- Functions ---

def get_weather_data(city_name, api_key, units="metric"):
    """Fetches weather data from OpenWeatherMap API."""
    # Construct the full API request URL
    url = f"{BASE_URL}q={city_name}&appid={api_key}&units={units}"

    try:
        response = requests.get(url)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # Parse the JSON response
        weather_data = response.json()
        return weather_data

    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 401:
            print(f"Error: Invalid API Key. Please check your API_KEY variable.")
        elif response.status_code == 404:
            print(f"Error: City '{city_name}' not found.")
        else:
            print(f"HTTP error occurred: {http_err} - Status Code: {response.status_code}")
        return None
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
        return None
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
        return None
    except requests.exceptions.RequestException as req_err:
        print(f"An error occurred during the request: {req_err}")
        return None
    except json.JSONDecodeError:
        print("Error: Could not decode the server response.")
        return None

def display_weather(data, units="metric"):
    """Formats and displays the fetched weather data."""
    if not data or data.get("cod") != 200:
        # Handle cases where data is None or the API returned an error code within the JSON
        if data and data.get("message"):
             print(f"API Error: {data['message']}")
        # Specific error messages handled in get_weather_data
        return

    try:
        main_data = data.get("main", {})
        weather_desc = data.get("weather", [{}])[0].get("description", "N/A")
        wind_data = data.get("wind", {})
        sys_data = data.get("sys", {})
        city = data.get("name", "N/A")
        country = sys_data.get("country", "N/A")

        temp = main_data.get("temp")
        feels_like = main_data.get("feels_like")
        humidity = main_data.get("humidity")
        pressure = main_data.get("pressure") # Pressure is usually in hPa
        wind_speed = wind_data.get("speed")

        # Determine units for display
        temp_unit = "°C" if units == "metric" else "°F"
        speed_unit = "m/s" if units == "metric" else "mph"

        # Format sunrise/sunset times (API gives Unix timestamp)
        sunrise_ts = sys_data.get("sunrise")
        sunset_ts = sys_data.get("sunset")
        sunrise_time = datetime.fromtimestamp(sunrise_ts).strftime('%H:%M:%S') if sunrise_ts else "N/A"
        sunset_time = datetime.fromtimestamp(sunset_ts).strftime('%H:%M:%S') if sunset_ts else "N/A"


        print("-" * 40)
        print(f"Weather for {city}, {country}")
        print("-" * 40)
        print(f"Condition:    {weather_desc.capitalize()}")
        if temp is not None:
            print(f"Temperature:  {temp:.1f}{temp_unit}")
        if feels_like is not None:
            print(f"Feels like:   {feels_like:.1f}{temp_unit}")
        if humidity is not None:
            print(f"Humidity:     {humidity}%")
        if pressure is not None:
             print(f"Pressure:     {pressure} hPa")
        if wind_speed is not None:
            print(f"Wind Speed:   {wind_speed} {speed_unit}")
        print(f"Sunrise:      {sunrise_time}")
        print(f"Sunset:       {sunset_time}")
        print("-" * 40)

    except KeyError as e:
        print(f"Error: Missing expected data field: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while displaying data: {e}")


# --- Main Execution ---
if __name__ == "__main__":
    if API_KEY == "YOUR_API_KEY":
        print("Error: Please replace 'YOUR_API_KEY' with your actual OpenWeatherMap API key in the script.")
        sys.exit(1) # Exit if API key is not set

    while True:
        city = input("Enter city name (or type 'quit' to exit): ").strip()
        if not city:
            print("Please enter a city name.")
            continue
        if city.lower() == 'quit':
            break

        # Optional: Ask for units
        unit_choice = input("Choose units: (M)etric (°C, m/s) or (I)mperial (°F, mph)? [M]: ").strip().lower()
        units = "imperial" if unit_choice == 'i' else "metric"


        print(f"\nFetching weather data for {city}...")
        weather_info = get_weather_data(city, API_KEY, units)

        if weather_info:
            display_weather(weather_info, units)
        # Error messages are printed within get_weather_data or display_weather

    print("Exiting weather app. Goodbye!")