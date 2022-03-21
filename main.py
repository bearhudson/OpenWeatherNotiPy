#!/usr/bin/python3

import datetime
import time
import os
import random
from rich.live import Live
from rich.table import Table
from rich import box
from rich.text import Text
from WeatherClass.WeatherClass.weatherclass import WeatherClass
from newsapi import NewsApiClient

ZIPCODE = os.environ.get('ZIPCODE')
UNITS = os.environ.get('UNITS')
NEWS_API = os.environ.get("NEWSAPI_KEY")
SLEEP = 60

if UNITS == 'imperial':
    weather_location = WeatherClass(ZIPCODE, 'imperial')
    temp_symbol = '℉'
    speed_symbol = 'mph'
else:
    weather_location = WeatherClass(ZIPCODE, 'imperial')
    temp_symbol = '℃'
    speed_symbol = 'kph'


def draw_main_table() -> Table:
    current_weather_slice = weather_location.weather_data['current']
    hourly_weather_slice = weather_location.weather_data['hourly']
    daily_weather_slice = weather_location.weather_data['daily']
    news = NewsApiClient(api_key=NEWS_API)
    top_headlines = news.get_top_headlines(sources='bbc-news')

    del daily_weather_slice[0]

    dt = datetime.datetime.fromtimestamp(current_weather_slice['dt'])
    sunset_dt = datetime.datetime.fromtimestamp(current_weather_slice['sunset'])

    header_style = "bold yellow1"
    main_table_style = "dark_orange"

    main_table = Table(width=140, box=None, padding=0, pad_edge=False, style=f"{main_table_style}")
    header_table = Table(width=140, box=None, padding=0, pad_edge=False, show_footer=True,
                         show_header=True, style=f"{header_style}")
    today_table = Table(box=box.MINIMAL_HEAVY_HEAD,
                        padding=0, pad_edge=False, width=140, row_styles=["grey50", "white"])
    conditions_table = Table(box=None, padding=1, pad_edge=False, style='italic white')
    hourly_conditions_table = Table(box=None, padding=1, pad_edge=False, style='italic white')
    future_conditions_table = Table(box=box.MINIMAL_HEAVY_HEAD,
                                    padding=0, pad_edge=False, width=140, row_styles=["grey50", "white"])
    historic_conditions_table = Table(box=box.MINIMAL_HEAVY_HEAD,
                                      padding=0, pad_edge=False, width=140, row_styles=["grey50", "white"])
    top_headlines_table = Table(box=None,
                                padding=0, pad_edge=False, width=140, row_styles=["grey50", "white"])

    header_temp = Text(f"🕐 {datetime.datetime.strftime(datetime.datetime.now(), '%H:%M')} // "
                       f"🌡️ {current_weather_slice['temp']} {temp_symbol}")
    header_temp.stylize(f"{header_style}")
    header_table.add_column(header_temp)
    header_location = Text(f"Currently in {weather_location.geo_data['name']} ->")
    header_location.stylize(f"{header_style}")
    header_table.add_column(header_location)
    header_desc = Text(f"🌄 {daily_weather_slice[0]['weather'][0]['description']}")
    header_desc.stylize(f"{header_style}")
    header_table.add_column(header_desc)
    header_pressure = Text(f"🌈 {current_weather_slice['pressure']} mb")
    header_pressure.stylize(f"{header_style}")
    header_table.add_column(header_pressure)
    header_sunset = Text(f"🌇 {datetime.datetime.strftime(sunset_dt, '%H:%M')}")
    header_sunset.stylize(f"{header_style}")
    header_table.add_column(header_sunset)
    header_moon = Text(f"🌜 {weather_location.moon_phase_to_string(daily_weather_slice[0]['moon_phase'])}")
    header_moon.stylize(f"{header_style}")
    header_table.add_column(header_moon)

    for hourly_conditions in current_weather_slice['weather']:
        conditions_table.add_column(f"{hourly_conditions['main']}")

    today_table.add_column("Date", justify="right")
    today_table.add_column("Time", justify="right")
    today_table.add_column("Temp", justify="left")
    today_table.add_column("Feels Like", justify="left")
    today_table.add_column("Pressure", justify="right")
    today_table.add_column("Humid %", justify="right")
    today_table.add_column("Dew Pt", justify="left")
    today_table.add_column("Cloud Cover", justify="right")
    today_table.add_column("UVI", justify="right")
    today_table.add_column("Wind S", justify="right")
    today_table.add_column("Wind D", justify="right")
    today_table.add_column("Forecast")
    today_table.add_row(f"{datetime.datetime.strftime(dt, '%y/%m/%d')}",
                        f"{datetime.datetime.strftime(dt, '%H:%M')}",
                        f"{current_weather_slice['temp']} {temp_symbol} ",
                        f"{current_weather_slice['feels_like']} {temp_symbol} ",
                        f"{current_weather_slice['pressure']} mb",
                        f"{current_weather_slice['humidity']}",
                        f"{current_weather_slice['dew_point']} {temp_symbol} ",
                        f"{current_weather_slice['clouds']} %",
                        f"{current_weather_slice['uvi']}",
                        f"{current_weather_slice['wind_speed']} {speed_symbol}",
                        f"{weather_location.deg_to_direction(current_weather_slice['wind_deg'])}",
                        conditions_table)
    future_conditions_table.add_column("Date", justify="right")
    future_conditions_table.add_column("High", justify="left")
    future_conditions_table.add_column("Low", justify="left")
    future_conditions_table.add_column("Feels Like", justify="left")
    future_conditions_table.add_column("Pressure", justify="right")
    future_conditions_table.add_column("Humid %", justify="right")
    future_conditions_table.add_column("Dew Pt", justify="left")
    future_conditions_table.add_column("UVI", justify="right")
    future_conditions_table.add_column("Wind S", justify="right")
    future_conditions_table.add_column("Wind D", justify="right")
    future_conditions_table.add_column("Sunrise", justify="right")
    future_conditions_table.add_column("Moon", justify="right")
    future_conditions_table.add_column("Forecast")

    for forecast_data in daily_weather_slice[:7]:
        dt_forecast = datetime.datetime.fromtimestamp(forecast_data['dt'])
        dt_sunrise = datetime.datetime.fromtimestamp(forecast_data['sunrise'])
        future_conditions_table.add_row(f"{datetime.datetime.strftime(dt_forecast, '%y/%m/%d')}",
                                        f"{forecast_data['temp']['max']} {temp_symbol}",
                                        f"{forecast_data['temp']['min']} {temp_symbol}",
                                        f"{forecast_data['feels_like']['day']} {temp_symbol}",
                                        f"{forecast_data['pressure']} mb",
                                        f"{forecast_data['humidity']}",
                                        f"{forecast_data['dew_point']} {temp_symbol}",
                                        f"{forecast_data['uvi']}",
                                        f"{forecast_data['wind_speed']} {speed_symbol}",
                                        f"{weather_location.deg_to_direction(forecast_data['wind_deg'])}",
                                        f"{datetime.datetime.strftime(dt_sunrise, '%H:%M')}",
                                        f"{weather_location.moon_phase_to_string(forecast_data['moon_phase'])}",
                                        f"{weather_location.check_condition(forecast_data['weather'][0]['id'])}")

    for index, hourly_data in zip(range(3), hourly_weather_slice[1:]):
        for hourly_conditions in hourly_data['weather']:
            hourly_conditions_table.add_column(f"{hourly_conditions['main']}")
        dt_old = datetime.datetime.fromtimestamp(hourly_data['dt'])
        today_table.add_row(f"",
                            f"{datetime.datetime.strftime(dt_old, '%H:%M')}",
                            f"{hourly_data['temp']} {temp_symbol} ",
                            f"{hourly_data['feels_like']} {temp_symbol} ",
                            f"{hourly_data['pressure']} mb",
                            f"{hourly_data['humidity']}",
                            f"{hourly_data['dew_point']} {temp_symbol} ",
                            f"{hourly_data['clouds']} %",
                            f"{hourly_data['uvi']}",
                            f"{hourly_data['wind_speed']} {speed_symbol}",
                            f"{weather_location.deg_to_direction(hourly_data['wind_deg'])}",
                            hourly_conditions_table)
    historic_conditions_table.add_column("Date", justify="right")
    historic_conditions_table.add_column("Temp", justify="left")
    historic_conditions_table.add_column("Feels Like", justify="left")
    historic_conditions_table.add_column("Pressure", justify="right")
    historic_conditions_table.add_column("Humid %", justify="right")
    historic_conditions_table.add_column("Dew Pt", justify="left")
    historic_conditions_table.add_column("Cloud Cover", justify="right")
    historic_conditions_table.add_column("UVI", justify="right")
    historic_conditions_table.add_column("Wind S", justify="right")
    historic_conditions_table.add_column("Wind D", justify="right")
    historic_conditions_table.add_column("Forecast")

    historic_slice = []

    while len(historic_slice) <= 1:
        weather_location.get_historic_weather(len(historic_slice))
        historic_slice += weather_location.historic_data['hourly'][:1]

    for historic_data in historic_slice:
        dt_old = datetime.datetime.fromtimestamp(historic_data['dt'])
        historic_conditions_table.add_row(f"{datetime.datetime.strftime(dt_old, '%y/%m/%d')}",
                                          f"{historic_data['temp']} {temp_symbol} ",
                                          f"{historic_data['feels_like']} {temp_symbol} ",
                                          f"{historic_data['pressure']} mb",
                                          f"{historic_data['humidity']}",
                                          f"{historic_data['dew_point']} {temp_symbol} ",
                                          f"{historic_data['clouds']} %",
                                          f"{historic_data['uvi']}",
                                          f"{historic_data['wind_speed']} {speed_symbol}",
                                          f"{weather_location.deg_to_direction(historic_data['wind_deg'])}",
                                          f"{weather_location.check_condition(historic_data['weather'][0]['id'])}")
    articles = top_headlines['articles']
    top_headlines_table.add_row(f"\tHeadlines ->", style="dark_orange")
    for article in random.sample(articles, 4):
        top_headlines_table.add_row(f"\t{article['description']}")

    main_table.add_row(header_table)
    main_table.add_row(today_table)
    main_table.add_row(future_conditions_table)
    main_table.add_row(historic_conditions_table)
    main_table.add_row(top_headlines_table)

    return main_table


def main():
    with Live(draw_main_table(), refresh_per_second=4) as live:
        while True:
            live.update(draw_main_table())
            weather_location.update_weather()
            time.sleep(SLEEP)


if __name__ == "__main__":
    os.system('clear')
    main()
