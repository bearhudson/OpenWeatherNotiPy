import datetime
import time
from rich.live import Live
from rich.table import Table
from rich import box
from WeatherClass.WeatherClass.weatherclass import WeatherClass
import os

ZIPCODE = os.environ.get('ZIPCODE')

weather_location = WeatherClass(ZIPCODE)
current_weather_slice = weather_location.weather_data['current']


def draw_main_table() -> Table:
    now = datetime.datetime.now()
    sub_table = Table()
    for conditions in current_weather_slice['weather']:
        sub_table.add_column(f"{conditions['id']}")
        sub_table.add_row(conditions['main'])

    main_table = Table(title=f"Weather for {ZIPCODE}",
                       width=100, box=box.MINIMAL_DOUBLE_HEAD)
    main_table.add_column("Location")
    main_table.add_column("Date")
    main_table.add_column("Time")
    main_table.add_column("Temp")
    main_table.add_column("Humid %")
    main_table.add_column("Clouds")
    main_table.add_column("Currently")
    main_table.add_row(f"{weather_location.lat}, {weather_location.lon}",
                       f"{datetime.datetime.strftime(now, '%y/%m/%d')}",
                       f"{datetime.datetime.strftime(now, '%H:%M:%S')}",
                       f"{current_weather_slice['temp']}",
                       f"{current_weather_slice['humidity']}",
                       f"{current_weather_slice['clouds']}", sub_table)
    return main_table


with Live(draw_main_table(), refresh_per_second=4) as live:
    while True:
        time.sleep(60)
        weather_location.update_weather()
        live.update(draw_main_table())
