from fastapi import APIRouter, HTTPException
import httpx
from pydantic import BaseModel
from typing import List

class Event(BaseModel):
    idEvent: str
    strEvent: str
    strHomeTeam: str
    strAwayTeam: str
    idHomeTeam: str
    idAwayTeam: str
    dateEvent: str
    strTime: str
    strHomeTeamBadge: str
    strAwayTeamBadge: str
    idLeague: str
    idVenue: str
    strVenue: str
    strPronostico: str = ""

router = APIRouter()

@router.get("/test")
async def test_endpoint():
    """
    Endpoint de prueba para verificar si aparece en Swagger.
    """
    return {"message": "Este es un endpoint de prueba"}

# Función para obtener el pronóstico usando OpenAI
async def get_match_prediction(home_team: str, away_team: str, date: str, weather: dict) -> str:
    prompt = f"""
    Análisis del Partido: {home_team} vs {away_team}
    Fecha: {date}
    Clima: Temperatura {weather['temperature']}°C, Viento {weather['wind_speed']} km/h, Condiciones {weather['description']}
    Basado en las condiciones climáticas y el contexto actual, ¿qué pronóstico harías para este partido?
    Proporciona un análisis detallado y considera cómo las condiciones pueden afectar el juego.
    """
    
    headers = {
        "Authorization": f"Bearer YOUR_OPENAI_API_KEY",
        "Content-Type": "application/json",
    }
    data = {
        "model": "text-davinci-003",
        "prompt": prompt,
        "max_tokens": 150,
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post("https://api.openai.com/v1/completions", json=data, headers=headers)
            response.raise_for_status()
            chat_response = response.json()
            return chat_response["choices"][0]["text"].strip()
        except httpx.RequestError as e:
            return f"Error al obtener el pronóstico: {e}"

# Función para obtener el clima
async def get_weather(city: str, date: str) -> dict:
    api_key = "YOUR_WEATHER_API_KEY"  # Clave de OpenWeatherMap u otro servicio
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            weather_data = response.json()
            return {
                "temperature": weather_data["main"]["temp"],
                "wind_speed": weather_data["wind"]["speed"],
                "description": weather_data["weather"][0]["description"],
            }
        except httpx.RequestError as e:
            return {"error": f"Error al obtener el clima: {e}"}


# Define el endpoint
@router.get("/next", response_model=list[Event])
async def get_next_events():
    # URL de la API de terceros
    api_url = "https://www.thesportsdb.com/api/v1/json/3/eventsnext.php?id=4335"

    try:
        # Realiza la solicitud a la API externa
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url)
            response.raise_for_status()  # Lanza una excepción si el estado no es 200

        # Procesa la respuesta
        data = response.json()

        # Extrae los eventos y los campos deseados
        events = data.get("events", [])

       enriched_events = []

        for event in events:
            # Extrae datos básicos del evento
            home_team = event.get("strHomeTeam")
            away_team = event.get("strAwayTeam")
            date_event = event.get("dateEvent")
            venue = event.get("strVenue", "Unknown location")

            # Obtén el clima y el pronóstico
            weather = await get_weather(venue, date_event)
            pronostico = await get_match_prediction(home_team, away_team, date_event, weather)

            # Enriquecer el evento con el pronóstico
            enriched_events.append({
                "idEvent": event.get("idEvent"),
                "strEvent": event.get("strEvent"),
                "strHomeTeam": home_team,
                "strAwayTeam": away_team,
                "idHomeTeam": event.get("idHomeTeam"),
                "idAwayTeam": event.get("idAwayTeam"),
                "dateEvent": date_event,
                "strTime": event.get("strTime"),
                "strHomeTeamBadge": event.get("strHomeTeamBadge"),
                "strAwayTeamBadge": event.get("strAwayTeamBadge"),
                "idLeague": event.get("idLeague"),
                "idVenue": event.get("idVenue"),
                "strVenue": venue,
                "Pronostico": pronostico,
            })

        return enriched_events 

    except httpx.RequestError as e:
        # Maneja errores relacionados con la solicitud
        raise HTTPException(
            status_code=500,
            detail=f"Error al comunicarse con la API externa: {e}",
        )
    except Exception as e:
        # Maneja errores generales
        raise HTTPException(
            status_code=500,
            detail=f"Error inesperado: {e}",
        )
