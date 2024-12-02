from fastapi import APIRouter, HTTPException
import httpx

from pydantic import BaseModel

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

router = APIRouter()

@router.get("/test")
async def test_endpoint():
    """
    Endpoint de prueba para verificar si aparece en Swagger.
    """
    return {"message": "Este es un endpoint de prueba"}

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
        filtered_events = [
            {
                "idEvent": event.get("idEvent"),
                "strEvent": event.get("strEvent"),
                "strHomeTeam": event.get("strHomeTeam"),
                "strAwayTeam": event.get("strAwayTeam"),
                "idHomeTeam": event.get("idHomeTeam"),
                "idAwayTeam": event.get("idAwayTeam"),
                "dateEvent": event.get("dateEvent"),
                "strTime": event.get("strTime"),
                "strHomeTeamBadge": event.get("strHomeTeamBadge"),
                "strAwayTeamBadge": event.get("strAwayTeamBadge"),
                "idLeague": event.get("idLeague"),
                "idVenue": event.get("idVenue"),
                "strVenue": event.get("strVenue"),
            }
            for event in events
        ]

        return filtered_events

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
