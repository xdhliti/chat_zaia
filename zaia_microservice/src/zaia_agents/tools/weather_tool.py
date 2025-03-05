import requests
from langchain.tools import tool
import os
import json
from dotenv import load_dotenv
from datetime import datetime, timedelta
from langchain_community.utilities import OpenWeatherMapAPIWrapper

load_dotenv()


class WeatherTool():

    @tool("Get Weather Details")
    def get_weather_report(city):
        """
        Get a detailed weather report of the city. The temperature must be in Celsius or Farenheit. 
        For example 20°C or 20°F.
        """

        api_key = os.environ['WEATHER_API_KEY']
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url)

        current_weather_data = response.json()
        current_weather = {
            "description": current_weather_data["weather"][0]["description"],
            "temperature": current_weather_data["main"]["temp"],
            "humidity": current_weather_data["main"]["humidity"],
            "wind_speed": current_weather_data["wind"]["speed"]
        }


        return current_weather