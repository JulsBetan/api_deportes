import re

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

# Ejemplo de uso
dms_input = "39°56′39″N 0°06′13″O"
decimal_input = "42.2118°N 8.7397°W" #"42.2118°N 8.7397°W"

coordinates_dms = convert_to_decimal(dms_input)
coordinates_decimal = convert_to_decimal(decimal_input)

if coordinates_dms:
    print(f"DMS - Latitud: {coordinates_dms[0]}, Longitud: {coordinates_dms[1]}")
else:
    print("Coordenadas DMS no válidas.")

if coordinates_decimal:
    print(f"Decimal - Latitud: {coordinates_decimal[0]}, Longitud: {coordinates_decimal[1]}")
else:
    print("Coordenadas decimales no válidas.")
