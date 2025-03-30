import tkinter as tk
from tkinter import ttk  # Themed widgets
from tkinter import messagebox
import requests
import json
from datetime import datetime
import threading # To prevent GUI freezing during API calls
import sys

# --- Configuration ---
# !! REPLACE 'YOUR_API_KEY' WITH YOUR ACTUAL KEY !!
API_KEY = "AIzaSyCCjkBZDHOCQ3Vr-cD20UK0WhIiFr-mdoc"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"
ICON_BASE_URL = "http://openweathermap.org/img/wn/" # Base URL for weather icons

# --- Functions ---

def get_weather_data(city_name, api_key, units="metric"):
    """Fetches weather data from OpenWeatherMap API.
       Returns the parsed JSON data or None on error.
       Includes error type hints for better handling.
    """
    url = f"{BASE_URL}q={city_name}&appid={api_key}&units={units}"
    try:
        response = requests.get(url, timeout=10) # Added timeout
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 401:
            return {"error": "api_key", "message": "Invalid API Key."}
        elif response.status_code == 404:
            return {"error": "not_found", "message": f"City '{city_name}' not found."}
        else:
            return {"error": "http", "message": f"HTTP error: {http_err}"}
    except requests.exceptions.ConnectionError:
        return {"error": "connection", "message": "Network connection error."}
    except requests.exceptions.Timeout:
        return {"error": "timeout", "message": "Request timed out."}
    except requests.exceptions.RequestException as req_err:
        return {"error": "request", "message": f"Request error: {req_err}"}
    except json.JSONDecodeError:
        return {"error": "json", "message": "Error decoding server response."}

def format_weather_display(data, units="metric"):
    """Formats the weather data into a dictionary of strings for display."""
    display_info = {
        "location": "N/A",
        "condition": "N/A",
        "temp": "N/A",
        "feels_like": "N/A",
        "humidity": "N/A",
        "pressure": "N/A",
        "wind": "N/A",
        "sunrise": "N/A",
        "sunset": "N/A",
        "icon_code": None,
        "error": None # Field to pass potential errors
    }

    # Check for errors passed from get_weather_data
    if data and data.get("error"):
        display_info["error"] = data["message"]
        return display_info
    elif not data or data.get("cod") != 200:
         # Handle cases where data is None or the API returned an error code within the JSON
        if data and data.get("message"):
             display_info["error"] = f"API Error: {data['message']}"
        else:
             display_info["error"] = "Could not retrieve weather data."
        return display_info

    try:
        main_data = data.get("main", {})
        weather_list = data.get("weather", [{}])
        weather_main = weather_list[0] if weather_list else {}
        wind_data = data.get("wind", {})
        sys_data = data.get("sys", {})
        city = data.get("name", "N/A")
        country = sys_data.get("country", "N/A")

        temp = main_data.get("temp")
        feels_like = main_data.get("feels_like")
        humidity = main_data.get("humidity")
        pressure = main_data.get("pressure")
        wind_speed = wind_data.get("speed")
        wind_deg = wind_data.get("deg") # Wind direction

        weather_desc = weather_main.get("description", "N/A").capitalize()
        icon_code = weather_main.get("icon")

        temp_unit = "°C" if units == "metric" else "°F"
        speed_unit = " m/s" if units == "metric" else " mph"

        sunrise_ts = sys_data.get("sunrise")
        sunset_ts = sys_data.get("sunset")

        display_info["location"] = f"{city}, {country}"
        display_info["condition"] = weather_desc
        display_info["icon_code"] = icon_code

        if temp is not None:
            display_info["temp"] = f"{temp:.1f}{temp_unit}"
        if feels_like is not None:
            display_info["feels_like"] = f"{feels_like:.1f}{temp_unit}"
        if humidity is not None:
            display_info["humidity"] = f"{humidity}%"
        if pressure is not None:
             display_info["pressure"] = f"{pressure} hPa"
        if wind_speed is not None:
            wind_str = f"{wind_speed:.1f}{speed_unit}"
            # Optional: Add wind direction if available
            # if wind_deg is not None: wind_str += f" (at {wind_deg}°)"
            display_info["wind"] = wind_str

        if sunrise_ts:
            display_info["sunrise"] = datetime.fromtimestamp(sunrise_ts).strftime('%H:%M:%S')
        if sunset_ts:
            display_info["sunset"] = datetime.fromtimestamp(sunset_ts).strftime('%H:%M:%S')

    except KeyError as e:
        display_info["error"] = f"Missing data field: {e}"
    except Exception as e:
        display_info["error"] = f"Error processing data: {e}"

    return display_info


# --- GUI Class ---

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather App")
        self.root.geometry("450x450") # Adjusted size
        self.root.option_add("*Font", "Helvetica 10") # Default font

        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use('clam') # Try 'clam', 'alt', 'default', 'classic'

        # Variables
        self.city_var = tk.StringVar(value="London") # Default city
        self.units_var = tk.StringVar(value="metric") # Default units
        self.weather_info = tk.StringVar(value="Enter a city and click 'Get Weather'")

        # --- GUI Layout ---

        # Input Frame
        input_frame = ttk.Frame(root, padding="10 10 10 10")
        input_frame.pack(fill=tk.X)

        ttk.Label(input_frame, text="City:").pack(side=tk.LEFT, padx=5)
        self.city_entry = ttk.Entry(input_frame, textvariable=self.city_var, width=20)
        self.city_entry.pack(side=tk.LEFT, padx=5)
        self.city_entry.bind("<Return>", self.fetch_weather_threaded) # Bind Enter key

        self.search_button = ttk.Button(input_frame, text="Get Weather", command=self.fetch_weather_threaded)
        self.search_button.pack(side=tk.LEFT, padx=5)

        # Units Frame
        units_frame = ttk.Frame(root, padding="5 0 10 10")
        units_frame.pack(fill=tk.X)
        ttk.Label(units_frame, text="Units:").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(units_frame, text="Metric (°C)", variable=self.units_var, value="metric").pack(side=tk.LEFT)
        ttk.Radiobutton(units_frame, text="Imperial (°F)", variable=self.units_var, value="imperial").pack(side=tk.LEFT)


        # Results Frame (using Labels for better alignment)
        results_frame = ttk.LabelFrame(root, text="Current Weather", padding="10 10 10 10")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Using grid within the results_frame for precise layout
        results_frame.columnconfigure(1, weight=1) # Make the value column expandable

        self.location_label_val = tk.StringVar(value="N/A")
        self.condition_label_val = tk.StringVar(value="N/A")
        self.temp_label_val = tk.StringVar(value="N/A")
        self.feels_like_label_val = tk.StringVar(value="N/A")
        self.humidity_label_val = tk.StringVar(value="N/A")
        self.pressure_label_val = tk.StringVar(value="N/A")
        self.wind_label_val = tk.StringVar(value="N/A")
        self.sunrise_label_val = tk.StringVar(value="N/A")
        self.sunset_label_val = tk.StringVar(value="N/A")
        # Add more StringVars for other data points as needed

        row_num = 0
        ttk.Label(results_frame, text="Location:", font=("Helvetica", 10, "bold")).grid(row=row_num, column=0, sticky="w", pady=2)
        ttk.Label(results_frame, textvariable=self.location_label_val).grid(row=row_num, column=1, sticky="w", pady=2)
        row_num += 1

        ttk.Label(results_frame, text="Condition:", font=("Helvetica", 10, "bold")).grid(row=row_num, column=0, sticky="w", pady=2)
        ttk.Label(results_frame, textvariable=self.condition_label_val).grid(row=row_num, column=1, sticky="w", pady=2)
        row_num += 1

        ttk.Label(results_frame, text="Temperature:", font=("Helvetica", 10, "bold")).grid(row=row_num, column=0, sticky="w", pady=2)
        ttk.Label(results_frame, textvariable=self.temp_label_val).grid(row=row_num, column=1, sticky="w", pady=2)
        row_num += 1

        ttk.Label(results_frame, text="Feels Like:", font=("Helvetica", 10, "bold")).grid(row=row_num, column=0, sticky="w", pady=2)
        ttk.Label(results_frame, textvariable=self.feels_like_label_val).grid(row=row_num, column=1, sticky="w", pady=2)
        row_num += 1

        ttk.Label(results_frame, text="Humidity:", font=("Helvetica", 10, "bold")).grid(row=row_num, column=0, sticky="w", pady=2)
        ttk.Label(results_frame, textvariable=self.humidity_label_val).grid(row=row_num, column=1, sticky="w", pady=2)
        row_num += 1

        ttk.Label(results_frame, text="Pressure:", font=("Helvetica", 10, "bold")).grid(row=row_num, column=0, sticky="w", pady=2)
        ttk.Label(results_frame, textvariable=self.pressure_label_val).grid(row=row_num, column=1, sticky="w", pady=2)
        row_num += 1

        ttk.Label(results_frame, text="Wind:", font=("Helvetica", 10, "bold")).grid(row=row_num, column=0, sticky="w", pady=2)
        ttk.Label(results_frame, textvariable=self.wind_label_val).grid(row=row_num, column=1, sticky="w", pady=2)
        row_num += 1

        ttk.Label(results_frame, text="Sunrise:", font=("Helvetica", 10, "bold")).grid(row=row_num, column=0, sticky="w", pady=2)
        ttk.Label(results_frame, textvariable=self.sunrise_label_val).grid(row=row_num, column=1, sticky="w", pady=2)
        row_num += 1

        ttk.Label(results_frame, text="Sunset:", font=("Helvetica", 10, "bold")).grid(row=row_num, column=0, sticky="w", pady=2)
        ttk.Label(results_frame, textvariable=self.sunset_label_val).grid(row=row_num, column=1, sticky="w", pady=2)
        row_num += 1


        # Status Bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, padding="2 2 2 2")
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Center the window on screen
        self.center_window()

    def center_window(self):
        """Centers the tkinter window."""
        self.root.update_idletasks() # Update geometry info
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def fetch_weather_threaded(self, event=None): # Accept event for Enter key binding
        """Initiates weather fetching in a separate thread."""
        city = self.city_var.get().strip()
        units = self.units_var.get()

        if not city:
            messagebox.showwarning("Input Error", "Please enter a city name.")
            return

        if API_KEY == "YOUR_API_KEY":
             messagebox.showerror("API Key Error", "Please replace 'YOUR_API_KEY' with your actual OpenWeatherMap API key in the script.")
             return

        # Disable button, update status - GUI feedback
        self.search_button.config(state=tk.DISABLED)
        self.status_var.set(f"Fetching weather for {city}...")
        self.clear_results() # Clear previous results

        # Start fetching in a new thread
        thread = threading.Thread(target=self.fetch_weather_task, args=(city, units), daemon=True)
        thread.start()

    def fetch_weather_task(self, city, units):
        """The actual task run in the background thread."""
        raw_data = get_weather_data(city, API_KEY, units)
        display_data = format_weather_display(raw_data, units)

        # Schedule the GUI update back on the main thread
        self.root.after(0, self.update_gui, display_data)


    def update_gui(self, display_data):
        """Updates the GUI elements with weather data. Runs in the main thread."""
        if display_data.get("error"):
            self.status_var.set(f"Error: {display_data['error']}")
            # Optionally show a message box for critical errors
            if display_data.get("error") in ["api_key", "connection", "timeout"]:
                 messagebox.showerror("Error", display_data['message'])
            self.clear_results(keep_location=False) # Clear everything on error
        else:
            self.location_label_val.set(display_data.get("location", "N/A"))
            self.condition_label_val.set(display_data.get("condition", "N/A"))
            self.temp_label_val.set(display_data.get("temp", "N/A"))
            self.feels_like_label_val.set(display_data.get("feels_like", "N/A"))
            self.humidity_label_val.set(display_data.get("humidity", "N/A"))
            self.pressure_label_val.set(display_data.get("pressure", "N/A"))
            self.wind_label_val.set(display_data.get("wind", "N/A"))
            self.sunrise_label_val.set(display_data.get("sunrise", "N/A"))
            self.sunset_label_val.set(display_data.get("sunset", "N/A"))
            self.status_var.set("Weather data updated successfully.")
            # You could potentially load and display the icon here too using PIL/Pillow
            # if display_data.get("icon_code"):
            #    print(f"Icon code: {display_data['icon_code']}") # Placeholder

        # Re-enable the button regardless of success or failure
        self.search_button.config(state=tk.NORMAL)


    def clear_results(self, keep_location=True):
        """Clears the result labels."""
        if not keep_location:
            self.location_label_val.set("N/A")
        self.condition_label_val.set("N/A")
        self.temp_label_val.set("N/A")
        self.feels_like_label_val.set("N/A")
        self.humidity_label_val.set("N/A")
        self.pressure_label_val.set("N/A")
        self.wind_label_val.set("N/A")
        self.sunrise_label_val.set("N/A")
        self.sunset_label_val.set("N/A")


# --- Main Execution ---
if __name__ == "__main__":
    # Basic check before starting GUI
    if API_KEY == "YOUR_API_KEY":
        print("CRITICAL ERROR: Please replace 'YOUR_API_KEY' with your actual OpenWeatherMap API key in the script.")
        print("The application cannot run without a valid API key.")
        # Optionally show a simple tk message box even before main loop
        root_check = tk.Tk()
        root_check.withdraw() # Hide the main window
        messagebox.showerror("API Key Missing", "Please set your OpenWeatherMap API Key in the script file (weather_gui_app.py) before running.")
        root_check.destroy()
        sys.exit(1) # Exit if API key is not set

    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()