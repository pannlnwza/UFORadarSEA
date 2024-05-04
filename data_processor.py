import datetime
import pandas as pd
import numpy as np


class UFODataProcessor:
    def __init__(self, ufo_reports_file, airports_file):
        self.ufo_reports = pd.read_csv(ufo_reports_file)
        self.airports = pd.read_csv(airports_file)

    def separate_datetime(self):
        # Separate date_time_found into year_found, month, and hour
        self.ufo_reports['date_time_found'] = pd.to_datetime(self.ufo_reports['date_time_found'])
        self.ufo_reports['year_found'] = self.ufo_reports['date_time_found'].dt.year
        self.ufo_reports['month'] = self.ufo_reports['date_time_found'].dt.month
        self.ufo_reports['hour'] = self.ufo_reports['date_time_found'].dt.hour

    def haversine_distance(self, lat1, lon1, lat2, lon2):
        # Calculate the great-circle distance between two points
        R = 6371  # Radius of the Earth in kilometers
        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
        c = 2 * np.arcsin(np.sqrt(a))
        distance = R * c
        return distance

    def find_nearest_airport_distance(self):
        # Function to find the distance of each UFO report to the nearest airport
        def nearest_airport_distance(row):
            min_distance = float('inf')
            for _, airport in self.airports.iterrows():
                distance = self.haversine_distance(row['latitude'], row['longitude'], airport['latitude_deg'],
                                                   airport['longitude_deg'])
                min_distance = min(min_distance, distance)
            return min_distance

        self.ufo_reports['distance_to_nearest_airport_km'] = self.ufo_reports.apply(nearest_airport_distance, axis=1)

    def save_to_csv(self, filename):
        # Save the processed UFO report data to a CSV file
        self.ufo_reports['date_documented'] = datetime.date.today().strftime('%m/%d/%Y')
        self.ufo_reports.to_csv(filename, index=False)

    def get_ufo_data(self):
        return self.ufo_reports
