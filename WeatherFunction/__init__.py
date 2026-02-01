import logging
import requests
import azure.functions as func

def main(mytimer: func.TimerRequest) -> None:
    city = "Paris"
    api_key = "TA_CLE_API"
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

    response = requests.get(url)
    data = response.json()

    temp = data["main"]["temp"]
    humidity = data["main"]["humidity"]
    weather = data["weather"][0]["description"]

    logging.info(
        f"Météo {city} | Temp: {temp}°C | Humidité: {humidity}% | {weather}"
    )
