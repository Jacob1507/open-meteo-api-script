## How to install 
* `git clone https://github.com/Jacob1507/open-meteo-api-script`
* `cd open-meteo-api-script`
* `pip install -r requirements.txt`
## How to use
Main command body:

`python script/main.py -t <float> -r <float> -c <string>`
* `-t` takes temperature value as parameter,
* `-r` takes rain value as parameter,
* `-c` takes city name as parameter (city is optional so parameter might be skipped).

By executing `python script/main.py --help` script will return help text for defined parameters.

## Examples
### Ex. 1
`python script/main.py -t 15.2 -r 0.2`

```
Warning: Wroclaw, low temperature 14.2 of °C and rain 0.4 mm expected on 2023-04-24T14:00
Warning: Wroclaw, low temperature 14.2 of °C and rain 1.2 mm expected on 2023-04-24T15:00
Warning: Wroclaw, low temperature 13.1 of °C and rain 0.4 mm expected on 2023-04-24T17:00
Warning: Wroclaw, low temperature 12.4 of °C and rain 0.3 mm expected on 2023-04-24T18:00
<rest of wargnings>
```

### Ex. 2
`python script/main.py -t 12 -r 0.2 -c gdansk`

```
Warning: Gdansk, low temperature 9.4 of °C and rain 0.4 mm expected on 2023-04-25T05:00
Warning: Gdansk, low temperature 9.3 of °C and rain 0.3 mm expected on 2023-04-25T13:00
Warning: Gdansk, low temperature 9.2 of °C and rain 0.9 mm expected on 2023-04-25T15:00
Warning: Gdansk, low temperature 8.9 of °C and rain 0.3 mm expected on 2023-04-25T16:00
```

### Ex. 3
`python script/main.py -t 12 -r 0.2 -c uganda`

```
No data found for Uganda
```
