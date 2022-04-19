#!/usr/bin/python3

import datetime
import time
import os

from rich.live import Live
from rich.table import Table
from rich import box
from rich.text import Text
from newsapi import NewsApiClient
import asyncio
from pyiqvia import Client as IqviaClient
import openweatherclass as owc
from openweatherclass.functions import deg_to_direction
from openweatherclass.functions import moon_phase_to_string
from functions import *

API_KEY = os.environ.get("OPENWEATHER_API_KEY")
NEWS_API = os.environ.get("NEWSAPI_KEY")
ZIPCODE = os.environ.get('ZIPCODE')
UNITS = os.environ.get('UNITS')
DISPLAY_WIDTH = os.get_terminal_size().columns
SLEEP = 360

if UNITS == 'imperial':
    owc_data = owc.OpenWeatherClass(zipcode=ZIPCODE, api_key=API_KEY, units=UNITS)
    temp_symbol = '℉'
    speed_symbol = 'mph'
else:
    owc_data = owc.OpenWeatherClass(zipcode=ZIPCODE, api_key=API_KEY, units=UNITS)
    temp_symbol = '℃'
    speed_symbol = 'kph'


def draw_main_table() -> Table:
    current_weather_slice = owc_data.weather_data['current']
    hourly_weather_slice = owc_data.weather_data['hourly']
    daily_weather_slice = owc_data.weather_data['daily']

    historic_slice = []
    while len(historic_slice) <= 1:
        owc_data.get_historic_weather(len(historic_slice))
        historic_slice += owc_data.historic_data['hourly'][:1]

    pressure_display = []
    owc_data.get_historic_weather(1)
    for index, record in enumerate(owc_data.historic_data['hourly']):
        if index == 1 or index == 5 or index == 12:
            pressure_display += get_pressure_display(current_weather_slice['pressure'], record['pressure'], index)

    news = NewsApiClient(api_key=NEWS_API)
    top_headlines = news.get_top_headlines(sources='bbc-news')
    articles = top_headlines['articles']

    del daily_weather_slice[0]

    dt = datetime.datetime.fromtimestamp(current_weather_slice['dt'])
    sunset_dt = datetime.datetime.fromtimestamp(current_weather_slice['sunset'])
    sunrise_dt = datetime.datetime.fromtimestamp(current_weather_slice['sunrise'])
    sun_icon = get_sun_icons(dt, sunrise_dt, sunset_dt)

    header_style = "bold yellow1"
    main_table_style = "dark_orange"
    box_style = box.MINIMAL_HEAVY_HEAD

    main_table = Table(width=DISPLAY_WIDTH, box=None, padding=0, pad_edge=False, style=f"{main_table_style}")
    header_table = Table(width=DISPLAY_WIDTH, box=None, padding=0, pad_edge=False, show_footer=True,
                         show_header=True, style=f"{header_style}")
    today_table = Table(box=box_style,
                        padding=0, pad_edge=False, width=DISPLAY_WIDTH, row_styles=["grey62", "grey93"])
    conditions_table = Table(box=None, padding=1, pad_edge=False)
    hourly_conditions_table = Table(box=None, padding=1, pad_edge=False)
    future_conditions_table = Table(box=box_style,
                                    padding=0, pad_edge=False, width=DISPLAY_WIDTH, row_styles=["grey62", "grey93"])
    historic_conditions_table = Table(box=box_style,
                                      padding=0, pad_edge=False, width=DISPLAY_WIDTH, row_styles=["grey62", "grey93"])
    news_and_alerts_table = Table(box=box.SQUARE_DOUBLE_HEAD, show_header=False, padding=0, pad_edge=False,
                                  width=DISPLAY_WIDTH, row_styles=["grey62", "grey93"])
    header_ozone = asyncio.run(get_ozone(ZIPCODE))
    header_temp = Text(f"{get_time_emoji(int(datetime.datetime.strftime(datetime.datetime.now(), '%H')))} "
                       f"{datetime.datetime.strftime(datetime.datetime.now(), '%H:%M')} // "
                       f"📅 {datetime.datetime.strftime(datetime.datetime.now(), '%b, %d')} // "
                       f"🌡️ {current_weather_slice['temp']} {temp_symbol} // "
                       f"🏭 {header_ozone[0].title()}: {header_ozone[1]} ppm")
    header_temp.stylize(f"{header_style}")
    header_table.add_column(header_temp)
    header_location = Text(f"Currently in {owc_data.geo_data['name']} ->")
    header_location.stylize(f"{header_style}")
    header_table.add_column(header_location)
    header_desc = Text(f"{get_weather_emoji(int(current_weather_slice['weather'][0]['id']))}  "
                       f"{current_weather_slice['weather'][0]['description']}")
    header_desc.stylize(f"{header_style}")
    header_table.add_column(header_desc)
    header_pressure = Text(f"🌈 {current_weather_slice['pressure']} mb {''.join(pressure_display)}")
    header_pressure.stylize(f"{header_style}")
    header_table.add_column(header_pressure)
    if sun_icon[0] == "am":
        header_sunset = Text(f"{sun_icon[1]} Sunset: {datetime.datetime.strftime(sunset_dt, '%H:%M')}")
        header_sunset.stylize(f"{header_style}")
        header_table.add_column(header_sunset)
    elif sun_icon[0] == "pm":
        header_sunrise = Text(f"{sun_icon[1]} Sunrise: {datetime.datetime.strftime(sunrise_dt, '%H:%M')}")
        header_sunrise.stylize(f"{header_style}")
        header_table.add_column(header_sunrise)
    header_moon = Text(f"🌜 {moon_phase_to_string(daily_weather_slice[0]['moon_phase'])}")
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
                        f"{deg_to_direction(current_weather_slice['wind_deg'])}", conditions_table)
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
    future_conditions_table.add_column("SunR", justify="right")
    future_conditions_table.add_column("SunS", justify="right")
    future_conditions_table.add_column("Moon", justify="right")
    future_conditions_table.add_column("Forecast")

    for forecast_data in daily_weather_slice[:7]:
        dt_forecast = datetime.datetime.fromtimestamp(forecast_data['dt'])
        dt_sunrise = datetime.datetime.fromtimestamp(forecast_data['sunrise'])
        dt_sunset = datetime.datetime.fromtimestamp(forecast_data['sunset'])
        future_conditions_table.add_row(f"{datetime.datetime.strftime(dt_forecast, '%A')}",
                                        f"{forecast_data['temp']['max']} {temp_symbol}",
                                        f"{forecast_data['temp']['min']} {temp_symbol}",
                                        f"{forecast_data['feels_like']['day']} {temp_symbol}",
                                        f"{forecast_data['pressure']} mb",
                                        f"{forecast_data['humidity']}",
                                        f"{forecast_data['dew_point']} {temp_symbol}",
                                        f"{forecast_data['uvi']}",
                                        f"{forecast_data['wind_speed']} {speed_symbol}",
                                        f"{deg_to_direction(forecast_data['wind_deg'])}",
                                        f"{datetime.datetime.strftime(dt_sunrise, '%H:%M')}",
                                        f"{datetime.datetime.strftime(dt_sunset, '%H:%M')}",
                                        f"{moon_phase_to_string(forecast_data['moon_phase'])}",
                                        f"{owc_data.check_condition(forecast_data['weather'][0]['id']).title()}")

    for index, hourly_data in zip(range(8), hourly_weather_slice[1:]):
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
                            f"{deg_to_direction(hourly_data['wind_deg'])}",
                            f"{owc_data.check_condition(hourly_data['weather'][0]['id']).title()}")
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
                                          f"{deg_to_direction(historic_data['wind_deg'])}",
                                          f"{owc_data.check_condition(historic_data['weather'][0]['id']).title()}")

    news_and_alerts_table.add_row(f"🌻 Air Quality ->", style=f"{main_table_style}")
    news_and_alerts_table.add_row(f"{asyncio.run(get_pollen(PZIPCODE=ZIPCODE))}")
    news_and_alerts_table.add_row(f"🚨 Alerts ->", style=f"{main_table_style}")
    if 'alerts' in owc_data.weather_data:
        alerts_slice = owc_data.weather_data['alerts']
        for alert in alerts_slice:
            alert_sender = alert['sender_name']
            news_and_alerts_table.add_row(f"{alert_sender}: {alert['description']}".replace('\n', ''), style='white')
    else:
        news_and_alerts_table.add_row(f"No alerts at this time.")
    news_and_alerts_table.add_row(f"📰 Headlines ->", style=f"{main_table_style}")
    for article in random.sample(articles, 4):
        news_and_alerts_table.add_row(f"{article['description'][:DISPLAY_WIDTH - 5]}")

    main_table.add_row(header_table)
    main_table.add_row(today_table)
    main_table.add_row(future_conditions_table)
    main_table.add_row(historic_conditions_table)
    main_table.add_row(news_and_alerts_table)
    return main_table


def main() -> None:
    with Live(draw_main_table(), refresh_per_second=1) as live:
        while True:
            time.sleep(1)
            owc_data.update_weather()
            owc_data.get_today_history()
            live.update(draw_main_table())
            time.sleep(SLEEP)


async def get_pollen(PZIPCODE) -> str:
    allergens_outlook = await IqviaClient(PZIPCODE).allergens.outlook()
    return allergens_outlook["Trend"].title() + ": " + allergens_outlook["Outlook"]


async def get_ozone(PZIPCODE) -> tuple:
    asthma_current = await IqviaClient(PZIPCODE).asthma.current()
    asthma_current_slice = asthma_current["Location"]["periods"]
    for entries in asthma_current_slice[:1]:
        try:
            return entries['Triggers'][0]['Name'], entries['Triggers'][0]['PPM']
        except IndexError:
            pass


if __name__ == "__main__":
    os.system('clear')
    main()
