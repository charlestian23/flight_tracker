"""flight info module for flight info class"""
import datetime
import pandas as pd

class FlightInfo:
    """
    FlightInfo class
    Attributes:
        details: pandas dataframe with flight details
    """

    def __init__(self, filename):
        # Defines columns for the dataframe
        columns = [
            "YEAR",
            "MONTH",
            "DAY",
            "DAY_OF_WEEK",
            "AIRLINE",
            "FLIGHT_NUMBER",
            "ORIGIN_AIRPORT",
            "DESTINATION_AIRPORT",
            "DEPARTURE_TIME",
            "DIVERTED",
            "CANCELLED",
            "ARRIVAL_TIME",
            "ELAPSED_TIME",
            "ORIGIN_COUNTRY",
            "DESTINATION_COUNTRY",
            "ORIGIN_CONTINENT",
            "DESTINATION_CONTINENT",
            "CARGO",
        ]

        # Defines data types for the columns
        data_types = {
            "YEAR": int,
            "MONTH": int,
            "DAY": int,
            "DAY_OF_WEEK": "string",
            "AIRLINE": "string",
            "FLIGHT_NUMBER": int,
            "ORIGIN_AIRPORT": "string",
            "DESTINATION_AIRPORT": "string",
            "DEPARTURE_TIME": "string",
            "ARRIVAL_TIME": "string",
            "DIVERTED": int,
            "CANCELLED": int,
            "ELAPSED_TIME": int,
            "ORIGIN_COUNTRY": "string",
            "DESTINATION_COUNTRY": "string",
            "ORIGIN_CONTINENT": "string",
            "DESTINATION_CONTINENT": "string",
            "CARGO": bool,
        }

        # Reads the CSV file with the given filename, using only the specified columns and data types
        self.details = pd.read_csv(filename, usecols=columns, dtype=data_types)

        # Pads the DEPARTURE_TIME column to always have 4 digits
        self.details["DEPARTURE_TIME"] = self.details["DEPARTURE_TIME"].str.zfill(4)

        # Extracts the hour and minute from the DEPARTURE_TIME column
        self.details["HOUR"] = self.details["DEPARTURE_TIME"].str[:2]
        self.details["MINUTE"] = self.details["DEPARTURE_TIME"].str[2:]

        # Converts the YEAR, MONTH, DAY, HOUR, and MINUTE columns to a Pandas datetime object in the DEPARTURE_TIME column
        self.details["DEPARTURE_TIME"] = pd.to_datetime(
            self.details[["YEAR", "MONTH", "DAY", "HOUR", "MINUTE"]]
        )

        # Converts the ELAPSED_TIME column to a Pandas timedelta object
        self.details["ELAPSED_TIME"] = pd.to_timedelta(
            self.details["ELAPSED_TIME"], unit="minute"
        )

        # Calculates the ARRIVAL_TIME column by adding the DEPARTURE_TIME and ELAPSED_TIME columns
        self.details["ARRIVAL_TIME"] = (
            self.details["DEPARTURE_TIME"] + self.details["ELAPSED_TIME"]
        )

        # Creates a copy of the full dataset for resetting filters later
        self.full_data = self.details.copy()

    def filter_by_location(self, origin_type, origin_values, dest_type, dest_values):
        """
        Filter by origin and destination
        Parameters:
            origin_type: type of origin filter (airport, country, continent)
            origin_values: list of origin values to filter by
            dest_type: type of destination filter (airport, country, continent)
            dest_values: list of destination values to filter by
        """

        # If there is any "NA" value in the origin_values list, replace it with "UA"
        for i in origin_values:
            if i == "NA":
                origin_values.remove(i)
                origin_values.append("UA")

        # If there is any "NA" value in the dest_values list, replace it with "UA"
        for i in dest_values:
            if i == "NA":
                dest_values.remove(i)
                dest_values.append("UA")

        # Filter the details DataFrame based on the origin and destination types and values
        if origin_type == "airport":
            self.details = self.details[self.details["ORIGIN_AIRPORT"].isin(origin_values)]
        elif origin_type == "country":
            self.details = self.details[self.details["ORIGIN_COUNTRY"].isin(origin_values)]
        elif origin_type == "continent":
            self.details = self.details[self.details["ORIGIN_CONTINENT"].isin(origin_values)]

        if dest_type == "airport":
            self.details = self.details[self.details["DESTINATION_AIRPORT"].isin(dest_values)]
        elif dest_type == "country":
            self.details = self.details[self.details["DESTINATION_COUNTRY"].isin(dest_values)]
        elif dest_type == "continent":
            self.details = self.details[self.details["DESTINATION_CONTINENT"].isin(dest_values)]

    def filter_by_time(self, start_date, start_time, end_date, end_time):
        """
        Filter by time
        Parameters:
            start_date: start date of filter
            start_time: start time of filter
            end_date: end date of filter
            end_time: end time of filter
        """
        # Parse the start and end dates and times into a datetime object
        parsed_start = start_date + "-" + start_time[:2] + "-" + start_time[2:]
        parsed_end = end_date + "-" + end_time[:2] + "-" + end_time[2:]
        depart_time = datetime.datetime.strptime(parsed_start, "%Y-%m-%d-%H-%M")
        arrive_time = datetime.datetime.strptime(parsed_end, "%Y-%m-%d-%H-%M")

        # Filter the details DataFrame based on the departure and arrival times
        self.details = self.details[self.details["DEPARTURE_TIME"] > depart_time]
        self.details = self.details[self.details["ARRIVAL_TIME"] < arrive_time]

    def filter_by_day_of_week(self, days):
        """
        Filter by day of week
        Parameters:
            days: dictionary of days of week to filter by
        """
        # Create a list of selected days based on the input dictionary
        selected_days = []
        for k in days.keys():
            if days[k] == "true":
                selected_days.append(k)

        # Filter the details DataFrame based on the selected days
        self.details = self.details[self.details["DAY_OF_WEEK"].isin(selected_days)]

    def filter_by_airline(self, airlines):
        """
        Filter by airline
        Parameters:
            airlines: list of airlines to filter by
        """
        # Filter the details DataFrame based on the input list of airlines
        self.details = self.details[self.details["AIRLINE"].isin(airlines)]

    def filter_by_cargo(self, is_cargo, is_passenger):
        """
        Filter by cargo or passenger
        Parameters:
            is_cargo: boolean for if cargo flights should be included
            is_passenger: boolean for if passenger flights should be included
        """
        # Check if filter should include cargo flights only
        if is_cargo == "true" and is_passenger == "false":
            self.details = self.details[self.details["CARGO"] == 1]
        # Check if filter should include passenger flights only
        elif is_cargo == "false" and is_passenger == "true":
            self.details = self.details[self.details["CARGO"] == 0]

    def filter_by_added(self, req):
        """
        Filter by added
        Parameters:
            req: request object containing start and end dates
        """

        # Parsing start and end dates from request object
        parsed_start1 = (
            req.start_date + "-" + req.start_time[:2] + "-" + req.start_time[2:]
        )
        parsed_end1 = req.end_date + "-" + req.end_time[:2] + "-" + req.end_time[2:]

        # Parsing start and end dates from advanced request object
        parsed_start2 = (
            req.adv_req.start_date
            + "-"
            + req.adv_req.start_time[:2]
            + "-"
            + req.adv_req.start_time[2:]
        )
        parsed_end2 = (
            req.adv_req.end_date
            + "-"
            + req.adv_req.end_time[:2]
            + "-"
            + req.adv_req.end_time[2:]
        )

        # Converting parsed dates to datetime format
        depart1 = datetime.datetime.strptime(parsed_start1, "%Y-%m-%d-%H-%M")
        arrive1 = datetime.datetime.strptime(parsed_end1, "%Y-%m-%d-%H-%M")
        depart2 = datetime.datetime.strptime(parsed_start2, "%Y-%m-%d-%H-%M")
        arrive2 = datetime.datetime.strptime(parsed_end2, "%Y-%m-%d-%H-%M")

        # Filtering flights based on departure and arrival times
        flights1 = self.details[
            (self.details["DEPARTURE_TIME"] > depart1)
            & (self.details["ARRIVAL_TIME"] < arrive1)
        ]
        flights2 = self.full_data[
            (self.full_data["DEPARTURE_TIME"] > depart2)
            & (self.full_data["ARRIVAL_TIME"] < arrive2)
        ]

        # Filtering flights based on airlines
        flights2 = flights2[flights2["AIRLINE"].isin(req.airlines)]

        # Copying flights2 dataframe to added_flights dataframe
        added_flights = flights2.copy()

        # Iterating over flights2 dataframe and removing any overlapping flights with flights1 dataframe
        for index, f in flights2.iterrows():
            temp = flights1[
                (flights1["DAY_OF_WEEK"] == f["DAY_OF_WEEK"])
                & (flights1["HOUR"] == f["HOUR"])
                & (flights1["MINUTE"] == f["MINUTE"])
                & (flights1["AIRLINE"] == f["AIRLINE"])
                & (flights1["ORIGIN_AIRPORT"] == f["ORIGIN_AIRPORT"])
                & (flights1["DESTINATION_AIRPORT"] == f["DESTINATION_AIRPORT"])
            ]
            if temp.shape[0] > 0:
                added_flights.drop(index, inplace=True)

        # Updating self.details dataframe with added_flights dataframe
        self.details = added_flights


    def filter_by_removed(self, req):
        """
        Filter by removed
        Parameters:
            req: request object containing start and end dates
        """

        # Parse the start and end dates
        parsed_start1 = (
            req.start_date + "-" + req.start_time[:2] + "-" + req.start_time[2:]
        )
        parsed_end1 = req.end_date + "-" + req.end_time[:2] + "-" + req.end_time[2:]

        # Parse the start and end dates from the advanced request
        parsed_start2 = (
            req.adv_req.start_date
            + "-"
            + req.adv_req.start_time[:2]
            + "-"
            + req.adv_req.start_time[2:]
        )
        parsed_end2 = (
            req.adv_req.end_date
            + "-"
            + req.adv_req.end_time[:2]
            + "-"
            + req.adv_req.end_time[2:]
        )

        # Convert parsed dates to datetime objects
        depart1 = datetime.datetime.strptime(parsed_start1, "%Y-%m-%d-%H-%M")
        arrive1 = datetime.datetime.strptime(parsed_end1, "%Y-%m-%d-%H-%M")
        depart2 = datetime.datetime.strptime(parsed_start2, "%Y-%m-%d-%H-%M")
        arrive2 = datetime.datetime.strptime(parsed_end2, "%Y-%m-%d-%H-%M")

        # Get flights within the specified date range
        flights1 = self.details[
            (self.details["DEPARTURE_TIME"] > depart1)
            & (self.details["ARRIVAL_TIME"] < arrive1)
        ]
        flights2 = self.full_data[
            (self.full_data["DEPARTURE_TIME"] > depart2)
            & (self.full_data["ARRIVAL_TIME"] < arrive2)
        ]

        # Filter flights by airlines specified in request object
        flights2 = flights2[flights2["AIRLINE"].isin(req.airlines)]

        # Make a copy of flights within the specified date range
        removed_flights = flights1.copy()

        # Iterate over flights within the specified date range
        for index, f in flights1.iterrows():

            # Find flights that match the current flight within the advanced request
            temp = flights2[
                (flights2["DAY_OF_WEEK"] == f["DAY_OF_WEEK"])
                & (flights2["HOUR"] == f["HOUR"])
                & (flights2["MINUTE"] == f["MINUTE"])
                & (flights2["AIRLINE"] == f["AIRLINE"])
                & (flights2["ORIGIN_AIRPORT"] == f["ORIGIN_AIRPORT"])
                & (flights2["DESTINATION_AIRPORT"] == f["DESTINATION_AIRPORT"])
            ]

            # If a matching flight is found, remove the current flight from the list of removed flights
            if temp.shape[0] > 0:
                removed_flights.drop(index, inplace=True)

        # Update the details with the list of removed flights
        self.details = removed_flights


    def filter_by_stops(self, req):
        """
        Filter by stops
        Parameters:
            req: request object containing origin and destination airports,
                 number of stops, start and end dates and times
        """
        origin = req.origin_values
        destination = req.dest_values
        stops = req.num_layovers
        start_date = req.start_date
        start_time = req.start_time
        parsed_start = start_date + "-" + start_time[:2] + "-" + start_time[2:] # combine date and time into a single string
        end_date = req.end_date
        end_time = req.end_time
        parsed_end = end_date + "-" + end_time[:2] + "-" + end_time[2:] # combine date and time into a single string
        depart_time = datetime.datetime.strptime(parsed_start, "%Y-%m-%d-%H-%M") # convert string to datetime object
        arrive_time = datetime.datetime.strptime(parsed_end, "%Y-%m-%d-%H-%M") # convert string to datetime object
        visited = [] # initialize list of visited airports
        path = [] # initialize list of paths
        flightinfo = [] # initialize list of flight information
        temp = [] # initialize temporary list of flight information
        if int(stops) > 0: # only run if number of stops is greater than 0
            stop_helper(
                self.full_data, # all available flight data
                self.full_data, # copy of all available flight data
                origin, # starting airport
                destination, # ending airport
                int(stops), # number of stops
                depart_time, # start time
                arrive_time, # end time
                visited, # list of visited airports
                path, # list of paths
                flightinfo, # list of flight information
                temp, # temporary list of flight information
            )
            flatten = [element for sublist in flightinfo for element in sublist] # flatten list of flight information
            combined = pd.concat(flatten).drop_duplicates() # combine all flight information into a single dataframe and remove duplicates
            eu = ["EU"]
            KATL = ["KATL"]
            KLAX = ["KLAX"]
            combined = combined.query("DESTINATION_CONTINENT != @eu") # remove flights to Europe
            combined = combined.query("DESTINATION_AIRPORT != @KATL") # remove flights to Atlanta
            combined = combined.query("DESTINATION_AIRPORT != @KLAX") # remove flights to Los Angeles
            self.details = combined # update details attribute with filtered flight information


def stop_helper(
    flights,
    flights_copy,
    origin,
    destination,
    stops,
    depart_time,
    arrive_time,
    visited,
    path=[],
    flightinfo=[],
    temp=[],
):
    # Check if origin and destination are the same
    if origin == destination:
        print("end")
        # Add destination to the path
        path.append(destination)
        # If path is not in visited, add path and temp to flightinfo
        if path not in visited:
            visited.append(path)
            flightinfo.append(temp)
        return

    # make a copy of all flights
    flights_copy = flights.copy()
    # Filter flights_copy to contain only flights with origin in origin list
    flights_copy = flights_copy[flights_copy["ORIGIN_AIRPORT"].isin(origin)]
    # Filter flights_copy to contain only flights with departure time after depart_time
    flights_copy = flights_copy.query("DEPARTURE_TIME > @depart_time")
    # Filter flights_copy to contain only flights with arrival time before arrive_time
    flights_copy = flights_copy[flights_copy["ARRIVAL_TIME"] < arrive_time]

    # Loop through all destinations in flights_copy
    for dest in flights_copy["DESTINATION_AIRPORT"]:
        # If dest is not already in path
        if dest not in path:
            print(dest)
            # Create a list with the current destination
            lst_dest = [dest]
            # Append origin to the path
            path.append(origin)
            # Append flights_copy to temp
            temp.append(flights_copy)
            # Recursively call stop_helper function with the new destination in lst_dest
            stop_helper(
                flights,
                flights_copy,
                lst_dest,
                destination,
                int(stops),
                depart_time,
                arrive_time,
                visited,
                path,
                flightinfo,
                temp,
            )
            # Reset temp and path to empty lists
            temp = []
            path = []
