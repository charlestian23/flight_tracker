"""The application"""
from flask import Flask, render_template, request
from flight_info import FlightInfo
from request import Request

# Set the filename of the data to be used
FILENAME = "./data/testing_data.csv"

# Create a Flask app
app = Flask(__name__)

# Initialize a FlightInfo object with the filename
flights = FlightInfo(FILENAME)

# Define the home route
@app.route("/")
def home():
    """The home page"""
    return render_template("index.html")

# Define the form route
@app.route("/form")
def form():
    """The form page"""
    # Get the value of the "form" cookie
    name = request.cookies.get("form")

    # Create a Request object with the name value
    req = Request(name)

    # Copy the full data to the details attribute of the FlightInfo object
    flights.details = flights.full_data.copy()

    # Filter the flights by location using the origin and destination types and values
    flights.filter_by_location(
        req.origin_type, req.origin_values, req.dest_type, req.dest_values
    )

    # Filter the flights by time using the start and end dates and times
    flights.filter_by_time(req.start_date, req.start_time, req.end_date, req.end_time)

    # Filter the flights by day of the week
    flights.filter_by_day_of_week(req.day_of_week)

    # Filter the flights by airline
    flights.filter_by_airline(req.airlines)

    # Filter the flights by cargo and passenger status
    flights.filter_by_cargo(req.is_cargo, req.is_passenger)

    # Filter the flights by stops
    flights.filter_by_stops(req)

    # If the "filter_added" attribute of the advanced request is "true", filter the flights by added flights
    if req.adv_req.filter_added == "true":
        flights.filter_by_added(req)

    # If the "filter_removed" attribute of the advanced request is "true", filter the flights by removed flights
    if req.adv_req.filter_removed == "true":
        flights.filter_by_removed(req)

    # Create a set of tuples containing the origin airport, destination airport, airline, and cargo status for each flight
    ret_val = set()
    for _, row in flights.details.iterrows():
        origin_airport = row["ORIGIN_AIRPORT"]
        destination_airport = row["DESTINATION_AIRPORT"]
        airline = row["AIRLINE"]
        is_cargo = str(row["CARGO"]).lower()

        ret_val.add((origin_airport, destination_airport, airline, is_cargo))

    # Convert the set of tuples to a list of lists
    ret_val_list = []
    for item in ret_val:
        ret_val_list.append([item[0], item[1], item[2], item[3]])

    # Print the return dataframe
    print("\nReturn Dataframe:\n", ret_val_list)

    # Return the list of flights as a string
    return f"{ret_val_list}"
