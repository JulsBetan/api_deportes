from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models import EventModel
from app.schemas import Event
import httpx
from pydantic import BaseModel
from typing import List
import openai

import re

from app.config import get_settings

settings = get_settings()

OPENAI_KEY = settings.openai_key
WEATHER_KEY = settings.weather_key
SPORTS_KEY = settings.sports_key

openai.api_key = OPENAI_KEY

# class Event(BaseModel):
#     idEvent: str
#     strEvent: str
#     strHomeTeam: str
#     strAwayTeam: str
#     idHomeTeam: str
#     idAwayTeam: str
#     dateEvent: str
#     strTime: str
#     strHomeTeamBadge: str
#     strAwayTeamBadge: str
#     idLeague: str
#     idVenue: str
#     strVenue: str
#     clima: dict
#     pronostico: str = ""

router = APIRouter()


def convert_to_decimal(dms_str: str) -> tuple:
    """
    Convierte coordenadas en formato DMS o decimal a coordenadas decimales.
    Ejemplo de entrada:
    - '42°50′14″N 2°41′17″W' (DMS)
    - '42°50′14″N 2°41′17″O' (DMS con "O" para oeste)
    - '42.2118°N 8.7397°W' (decimal con dirección)
    """
    try:
        # Patrón para DMS
        dms_pattern = r"(\d+)°(\d+)′(\d+)″([NSEWO])"
        # Patrón para grados decimales con dirección (ej. '42.2118°N')
        decimal_pattern = r"([\d\.]+)°([NSEWO])"

        dms_matches = re.findall(dms_pattern, dms_str)
        decimal_matches = re.findall(decimal_pattern, dms_str)

        # Conversión para formato DMS
        if len(dms_matches) == 2:
            def dms_to_decimal(degrees, minutes, seconds, direction):
                decimal = int(degrees) + int(minutes) / 60 + int(seconds) / 3600
                if direction in ['S', 'W', 'O']:  # Considera 'O' como oeste
                    decimal = -decimal
                return decimal

            lat = dms_to_decimal(*dms_matches[0])
            lon = dms_to_decimal(*dms_matches[1])
            return lat, lon

        # Conversión para formato decimal con dirección
        elif len(decimal_matches) == 2:
            def decimal_with_direction(value, direction):
                decimal = float(value)
                if direction in ['S', 'W', 'O']:  # Considera 'O' como oeste
                    decimal = -decimal
                return decimal

            lat = decimal_with_direction(*decimal_matches[0])
            lon = decimal_with_direction(*decimal_matches[1])
            return lat, lon

        # Si no se encontró un formato válido
        return None

    except Exception as e:
        print(f"Error al convertir coordenadas: {e}")
        return None

# Función para obtener el clima
async def get_weather(city: str, date: str) -> dict:
    api_key = WEATHER_KEY
    url = f"http://api_clima:3000/clima?city={city}"
    # url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            weather_data = response.json()
            # Verificar si la estructura esperada está presente
            if "main" in weather_data and "wind" in weather_data and "weather" in weather_data:
                return {
                    "temperature": weather_data["main"]["temp"],
                    "wind_speed": weather_data["wind"]["speed"],
                    "description": weather_data["weather"][0]["description"],
                }
            else:
                # Estructura diferente (manejo del caso 'desconocido')
                return {
                    "temperature": "Desconocida",
                    "wind_speed": "Desconocido",
                    "description": "No disponible",
                }
        except httpx.RequestError as e:
            # Registrar el error en los logs del servidor
            print(f"Error al obtener el clima para la ciudad {city}: {e}")
            return {"temperature": "Desconocida", "wind_speed": "Desconocido", "description": "No disponible"}

async def get_weather_by_coordinates(coordinates: str, date: str) -> dict:
   
    latitude, longitude = convert_to_decimal(coordinates)

    api_key = WEATHER_KEY
    # url = f"http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={api_key}&units=metric"
    url = f"http://api_clima:3000/clima?lat={latitude}&lon={longitude}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            weather_data = response.json()
            # Verificar si la estructura esperada está presente
            if "main" in weather_data and "wind" in weather_data and "weather" in weather_data:
                return {
                    "temperature": weather_data["main"]["temp"],
                    "wind_speed": weather_data["wind"]["speed"],
                    "description": weather_data["weather"][0]["description"],
                }
            else:
                # Estructura diferente (manejo del caso 'desconocido')
                return {
                    "temperature": "Desconocida",
                    "wind_speed": "Desconocido",
                    "description": "No disponible",
                }
        except httpx.RequestError as e:
            # Registrar el error en los logs del servidor
            print(f"Error al obtener el clima para la ciudad {coordinates}: {e}")
            return {"temperature": "Desconocida", "wind_speed": "Desconocido", "description": "No disponible"}


# Función para obtener `strMap` del evento
async def get_city_for_event(id_venue: str, country: str) -> str:
    sports_key = SPORTS_KEY
    api_url = f"https://www.thesportsdb.com/api/v1/json/{sports_key}/lookupvenue.php?id={id_venue}"
    async with httpx.AsyncClient() as client:
        try:
            print("Consultando evento:", id_venue)
            response = await client.get(api_url)
            response.raise_for_status()
            event_data = response.json()

            # Imprime la estructura completa de la respuesta
            print(f"Respuesta del evento {id_venue}:", event_data)

            if "venues" in event_data and event_data["venues"]:
                city = event_data["venues"][0].get("strMap", None)
                print(f"Ciudad obtenida para el evento {id_venue}: {city}")
                return city if city else country  # Si no hay ciudad, usa home_team
            return country  
        except httpx.RequestError as e:
            print(f"Error al consultar el evento {id_venue}: {e}")
            return country 

# Función para obtener `strLocation` del evento
async def get_location_for_event(id_venue: str, country: str) -> str:
    sports_key = SPORTS_KEY
    api_url = f"https://www.thesportsdb.com/api/v1/json/{sports_key}/lookupteam.php?id={id_venue}"
    async with httpx.AsyncClient() as client:
        try:
            print("Consultando evento:", id_venue)
            response = await client.get(api_url)
            response.raise_for_status()
            event_data = response.json()

            # Imprime la estructura completa de la respuesta
            print(f"Respuesta del evento {id_venue}:", event_data)

            if "teams" in event_data and event_data["teams"]:
                city = event_data["teams"][0].get("strLocation", None)
                print(f"Ciudad obtenida para el evento {id_venue}: {city}")
                return city if city else country  # Si no hay location, usa country
            return country  
        except httpx.RequestError as e:
            print(f"Error al consultar el evento {id_venue}: {e}")
            return country


# Función para obtener el pronóstico usando OpenAI
async def get_match_prediction(home_team: str, away_team: str, date: str, weather: dict) -> str:
    tokens = 200
    prompt = f"""
    Análisis del Partido: {home_team} vs {away_team}
    Fecha: {date}
    Clima: Temperatura {weather['temperature']}°C, Viento {weather['wind_speed']} km/h, Condiciones {weather['description']}
    Basado en las condiciones climáticas y el contexto actual de los equipos, ¿qué pronóstico harías para este partido?
    Proporciona un análisis breve, conciso y considera cómo las condiciones pueden afectar el juego. Procura utilizar menos 
    de {tokens} tokens y terminar el parrafo al final del texto. 
    """
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
        )
        return response.choices[0].message.content.strip()
    except openai.OpenAIError as e:
        return f"Error al obtener el pronóstico: {str(e)}"

@router.post("/update-events")
async def update_events(db: Session = Depends(get_db)):
    sports_key = SPORTS_KEY
    league_ids = ["4335", "4351"]  # IDs de las ligas a consultar
    all_enriched_events = []

    for id_league in league_ids:
        api_url = f"https://www.thesportsdb.com/api/v1/json/{sports_key}/eventsnextleague.php?id={id_league}"

        try:
            # Obtener los eventos desde el API
            async with httpx.AsyncClient() as client:
                response = await client.get(api_url)
                response.raise_for_status()

            data = response.json()
            events = data.get("events", [])
            ban = 0 # bandera para determinar si buscar weather por country despues de que falla por location 

            # Recolectar los idEvent actuales desde la respuesta del API
            current_event_ids = []

            for event in events:
                id_event = event.get("idEvent")
                if not id_event:
                    continue
                home_team = event.get("strHomeTeam")
                away_team = event.get("strAwayTeam")
                date_event = event.get("dateEvent")
                country = event.get("strCountry")
                venue = event.get("idVenue")
                if not venue:
                    continue
                current_event_ids.append(id_event)

                # Obtener la ciudad o coordenadas
                city_or_map = await get_city_for_event(venue, country)
                if re.search(r"°|′|″", city_or_map):
                    print(f"Usando coordenadas: {city_or_map}")
                    weather = await get_weather_by_coordinates(city_or_map, date_event)
                else:
                    if country == city_or_map: # Significa que no encontro Map, se busca por location del home_team
                        city_or_map = await get_location_for_event(event.get("idHomeTeam"), country)
                        if city_or_map != country: # Significa que encontro Location 
                            ban = 1

                    print(f"Usando ciudad o país: {city_or_map}")
                    if city_or_map == 'Brazil':
                        city_or_map = 'Brasil'

                    weather = await get_weather(city_or_map, date_event)

                    if weather["temperature"] == "Desconocida" and ban: # Se intenta buscar por pais
                        ban = 0
                        city_or_map = country
                        if city_or_map == 'Brazil':
                            city_or_map = 'Brasil'
                        weather = await get_weather(city_or_map, date_event)

                # Obtener el pronóstico
                pronostico = await get_match_prediction(home_team, away_team, date_event, weather)

                # Enriquecer el evento
                enriched_event = {
                    "idEvent": id_event,
                    "strEvent": event.get("strEvent"),
                    "strHomeTeam": home_team,
                    "strAwayTeam": away_team,
                    "idHomeTeam": event.get("idHomeTeam"),
                    "idAwayTeam": event.get("idAwayTeam"),
                    "dateEvent": event.get("dateEvent"),
                    "strTime": event.get("strTime"),
                    "strHomeTeamBadge": event.get("strHomeTeamBadge"),
                    "strAwayTeamBadge": event.get("strAwayTeamBadge"),
                    "idLeague": id_league,
                    "idVenue": event.get("idVenue"),
                    "strVenue": event.get("strVenue", "Desconocido"),
                    "clima": weather,
                    "pronostico": pronostico,
                }

                # Guardar o actualizar en la base de datos
                existing_event = db.query(EventModel).filter_by(id_event=id_event).first()
                if existing_event:
                    existing_event.event_data = enriched_event
                    existing_event.updated_at = datetime.now()
                else:
                    new_event = EventModel(
                        id_event=id_event,
                        id_league=id_league,
                        date_event=date_event,
                        event_data=enriched_event
                    )
                    db.add(new_event)
                db.commit()

                all_enriched_events.append(enriched_event)

            # Eliminar eventos que ya no están en la respuesta del API
            stored_events = db.query(EventModel).filter_by(id_league=id_league).all()
            for stored_event in stored_events:
                if stored_event.id_event not in current_event_ids:
                    db.delete(stored_event)
            db.commit()

        except httpx.RequestError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error al comunicarse con la API externa: {e}",
            )

    return {"message": "Eventos actualizados exitosamente", "events": all_enriched_events}

@router.get("/next", response_model=List[Event])
def get_next_events(db: Session = Depends(get_db)):
    # Consultar todos los eventos desde la base de datos
    events = db.query(EventModel).order_by(EventModel.date_event).all()
    # Transformar event_data (JSON) a la estructura de Event
    return [Event(**event.event_data) for event in events]
