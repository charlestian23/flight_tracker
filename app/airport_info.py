import csv
import json

# Load country data from JSON file
with open("./data/countries.json", encoding="utf8") as csv_file:
    country_data = json.load(csv_file)

# Define a function to get the country code from a country name
def get_country_code(country):
    """
    Get the country code from the country name.
    :param country: The country name.
    :return: The country code.
    """
    # Map certain country names to their correct names in the dataset
    if country == "North Korea":
        country = "Korea (Democratic People's Republic of"
    elif country == "South Korea":
        country = "Korea, Republic of"
    elif country == "Laos":
        country = "Lao People's Democratic Republic"
    elif country == "British Virgin Islands":
        country = "Virgin Islands (British)"
    elif country == "Macau":
        country = "Macao"
    elif country == "Congo (Brazzaville)":
        country = "Congo"
    elif country == "Congo (Kinshasa)":
        country = "Congo, Democratic Republic of the"
    elif country == "Czech Republic":
        country = "Czechia"
    elif country == "Reunion":
        country = "Réunion"
    elif country == "Cape Verde":
        country = "Cabo Verde"

    # Search for the country in the country data and return the corresponding code
    for item in country_data:
        if country.strip().upper() in item["name"].strip().upper():
            return item["alpha-2"]
    return None

# Initialize an empty dictionary to hold airport data
data = {}
INDENT = 4

# The flights you want to limit to
limit = ["VHHH", "ZSPD", "EGLL", "KJFK", "KLAX", "KATL", "EDDF", "MMMX"]

# Load airport data from CSV file
with open("./data/airports.dat.txt", encoding="utf8") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=",")

    # Loop over each row in the CSV file
    for row in csv_reader:
        # Create a dictionary to hold data for the current airport
        current_airport = {"name": row[1], "city": row[2]}

        # Map certain country names to their correct names in the dataset
        if row[3] == "Burma":
            current_airport["country"] = "Myanmar"
        elif row[3] == "Netherlands Antilles":
            current_airport["country"] = "Netherlands"
        else:
            current_airport["country"] = row[3]

        # Look up the country code for the current airport
        current_airport["country_code"] = get_country_code(current_airport["country"])

        # Add latitude and longitude data for the current airport
        current_airport["lat"] = float(row[6])
        current_airport["lng"] = float(row[7])

        # Get the ICAO code for the current airport
        icao_code = row[5]

        # Add data for the current airport to the data dictionary if it is in the limit list or if the limit list is empty
        if icao_code in limit or len(limit) == 0:
            data[icao_code] = current_airport

# Convert the data dictionary to a JSON object
json_object = json.dumps(data, indent=INDENT)

# Write the JSON object to a file
with open("./static/airports.json", "w", encoding="utf8") as file:
    file.write(json_object)
