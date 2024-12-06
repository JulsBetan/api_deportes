API Deportes

Este repositorio contiene la API que gestiona la lógica de negocio para la aplicación King Tide. Proporciona endpoints para gestionar eventos deportivos, pronósticos y más.

Requisitos previos

	•	Python 3.11 o superior
	•	PostgreSQL
	•	virtualenv o similar para entornos virtuales

Instalación

	1.	Clonar el repositorio:
git clone https://github.com/usuario/api_deportes.git
cd api_deportes
	2.	Crear un entorno virtual e instalar dependencias:
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
	3.	Configurar variables de entorno en un archivo .env (ejemplo en .env.example).

Ejecución local

	1.	Aplicar migraciones:
alembic upgrade head
	2.	Ejecutar la aplicación:
uvicorn app.main:app –reload

La API estará disponible en http://localhost:8000.

Docker

Construir la imagen Docker:

docker build -t usuario/api_deportes:latest .

Ejecutar el contenedor:

docker run -p 8000:8000 usuario/api_deportes:latest

Endpoints

La documentación Swagger está disponible en:
	•	http://localhost:8000/docs

Pruebas

Ejecutar pruebas unitarias:
pytest

Licencia

Este proyecto está bajo la licencia MIT.
