"""
module for flights
"""
import datetime


class Flight:
    """
    Flight class
        Attributes:
            flight_time: flight time in minutes
            departure_time: departure time as a datetime object
            arrival_time: arrival time as a datetime object
            origin: origin airport ICAO code
            destination: destination airport ICAO code
    """

    def __init__(self, flight_info):
        # initialize the object with the provided flight_info dictionary
        self.flight_time = int(flight_info["ELAPSED_TIME"])

        # create a datetime object for departure time from the provided date and time information
        self.departure_time = datetime.datetime(
            year=int(flight_info["YEAR"]),
            month=int(flight_info["MONTH"]),
            day=int(flight_info["DAY"]),
            hour=int(flight_info["DEPARTURE_TIME"].zfill(4)[:2]),
            minute=int(flight_info["DEPARTURE_TIME"].zfill(4)[2:]),
        )

        # calculate the arrival time by adding flight time to the departure time
        self.arrival_time = self.departure_time + datetime.timedelta(
            minutes=self.flight_time
        )

        # set the origin and destination airport ICAO codes
        self.origin = flight_info["ORIGIN_AIRPORT"]
        self.destination = flight_info["DESTINATION_AIRPORT"]

    def __str__(self):
        # return a string representation of the object
        ret_val = "\nOrigin: " + self.origin + "\n"
        ret_val += "Destination: " + self.destination + "\n"
        ret_val += (
            "Departure Time: " + self.departure_time.strftime("%m/%d/%Y %H:%M") + "\n"
        )
        ret_val += (
            "Arrival Time: " + self.arrival_time.strftime("%m/%d/%Y %H:%M") + "\n"
        )
        ret_val += "Flight Time: " + str(self.flight_time) + " minutes"

        return ret_val

    def __repr__(self):
        # return a string representation of the object
        return self.__str__()
