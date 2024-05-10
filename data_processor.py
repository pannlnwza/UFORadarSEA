import enum
import os
import datetime
from math import radians, sin, cos, sqrt, atan2
import pandas as pd


class UFODataProcessor:
    """
    A class for processing UFO data.
    """

    def __init__(self, ufo_reports_file, airports_file):
        """
        Initialize UFODataProcessor class.

        :param ufo_reports_file: Path to the UFO reports CSV file.
        :type ufo_reports_file: pd.Dataframe
        :param airports_file: Path to the airports CSV file.
        :type airports_file: pd.Dataframe
        """
        self.ufo_reports = pd.read_csv(ufo_reports_file)
        self.airports = pd.read_csv(airports_file)
        self.new_row = {}

    def get_ufo_data(self) -> pd.DataFrame:
        """
        Get UFO sighting data.

        :return: DataFrame containing UFO sighting data.
        :rtype: pandas.DataFrame
        """
        return self.ufo_reports

    def find_nearest_airport(self, latitude: float, longitude: float, airport_data: pd.DataFrame) -> float:
        """
        Find the nearest airport to a given location.

        :param latitude: Latitude of the location.
        :type latitude: float
        :param longitude: Longitude of the location.
        :type longitude: float
        :param airport_data: DataFrame containing airport data.
        :type airport_data: pandas.DataFrame
        :return: Minimum airport distance.
        :rtype: float
        """
        min_distance = float('inf')

        for _, airport in airport_data.iterrows():
            airport_lat = airport['LAT']
            airport_lon = airport['LONG']
            distance = self.haversine_distance(latitude, longitude, airport_lat, airport_lon)
            if distance < min_distance:
                min_distance = distance
        return min_distance

    def save_to_csv(self, date_time_found: str, country: str, location: str, latitude: float,
                    longitude: float, ufo_shape: str, length_of_encounter_seconds: float, description: str):
        """
        Save UFO sighting data to a CSV file.
        """
        report_no = self.ufo_reports.loc[len(self.ufo_reports)-1]['report_no'] + 1
        min_distance = self.find_nearest_airport(float(latitude), float(longitude), self.airports)
        year_found, month, hour = self.separate_datetime(date_time_found)
        season = self.month_to_season(month)
        date_documented = datetime.date.today().strftime('%m/%d/%Y')
        country_code = Country.find_val(country, 1)
        self.new_row = {'report_no': report_no,
                        'date_documented': date_documented,
                        'date_time_found': date_time_found,
                        'year_found': year_found,
                        'month': month,
                        'hour': hour,
                        'season': season,
                        'country_code': country_code,
                        'country': country,
                        'location': location,
                        'latitude': latitude,
                        'longitude': longitude,
                        'UFO_shape': ufo_shape,
                        'length_of_encounter_seconds': length_of_encounter_seconds,
                        'distance_to_nearest_airport_km': min_distance,
                        'description': description.strip()
                        }
        self.ufo_reports.loc[len(self.ufo_reports)] = self.new_row
        current_dir = os.getcwd()
        ufo_data = os.path.join(current_dir, 'data', 'nuforc_data.csv')
        self.ufo_reports.to_csv(ufo_data, mode='w', index=False)

    @staticmethod
    def separate_datetime(date_time) -> tuple:
        """
        Separate datetime into year, month, and hour.

        :param date_time: Datetime string.
        :type date_time: str
        :return: Year, month, and hour.
        :rtype: tuple
        """
        date_time = pd.to_datetime(date_time)
        year_found = date_time.year
        month_found = date_time.month
        hour_of_the_day = date_time.hour
        return year_found, month_found, hour_of_the_day

    @staticmethod
    def month_to_season(month: int) -> str:
        """
        Convert month to season.

        :param month: Month.
        :type month: int
        :return: Season corresponding to the month.
        :rtype: str
        """
        if month in [3, 4, 5]:
            return 'Spring'
        if month in [6, 7, 8]:
            return 'Summer'
        if month in [9, 10, 11]:
            return 'Autumn/Fall'
        return 'Winter'

    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate the Haversine distance between two points on the Earth's surface.

        :param lat1: Latitude of the first point in degrees.
        :type lat1: float
        :param lon1: Longitude of the first point in degrees.
        :type lon1: float
        :param lat2: Latitude of the second point in degrees.
        :type lat2: float
        :param lon2: Longitude of the second point in degrees.
        :type lon2: float
        :return: Distance between the two points in kilometers.
        :rtype: float
        """
        # Radius of the Earth in kilometers
        R = 6371.0

        # Convert latitude and longitude from degrees to radians
        lat1 = radians(float(lat1))
        lon1 = radians(float(lon1))
        lat2 = radians(float(lat2))
        lon2 = radians(float(lon2))

        # Calculate differences in latitude and longitude
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        # Haversine formula to calculate distance
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = R * c  # Distance in kilometers
        return distance


class Country(enum.Enum):
    BRUNEI = ['Brunei', 'BRN', 4.5, 114.6667]
    CAMBODIA = ['Cambodia', 'KHM', 13.0, 105.0]
    EAST_TIMOR = ['East Timor', 'TLS', -8.55, 125.5167]
    INDONESIA = ['Indonesia', 'IDN', -5.0, 120]
    LAOS = ['Laos', 'LAO', 18.0, 105.0]
    MALAYSIA = ['Malaysia', 'MYS', 2.5, 112.5]
    MYANMAR = ['Myanmar', 'MMR', 22.0, 98.0]
    PHILIPPINES = ['Philippines', 'PHL', 13.0, 122.0]
    SINGAPORE = ['Singapore', 'SG', 1.3667, 103.8]
    THAILAND = ['Thailand', 'THA', 15.0, 100.0]
    VIETNAM = ['Vietnam', 'VNM', 16.0, 106.0]

    @classmethod
    def find_val(cls, country_name, index):
        for country in cls:
            if country.value[0].lower() == country_name.lower():
                return country.value[index]
        return None