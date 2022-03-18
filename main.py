from WeatherClass.WeatherClass.weatherclass import WeatherClass
import rich


weather_location = WeatherClass('02188')

print(weather_location.lat, weather_location.lon)
for conditions in weather_location.weather_data['current']['weather']:
    print(conditions['main'])
