import serial
import pymongo
import requests
import datetime
import geocoder  # For obtaining the user's geographical location

# Configure Arduino serial communication
arduino_port = 'COM5'  # Adjust according to your actual port
baud_rate = 9600
ser = serial.Serial(arduino_port, baud_rate)

# Configure MongoDB
mongodb_uri = "mongodb+srv://wjie0922:e98043ty@clothes.hxcxq.mongodb.net/?retryWrites=true&w=majority&appName=clothes"
client = pymongo.MongoClient(mongodb_uri)
db = client["clothing"]

# Clothing information collection
clothing_collection = db["clothing_info"]
wearing_habits_collection = db["wearing_habits"]

# Weather API configuration
weather_api_url = "https://api.openweathermap.org/data/2.5/weather"
weather_api_key = "f546aaad1a06810fc51b9b56d0a47354"

def get_location():
    """Get the user's geographical location (via IP address)"""
    g = geocoder.ip('me')  # Get the current device's IP address location
    city = g.city  # Extract the city name
    if not city:
        print("Could not retrieve city. Defaulting to London.")
        city = "London"  # Default to London if city is not found
    return city

def get_weather_data(city):
    """Get current weather information"""
    params = {"q": city, "appid": weather_api_key, "units": "metric"}
    response = requests.get(weather_api_url, params=params)
    if response.status_code == 200:
        data = response.json()
        return {
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "weather_description": data["weather"][0]["description"]
        }
    else:
        print("Failed to get weather data.")
        return None

def add_clothing(tag_id):
    """Add clothing information"""
    clothing_type = input("Enter Clothing Type: ")
    season = input("Enter Season: ")
    color = input("Enter Color: ")
    style = input("Enter Style: ")
    material = input("Enter Material: ")
    thickness = input("Enter Thickness: ")

    clothing_data = {
        "tag_id": tag_id,
        "clothing_type": clothing_type,
        "season": season,
        "color": color,
        "style": style,
        "material": material,
        "thickness": thickness
    }
    clothing_collection.insert_one(clothing_data)
    print("Clothing information saved successfully.")

def record_wearing_habit(tag_id):
    """Record wearing habit"""
    clothing_data = clothing_collection.find_one({"tag_id": tag_id})
    if not clothing_data:
        print("No clothing found for this tag ID.")
        return

    city = get_location()  # Automatically get the user's city
    weather_data = get_weather_data(city)
    if weather_data:
        # Record only the date (without time)
        date = datetime.date.today().strftime("%Y-%m-%d")
        habit_data = {
            "tag_id": tag_id,
            "clothing_type": clothing_data["clothing_type"],
            "season": clothing_data["season"],
            "color": clothing_data["color"],
            "style": clothing_data["style"],
            "material": clothing_data["material"],
            "thickness": clothing_data["thickness"],
            "temperature": weather_data["temperature"],
            "humidity": weather_data["humidity"],
            "weather_description": weather_data["weather_description"],
            "date": date  # Save only the year, month, and day
        }
        wearing_habits_collection.insert_one(habit_data)
        print("Wearing habit recorded successfully.")

# Main program loop
while True:
    mode = input("Select Mode (1: Add Clothing, 2: Record Wearing Habit, 3: Exit): ")
    
    if mode == '1':  # Add clothing information
        print("You have entered Add Clothing mode.")
        while True:
            print("Please place the NTAG card...")

            # Wait for valid tag input
            while True:
                if ser.in_waiting > 0:
                    data = ser.readline().decode().strip()
                    if len(data) > 0:  # Ensure valid tag data is received
                        print(f"Detected Tag ID: {data}")
                        tag_id = data
                        break

            add_clothing(tag_id)

    elif mode == '2':  # Record wearing habit
        print("You have entered Record Wearing Habit mode.")
        while True:
            print("Please place the NTAG card...")

            # Wait for valid tag input
            while True:
                if ser.in_waiting > 0:
                    data = ser.readline().decode().strip()
                    if len(data) > 0:  # Ensure valid tag data is received
                        print(f"Detected Tag ID: {data}")
                        tag_id = data
                        break

            record_wearing_habit(tag_id)

    elif mode == '3':  # Exit the program
        print("Exiting program.")
        break
