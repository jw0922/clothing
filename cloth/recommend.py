import requests
import pymongo

# Connect to MongoDB database
mongodb_uri = "mongodb+srv://wjie0922:e98043ty@clothes.hxcxq.mongodb.net/?retryWrites=true&w=majority&appName=clothes"
client = pymongo.MongoClient(mongodb_uri)
db = client["clothing"]

# Access collections for clothing information and wearing habits
clothing_collection = db["clothing_info"]
wearing_habits_collection = db["wearing_habits"]

# Function to fetch current weather data for a given city
def get_weather_data(city):
    api_key = "f546aaad1a06810fc51b9b56d0a47354"  # Replace with your OpenWeatherMap API key
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    
    try:
        # Request weather data from the API
        response = requests.get(url)
        weather_data = response.json()
        
        # Check if the API call was successful
        if weather_data["cod"] != 200:
            print("Failed to retrieve weather data.")
            return None
        
        # Return temperature and weather description
        return {
            "temperature": weather_data["main"]["temp"],  # Current temperature
            "description": weather_data["weather"][0]["description"]  # Weather description
        }
    
    except Exception as e:
        print(f"Error getting weather data: {e}")
        return None

# Function to fetch historical wearing habits and calculate average thickness
def get_historical_clothing_data(temperature):
    # Query historical wearing habits within a ±3°C range of the current temperature
    historical_data = wearing_habits_collection.find({
        "temperature": {"$gte": temperature - 3, "$lte": temperature + 3}
    }, {"temperature": 1, "clothing_type": 1, "thickness": 1, "_id": 0})
    
    historical_clothing_data = list(historical_data)
    
    # Helper function to calculate average thickness for a specific clothing type
    def calculate_average_thickness(data, clothing_type):
        thicknesses = [float(item["thickness"]) for item in data if item["clothing_type"] == clothing_type]
        return sum(thicknesses) / len(thicknesses) if thicknesses else 0

    avg_pants_thickness = calculate_average_thickness(historical_clothing_data, "pants")
    avg_outerwear_thickness = calculate_average_thickness(historical_clothing_data, "outerwear")
    avg_innerwear_thickness = calculate_average_thickness(historical_clothing_data, "innerwear")
    
    return avg_pants_thickness, avg_outerwear_thickness, avg_innerwear_thickness

# Function to recommend clothing based on the current weather and historical data
def recommend_clothing_for_today(city):
    # Fetch current weather data
    weather_data = get_weather_data(city)
    if weather_data is None:
        print("Failed to get weather data.")
        return
    
    temperature = weather_data["temperature"]
    print(f"Current Temperature: {temperature}°C")
    
    # Calculate average thickness based on historical data
    avg_pants_thickness, avg_outerwear_thickness, avg_innerwear_thickness = get_historical_clothing_data(temperature)
    
    # Define thickness range ±1 for recommendations
    lower_pants_thickness = avg_pants_thickness - 1
    upper_pants_thickness = avg_pants_thickness + 1
    
    lower_outerwear_thickness = avg_outerwear_thickness - 1
    upper_outerwear_thickness = avg_outerwear_thickness + 1
    
    lower_innerwear_thickness = avg_innerwear_thickness - 1
    upper_innerwear_thickness = avg_innerwear_thickness + 1
    
    # Recommend pants based on thickness range
    recommended_pants = list(clothing_collection.find({
        "clothing_type": "pants",
        "thickness": {"$gte": lower_pants_thickness, "$lte": upper_pants_thickness}
    }).limit(1))
    
    # Recommend outerwear based on thickness range
    recommended_outerwear = list(clothing_collection.find({
        "clothing_type": "outerwear",
        "thickness": {"$gte": lower_outerwear_thickness, "$lte": upper_outerwear_thickness}
    }).limit(1))
    
    # Recommend innerwear based on thickness range
    recommended_innerwear = list(clothing_collection.find({
        "clothing_type": "innerwear",
        "thickness": {"$gte": lower_innerwear_thickness, "$lte": upper_innerwear_thickness}
    }).limit(1))
    
    # Return recommended clothing
    return {
        "temperature": temperature,
        "pants": recommended_pants[0] if recommended_pants else None,
        "outerwear": recommended_outerwear[0] if recommended_outerwear else None,
        "innerwear": recommended_innerwear[0] if recommended_innerwear else None
    }

# Test the recommendation function
city = "London"  # Specify the city
recommended_clothing = recommend_clothing_for_today(city)

# Print the recommended clothing
if recommended_clothing:
    print("Recommended Clothing:")
    print(f"Temperature: {recommended_clothing['temperature']}°C")
    if recommended_clothing["pants"]:
        print(f"Pants: {recommended_clothing['pants']}")
    if recommended_clothing["outerwear"]:
        print(f"Outerwear: {recommended_clothing['outerwear']}")
    if recommended_clothing["innerwear"]:
        print(f"Innerwear: {recommended_clothing['innerwear']}")
