import random


def get_pressure_display(hour_weather_slice):
    return_pressure_list = []
    current_pressure = hour_weather_slice[0]['pressure']
    for index, hour in enumerate(hour_weather_slice):
        y = hour['pressure']
        if index == 4 or index == 12 or index == 23:
            return_pressure_list += slope_calculator(0, index, current_pressure, y)
    return return_pressure_list


def slope_calculator(x1, x2, y1, y2):
    return_icon = '➡'
    rx = (y2 - y1) / (x2 - x1)
    pressure_icons = ['↗️', '↘️']
    if rx >= .5:
        return_icon = pressure_icons[0]
    elif rx <= -.5:
        return_icon = pressure_icons[1]
    return return_icon


def get_sun_icons(hour, sunrise, sunset):
    sunrise_icons = ['🌄', '🌅', '🌇']
    sunset_icons = ['🌃', '🌉', '🌌']
    if sunset > hour > sunrise:
        return "am", random.choice(sunset_icons)
    else:
        return "pm", random.choice(sunrise_icons)


def get_weather_emoji(status_code):
    emoji_list = ['❌', '⛈', '☔', '🌧', '🌨️', '🌪', '🌞', '🌤', '⛅', '☁']
    return_code = 0
    if status_code < 299:
        return_code = 1
    elif 300 <= status_code < 399:
        return_code = 2
    elif 500 <= status_code < 599:
        return_code = 3
    elif 600 <= status_code < 699:
        return_code = 4
    elif 700 <= status_code < 781:
        return_code = 5
    elif status_code == 800:
        return_code = 6
    elif status_code == 801:
        return_code = 7
    elif status_code == 802 or status_code == 803:
        return_code = 8
    elif status_code == 804:
        return_code = 9
    return emoji_list[return_code]


def get_time_emoji(hour):
    hour_icons = ['🕛', '🕐', '🕑', '🕒', '🕓', '🕔' '🕕', '🕖', '🕗', '🕘', '🕙', '🕚']
    icon = 0
    if hour == 1:
        icon = 1
    elif hour == 2:
        icon = 2
    elif hour == 3:
        icon = 3
    elif hour == 4:
        icon = 4
    elif hour == 5:
        icon = 5
    elif hour == 6:
        icon = 6
    elif hour == 7:
        icon = 7
    elif hour == 8:
        icon = 8
    elif hour == 9:
        icon = 9
    elif hour == 10:
        icon = 10
    elif hour == 11:
        icon = 11
    elif hour == 12:
        icon = 0
    elif hour == 13:
        icon = 1
    elif hour == 14:
        icon = 2
    elif hour == 15:
        icon = 3
    elif hour == 16:
        icon = 4
    elif hour == 17:
        icon = 5
    elif hour == 18:
        icon = 6
    elif hour == 19:
        icon = 7
    elif hour == 20:
        icon = 8
    elif hour == 21:
        icon = 9
    elif hour == 22:
        icon = 10
    elif hour == 23:
        icon = 11
    return hour_icons[icon]
