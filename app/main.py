from fastapi import FastAPI
from app.routes import users
from app.routes.events import router as events

from app.database import Base, engine
from app.models import User

from fastapi.middleware.cors import CORSMiddleware

# Crear las tablas en la base de datos
# print("Creando tablas en la base de datos...")
# Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the API"}

app.include_router(users.router, prefix="/users", tags=["Users"])

app.include_router(events, prefix="/events", tags=["Events"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == '__main__':
    uvicorn.run("main:app", host='127.0.0.1', port=8000, log_level="info", reload=True)
