API_URL: str = 'https://api.open-meteo.com/v1/'
API_ENDPOINT_PARAMS = [
    'forecast?latitude=51.10&longitude=17.03&hourly=temperature_2m,rain',
    'forecast?latitude=54.39&longitude=18.60&hourly=temperature_2m,rain',
    'forecast?latitude=52.23&longitude=21.01&hourly=temperature_2m,rain',
    'forecast?latitude=52.41&longitude=16.93&hourly=temperature_2m,rain',
]

API_INVALID_ENDPOINTS = [
    '',
    'forecast?latitude=&longitude=17.03&hourly=temperature_2m,rain',
    'forecast?latitude=54.39&longitude=&hourly=temperature_2m,rain',
    'forecast?latitude=&longitude=&hourly=temperature_2m,rain',
    'forecast?latitude&longitude&hourly=temperature_2m,rain',
    'forecast?latitude&longitude&hourly=',
    'forecast?'
]
