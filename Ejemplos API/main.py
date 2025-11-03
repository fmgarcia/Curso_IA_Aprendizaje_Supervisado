# Ejemplo de uso de una API en Python
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from base_model import BaseModel
import requests
import json
from videojuego_rawg import Videojuego_rawg
import datetime
import time


def insertar_videojuego(id, nombre, fecha_lanzamiento, imagen, valoracion):
    with Session(engine) as session:
        select_stmt = select(Videojuego_rawg).filter_by(id = id) # Consulta para verificar si el videojuego ya existe
        existe = session.scalars(select_stmt).all() # Ejecuta la consulta y obtiene todos los resultados y los almacena en una lista
        if len(existe) == 0: # Si no existe, lo inserta
            nuevo_videojuego = Videojuego_rawg(
                id=id,
                nombre=nombre,
                fecha_lanzamiento=fecha_lanzamiento,
                imagen=imagen,
                valoracion=valoracion
            )
            session.add(nuevo_videojuego) # Agrega el nuevo videojuego a la sesión
            session.commit() # Confirma la transacción
            print(f"Videojuego con id {id} insertado en la base de datos.")


# Aquí empieza el programa principal

# Paso 1. Crear la base de datos de ejemplo con las tablas definidas
engine = create_engine("sqlite:///videojuegos.db", echo=False) # Conexión a una base de datos SQLite, True para ver el log de SQL. Si no existe, la crea, si existe, se conecta.
BaseModel.metadata.create_all(engine)  # Crea las tablas en la base de datos según los modelos definidos

# Paso 2. Obtener datos de la API y almacenarlos en la base de datos
videojuegos = []
key = "08c18ae30e654ff499c546879ec660f2"  # Reemplaza con tu clave de API válida
pagina_inicial = 3
pagina_final = 10  # Número de páginas a obtener
page_size = 40  # Limitar a 40 resultados por página

for page in range(pagina_inicial, pagina_final + 1):
    url = f"https://api.rawg.io/api/games?key={key}&page={page}&page_size={page_size}"  # URL de la API con el parámetro page_size para limitar resultados
    cabeceras = {}
    cabeceras["User-Agent"] = "PostmanRuntime/7.49.0"
    response = requests.get(url, headers=cabeceras) # Realiza la solicitud GET a la API   
    if response.status_code == 200:
        json_data = json.loads(response.text)  # Carga la respuesta JSON en una variable de tipo diccionario de Python
        resultados = json_data["results"]  # Extrae la lista de resultados del diccionario
        for resultado in resultados: # Paso 3. Itera sobre cada resultado en la lista e inserta en la base de datos
            id = resultado["id"]
            nombre = resultado["name"]
            fecha_lanzamiento = datetime.datetime.strptime(resultado.get("released"), "%Y-%m-%d").year if resultado.get("released") else None
            imagen = resultado.get("background_image", None)
            valoracion = resultado.get("rating", 0.0)
            insertar_videojuego(id, nombre, fecha_lanzamiento, imagen, valoracion)

    else:
        print(f"Error al obtener datos de la API: {response.status_code}")
        
    if page != pagina_final:
        time.sleep(5)  # Espera 5 segundos entre solicitudes para no sobrecargar la API
print("Proceso completado.")
