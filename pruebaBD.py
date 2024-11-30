import psycopg2
from psycopg2 import OperationalError

# Configura los parámetros de conexión
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "password" 

from sqlalchemy import create_engine, text

# Cadena de conexión
DATABASE_URL = "postgresql+psycopg2://postgres:password@localhost:5432/postgres"

# Crear motor de conexión
engine = create_engine(DATABASE_URL)

# Probar conexión
try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version();"))
        for row in result:
            print(f"Versión de PostgreSQL: {row[0]}")
except Exception as e:
    print(f"Error al conectar a la base de datos: {e}")
