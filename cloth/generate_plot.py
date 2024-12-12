import matplotlib.pyplot as plt
from pymongo import MongoClient
from datetime import datetime, timedelta
import os

# Function to fetch the most recent data from MongoDB
def get_recent_data():
    # Connect to MongoDB
    mongodb_uri = "mongodb+srv://wjie0922:e98043ty@clothes.hxcxq.mongodb.net/?retryWrites=true&w=majority&appName=clothes"
    client = MongoClient(mongodb_uri)
    db = client["clothing"]
    collection = db["wearing_habits"]

    # Find the most recent record from the database
    latest_record = collection.find_one(sort=[("date", -1)])  # Sort by date in descending order
    if not latest_record:
        print("Database is empty. No data available.")
        return []  # Return empty list if no records are found

    latest_date = datetime.strptime(latest_record["date"], "%Y-%m-%d")
    seven_days_ago = latest_date - timedelta(days=7)

    # Fetch data from the last 7 days or from the most recent date to 7 days back
    data = list(collection.find({
        "date": {
            "$gte": seven_days_ago.strftime("%Y-%m-%d"),
            "$lte": latest_date.strftime("%Y-%m-%d")
        }
    }))

    return data

# Function to generate a plot for temperature and clothing thickness over time
def generate_thickness_temperature_plot():
    data = get_recent_data()
    if not data:
        print("No data available.")
        return None  # Return None if no data is available

    # Extract dates, temperatures, and thickness values from the data
    dates = sorted(list(set([item["date"] for item in data])))  # Ensure dates are sorted
    temperatures = []
    thicknesses = []
    
    for date in dates:
        # Calculate the average temperature for each date
        temp = sum(item["temperature"] for item in data if item["date"] == date) / len(
            [item for item in data if item["date"] == date]
        )
        # Sum the thickness for each date
        thick = sum(int(item["thickness"]) for item in data if item["date"] == date)
        temperatures.append(temp)
        thicknesses.append(thick)

    # Create a plot
    plt.figure(figsize=(10, 5))
    plt.plot(dates, temperatures, label="Temperature (°C)", color="blue", marker="o")
    plt.plot(dates, thicknesses, label="Clothing Thickness", color="orange", marker="o")
    plt.xlabel("Date")
    plt.ylabel("Value")
    plt.title("Clothing Thickness and Temperature Over Time")
    plt.legend()
    plt.xticks(rotation=45)  # Rotate date labels for better readability
    plt.tight_layout()

    # Save the plot to the static folder
    static_dir = "static"
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)  # Create the static folder if it doesn't exist
    plot_path = os.path.join(static_dir, "plot.png")
    plt.savefig(plot_path)  # Save the plot as an image
    plt.close()  # Close the plot to free memory

    return plot_path  # Return the path to the saved plot image
