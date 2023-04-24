import argparse
import asyncio

from geopy.geocoders import Nominatim
from geopy.location import Location

import requests
from requests.exceptions import RequestException

from exceptions import NoneRequestException


def find_geocode(city: str) -> Location:
    geolocator = Nominatim(user_agent='my_app')
    return geolocator.geocode(city)


def get_lon_and_lat(geocode: Location) -> list[float]:
    coordinates = list()

    if geocode:
        loc = geocode

        coordinates.append(loc.latitude)
        coordinates.append(loc.longitude)
    return coordinates


class WeatherFetcher:

    def __init__(self, city):
        self._request = None
        self.__api_url: str = 'https://api.open-meteo.com/v1/'

        self.city: str = city
        self.lat: float = self.get_location_info().latitude
        self.lon: float = self.get_location_info().longitude

        self.api_endpoint: str = f'forecast?latitude={self.lat}&longitude={self.lon}&hourly=temperature_2m,rain'

    def __str__(self):
        """ Represents full address of requested location """
        return self.get_location_info().address

    async def fetch_api_data(self) -> None:
        """
        Fetches API request and returns status code for reference.
        Raises exception if request data returns error.
        """
        url = self.__api_url + self.api_endpoint
        r = requests.get(url)

        req_data = r.json()
        if req_data.get('error', None):
            raise RequestException(req_data.get('reason'))
        self._request = r

    def get_location_info(self) -> Location:
        """ Returns location info based on latitude and longitude """
        geolocator = Nominatim(user_agent='weather_fetcher')
        loc_info = geolocator.geocode(self.city)
        return loc_info

    def to_dict(self) -> dict:
        """ Returns parsed json data as dict """
        if self._request:
            data = self._request.json()
            data["city"] = self.city
            return data
        raise NoneRequestException("Cannot parse NoneType element.")


class WeatherProcessor:

    def __init__(self,
                 temp_threshold: float = 21,
                 rainfall_threshold: float = 0.0,
                 weather_data: dict = None,
                 valid_keys: list = None):
        self.temp_threshold: float = temp_threshold
        self.rainfall_threshold: float = rainfall_threshold

        self.weather_data: dict = weather_data if weather_data else {}
        self.processed_data: list = list()
        self.valid_keys: list = valid_keys if valid_keys else ['temperature_2m', 'rain']
        self.units: dict = self.weather_data.get('hourly_units', {"time": "iso8601",
                                                                  "temperature_2m": "C",
                                                                  "rain": "mm"})

    @staticmethod
    def temperature_flag(temp: float, unit: str = 'C') -> str:
        """ return temperature flag as string representation """
        flag: str = ''

        unit = unit.lower()
        if unit == 'f':
            temp = (temp - 32) * (5 / 9)

        if temp < 15.0:
            flag = 'low temperature'
        elif temp < 23:
            flag = 'moderate temperature'
        else:
            flag = 'high temperature'
        return flag

    async def filter_data(self, full: int = 168) -> None:
        """ Filters data that are not matching set thresholds """
        data = self.weather_data.get('hourly')
        for idx in range(full):
            temp = data['temperature_2m'][idx]
            rain = data['rain'][idx]
            time = data['time'][idx]

            if temp < self.temp_threshold and rain > self.rainfall_threshold:
                item = {'temp': temp, 'rain': rain, 'time': time}
                self.processed_data.append(item)

    async def to_stdout(self) -> None:
        if not self.processed_data:
            print(f'No data found for {self.weather_data["city"].title()}')
        else:
            for item in self.processed_data:
                temp = item["temp"]
                print(f'Warning: {self.weather_data["city"].title()}, {self.temperature_flag(temp)} {temp}'
                      f' of {self.units["temperature_2m"]} and rain {item["rain"]} {self.units["rain"]} '
                      f'expected on {item["time"]}')


async def main():
    parser = argparse.ArgumentParser(description='Process API calls')
    parser.add_argument('-t', '--temp', help='Expects temperature value (represented in "C") as float', type=float)
    parser.add_argument('-r', '--rain', help='Expects rainfall value (represented in "mm") as float',
                        default=0.0, type=float)
    parser.add_argument('-c', '--city', help='Expects city name', default='wroclaw', required=False, type=str)
    args = parser.parse_args()

    weather_fetcher = WeatherFetcher(city=args.city)

    await asyncio.wait_for(weather_fetcher.fetch_api_data(), 5)
    weather_processor = WeatherProcessor(weather_data=weather_fetcher.to_dict(),
                                         rainfall_threshold=args.rain, temp_threshold=args.temp)
    await weather_processor.filter_data()
    await weather_processor.to_stdout()


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())

