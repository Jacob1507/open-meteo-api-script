import os
import json
import pytest
import requests
from script.main import WeatherFetcher
from script.main import WeatherProcessor

from utils.utils import status
from .test_data.urls import API_URL, API_ENDPOINT_PARAMS, API_INVALID_ENDPOINTS

from requests.exceptions import RequestException

WORKING_DIR = os.getcwd()
TEST_DATA_DIR = WORKING_DIR + '\\tests\\test_data\\'

TEST_WEATHER_FULL_INFO_FILE_PATH = TEST_DATA_DIR + 'weather_info.json'
TEST_WEATHER_SAMPLE_INFO_FILE_PATH = TEST_DATA_DIR + 'weather_info_sample.json'

searched_keys = ['latitude', 'longitude', 'hourly_units', 'hourly']
searched_units = ['temperature_2m', 'rain']
hourly_keys = ['rain', 'temperature_2m', 'time']


class TestWeatherApi:

    def test_api_get_response(self):
        url = API_URL + API_ENDPOINT_PARAMS[0]
        request = requests.get(url)
        assert request.status_code == status.HTTP_200_OK

        # Check required dict keys
        data = list(request.json().get('hourly'))
        assert data[0] == 'time'
        assert data[1] == 'temperature_2m'
        assert data[2] == 'rain'


class TestWeatherFetcher:

    @pytest.mark.asyncio
    async def test_basic_logic_flow(self):
        weather_fetcher = WeatherFetcher('Warsaw')

        weather_fetcher.api_endpoint = API_ENDPOINT_PARAMS[1]

        await weather_fetcher.fetch_api_data()
        assert weather_fetcher._request.status_code == status.HTTP_200_OK

        data = weather_fetcher.to_dict()

        # Check if base fields are supplied
        assert all(key in list(data) for key in searched_keys)

        # Check if units are correct
        assert all(unit in list(data.get('hourly_units')) for unit in searched_units)

    def test_empty_get_request_throws_error(self):
        weather_fetcher = WeatherFetcher('Warsaw')

        with pytest.raises(TypeError):
            weather_fetcher.to_dict()

    @pytest.mark.asyncio
    async def test_invalid_requests(self):
        weather_fetcher = WeatherFetcher('Warsaw')

        for endpoint in API_INVALID_ENDPOINTS:
            weather_fetcher.api_endpoint = endpoint
            with pytest.raises(RequestException):
                await weather_fetcher.fetch_api_data()


class TestWeatherProcessor:

    @pytest.mark.asyncio
    async def test_data_structures(self):
        weather_processor = WeatherProcessor(temp_threshold=15.0,
                                             rainfall_threshold=0.5,)

        with open(TEST_WEATHER_FULL_INFO_FILE_PATH, 'r') as f:
            weather_processor.weather_data = json.load(f)

        assert type(weather_processor.weather_data) == dict

        weather_processor.temp_threshold = 10.0
        weather_processor.rainfall_threshold = 0.5

        await weather_processor.filter_data()
        assert type(weather_processor.processed_data) == list
        assert weather_processor.processed_data != []

        data_hourly: dict = weather_processor.weather_data.get('hourly')
        assert data_hourly != {}

        assert all(data in hourly_keys for data in data_hourly)
        for values_list in data_hourly.values():
            assert len(values_list) == 168

    def test_temp_flags(self):
        flag_low_c = WeatherProcessor.temperature_flag(temp=-1.0)
        flag_mod_c = WeatherProcessor.temperature_flag(temp=22.99)
        flag_high_c = WeatherProcessor.temperature_flag(temp=23.01)

        assert flag_low_c == 'low temperature'
        assert flag_mod_c == 'moderate temperature'
        assert flag_high_c == 'high temperature'

        flag_low_f = WeatherProcessor.temperature_flag(temp=58.982, unit='F')
        flag_mod_f = WeatherProcessor.temperature_flag(temp=73.382, unit='F')
        flag_high_f = WeatherProcessor.temperature_flag(temp=90, unit='F')

        assert flag_low_f == 'low temperature'
        assert flag_mod_f == 'moderate temperature'
        assert flag_high_f == 'high temperature'

    @pytest.mark.asyncio
    async def test_data_filtering(self):
        expected_output = [
            {'temp': 5.9, 'rain': 0.4, 'time': '2023-04-22T00:00'},
            {'temp': 5.0, 'rain': 0.6, 'time': '2023-04-22T01:00'},
            {'temp': 4.1, 'rain': 2.4, 'time': '2023-04-22T02:00'},
            {'temp': 4.0, 'rain': 2.4, 'time': '2023-04-22T03:00'},
            {'temp': 5.4, 'rain': 1.3, 'time': '2023-04-22T04:00'},
        ]

        weather_processor = WeatherProcessor(temp_threshold=6.0,
                                             rainfall_threshold=0.2,)

        with open(TEST_WEATHER_SAMPLE_INFO_FILE_PATH, 'r') as f:
            weather_processor.weather_data = json.load(f)

        await weather_processor.filter_data(full=9)
        data = weather_processor.processed_data

        for idx in range(len(expected_output)):
            assert expected_output[idx]['temp'] == data[idx]['temp']
            assert expected_output[idx]['rain'] == data[idx]['rain']
            assert expected_output[idx]['time'] == data[idx]['time']
