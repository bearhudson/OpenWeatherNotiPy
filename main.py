#!/usr/bin/python3

import datetime
import time
from rich.live import Live
from rich.table import Table
from rich import box
from WeatherClass.WeatherClass.weatherclass import WeatherClass
import os
import sys
from termcolor import cprint
from pyfiglet import figlet_format
from colorama import init

init(strip=not sys.stdout.isatty())  # strip colors if stdout is redirected

ZIPCODE = os.environ.get('ZIPCODE')

weather_location = WeatherClass(ZIPCODE)
current_weather_slice = weather_location.weather_data['current']
hourly_weather_slice = weather_location.weather_data['hourly']
dt = datetime.datetime.fromtimestamp(current_weather_slice['dt'])
sunset_dt = datetime.datetime.fromtimestamp(current_weather_slice['sunset'])


def draw_main_table() -> Table:
    main_table = Table(title=f"{weather_location.geo_data['name']}",
                       width=150, box=box.MINIMAL_HEAVY_HEAD, padding=0, pad_edge=True)
    today_table = Table(box=None, padding=1, pad_edge=False)
    conditions_table = Table(box=None, padding=1, pad_edge=False)
    hourly_conditions_table = Table(box=None, padding=1, pad_edge=False)
    historic_conditions_table = Table(box=None, padding=1, pad_edge=False)
    for hourly_conditions in current_weather_slice['weather']:
        conditions_table.add_column(f"{hourly_conditions['main']}")
    main_table.add_row(today_table)
    today_table.add_column("Date")
    today_table.add_column("Time")
    today_table.add_column("Sunset")
    today_table.add_column("Temp")
    today_table.add_column("Feels Like")
    today_table.add_column("Pressure")
    today_table.add_column("Humid %")
    today_table.add_column("Dew Pt")
    today_table.add_column("Cloud Cover")
    today_table.add_column("UVI")
    today_table.add_column("Wind S")
    today_table.add_column("Wind D")
    today_table.add_column("Forecast")
    today_table.add_row(f"{datetime.datetime.strftime(dt, '%y/%m/%d')}",
                        f"{datetime.datetime.strftime(dt, '%H:%M')}",
                        f"{datetime.datetime.strftime(sunset_dt, '%H:%M')}",
                        f"{round(current_weather_slice['temp'])} c",
                        f"{round(current_weather_slice['feels_like'])} c",
                        f"{current_weather_slice['pressure']} mb",
                        f"{current_weather_slice['humidity']}",
                        f"{current_weather_slice['dew_point']} c",
                        f"{current_weather_slice['clouds']} %",
                        f"{current_weather_slice['uvi']}",
                        f"{current_weather_slice['wind_speed']} kph",
                        f"{deg_to_direction(current_weather_slice['wind_deg'])}",
                        conditions_table, )
    for index, hourly in zip(range(3), hourly_weather_slice[1:]):
        for hourly_conditions in hourly['weather']:
            hourly_conditions_table.add_column(f"{hourly_conditions['main']}")
        dt_old = datetime.datetime.fromtimestamp(hourly['dt'])
        today_table.add_row(f"",
                            f"{datetime.datetime.strftime(dt_old, '%H:%M')}",
                            f"",
                            f"{round(hourly['temp'])} c",
                            f"{hourly['feels_like']} c",
                            f"{hourly['pressure']} mb",
                            f"{hourly['humidity']}",
                            f"{hourly['dew_point']} c",
                            f"{hourly['clouds']} %",
                            f"{hourly['uvi']}",
                            f"{hourly['wind_speed']} kph",
                            f"{deg_to_direction(hourly['wind_deg'])}", hourly_conditions_table)
    day = 1
    historic_slice = []
    while day < 6:
        weather_location.get_historic_weather(day)
        historic_slice += weather_location.historic_data['hourly'][:1]
        day += 1
    for historic_data in historic_slice:
        dt_old = datetime.datetime.fromtimestamp(historic_data['dt'])
        historic_conditions_table.add_row(f"{datetime.datetime.strftime(dt_old, '%y/%m/%d')}",
                                          f"{datetime.datetime.strftime(dt_old, '%H:%M')}",
                                          f"", f"",
                                          f"{round(historic_data['temp'])} c",
                                          f"{round(historic_data['feels_like'])} c",
                                          f"{historic_data['pressure']} mb",
                                          f"{historic_data['humidity']}",
                                          f"{historic_data['dew_point']} c",
                                          f"{historic_data['clouds']} %",
                                          f"{historic_data['uvi']}",
                                          f"{historic_data['wind_speed']} kph",
                                          f"{deg_to_direction(historic_data['wind_deg'])}", )
    main_table.add_row(historic_conditions_table)
    return main_table


def deg_to_direction(degree):
    position = 0
    directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    if degree > 330 or degree <= 30:
        position = 0
    elif degree > 30 or degree <= 60:
        position = 1
    elif degree > 60 or degree <= 120:
        position = 2
    elif degree > 120 or degree <= 150:
        position = 3
    elif degree > 150 or degree <= 210:
        position = 4
    elif degree > 210 or degree <= 240:
        position = 5
    elif degree > 240 or degree <= 300:
        position = 6
    elif degree > 300 or degree <= 330:
        position = 7
    return directions[position]


def main():
    with Live(draw_main_table(), refresh_per_second=1) as live:
        while True:
            cprint(
                figlet_format(f"{current_weather_slice['temp']} c / "
                              f"{datetime.datetime.strftime(sunset_dt, '%H:%M')} / "
                              f"{current_weather_slice['pressure']} mb", font='small'), 'white', attrs=['bold'])
            weather_location.update_weather()
            live.update(draw_main_table())
            time.sleep(360)


if __name__ == "__main__":
    os.system('clear')
    main()
