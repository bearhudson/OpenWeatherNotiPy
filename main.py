import datetime
import time
from rich.live import Live
from rich.table import Table
from WeatherClass.WeatherClass.weatherclass import WeatherClass


weather_location = WeatherClass('02188')
current_weather_slice = weather_location.weather_data['current']


def status_table() -> Table:
    table = Table()
    table.add_column("Location", width=20)
    table.add_column("Date", width=15)
    table.add_column("Time", width=15)
    table.add_column("Temp (K)", width=15)
    table.add_column("Humidity (%)", width=15)
    table.add_column("Clouds (%)", width=15)
    now = datetime.datetime.now()
    table.add_row(f"{datetime.datetime.strftime(now, '%y/%m/%d')}",
                  f"{datetime.datetime.strftime(now, '%H:%M:%S')}",
                  f"{weather_location.lat}, {weather_location.lon}",
                  f"{current_weather_slice['temp']}",
                  f"{current_weather_slice['humidity']}",
                  f"{current_weather_slice['clouds']}")
    return table


def conditions_table() -> Table:
    pass


with Live(status_table(), refresh_per_second=1) as live:
    for _ in range(100):
        time.sleep(60)
        weather_location.update_weather()
        live.update(status_table())
