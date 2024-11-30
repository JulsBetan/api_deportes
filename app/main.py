from fastapi import FastAPI
from app.routes import users

from app.database import Base, engine
from app.models import User

from fastapi.middleware.cors import CORSMiddleware

# Crear las tablas en la base de datos
print("Creando tablas en la base de datos...")
Base.metadata.create_all(bind=engine)

app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

@app.get("/")
def read_root():
    return {"message": "Welcome to the API"}

app.include_router(users.router, prefix="/users", tags=["Users"])




