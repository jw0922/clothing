from flask import Flask, render_template, request, send_from_directory
from recommend import recommend_clothing_for_today  # Import the clothing recommendation function
import os
from generate_plot import generate_thickness_temperature_plot  # Import the function to generate the plot

app = Flask(__name__)

# Home page, where the user inputs the city
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        city = request.form["city"]
        recommended_clothing = recommend_clothing_for_today(city)  # Call the recommendation function
        return render_template("result.html", clothing=recommended_clothing)
    return render_template("index.html")

# Generate and display the chart
@app.route("/show_chart")
def show_chart():
    # Call the function to generate the plot
    plot_path = generate_thickness_temperature_plot()
    if plot_path:
        return render_template("index.html", plot_path=plot_path)
    else:
        return "Error generating the plot."

# Return the plot image file
@app.route("/static/<path:filename>")
def send_plot(filename):
    return send_from_directory(os.path.join(app.root_path, 'static'), filename)

# Run the application
if __name__ == "__main__":
    app.run(debug=True, port=5001)
