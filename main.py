from fastapi import FastAPI, Query
from supabase import create_client
from dotenv import load_dotenv
import os
import math

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(title="API INEGI - Supabase")

TABLA = "Pako-INEGI"


@app.get("/")
def inicio():
    return {"mensaje": "API INEGI conectada a Supabase"}


# 1. Catálogo general
@app.get("/api/unidades")
def obtener_unidades():
    respuesta = supabase.table(TABLA).select(
        "identificación, nom_estab, entidad, municipio, localidad"
    ).limit(100).execute()

    return respuesta.data


# 2. Buscador por nombre
@app.get("/api/unidades/buscar")
def buscar_por_nombre(nombre: str = Query(...)):
    respuesta = supabase.table(TABLA).select("*").ilike(
        "nom_estab", f"%{nombre}%"
    ).limit(100).execute()

    return respuesta.data


# 3. Filtros múltiples dinámicos
@app.get("/api/unidades/filtro")
def filtrar_unidades(estado: str = None, actividad: str = None):
    consulta = supabase.table(TABLA).select("*")

    if estado:
        consulta = consulta.eq("entidad", estado)

    if actividad:
        consulta = consulta.ilike("nombre_act", f"%{actividad}%")

    respuesta = consulta.limit(100).execute()
    return respuesta.data


# 4. KPI estatal
@app.get("/api/estadisticas/total_por_estado")
def total_por_estado():
    respuesta = supabase.table(TABLA).select("entidad").execute()

    conteo = {}

    for fila in respuesta.data:
        estado = fila.get("entidad")
        if estado:
            conteo[estado] = conteo.get(estado, 0) + 1

    resultado = [
        {"estado": estado, "total_unidades": total}
        for estado, total in conteo.items()
    ]

    return resultado


# 5. Consulta por ID
@app.get("/api/unidades/{id}")
def obtener_unidad_por_id(id: int):
    respuesta = supabase.table(TABLA).select("*").eq(
        "identificación", id
    ).execute()

    if respuesta.data:
        return respuesta.data[0]

    return {"mensaje": "Unidad económica no encontrada"}


# 6. Perfil completo anidado
@app.get("/api/unidades/{id}/perfil_completo")
def perfil_completo(id: int):
    respuesta = supabase.table(TABLA).select("*").eq(
        "identificación", id
    ).execute()

    if not respuesta.data:
        return {"mensaje": "Unidad económica no encontrada"}

    dato = respuesta.data[0]

    perfil = {
        "unidad": {
            "id": dato.get("identificación"),
            "nombre": dato.get("nom_estab"),
            "razon_social": dato.get("raz_social")
        },
        "ubicacion": {
            "entidad": dato.get("entidad"),
            "municipio": dato.get("municipio"),
            "localidad": dato.get("localidad"),
            "latitud": dato.get("latitud"),
            "longitud": dato.get("longitud")
        },
        "contacto": {
            "telefono": dato.get("telefono"),
            "correo": dato.get("correoelec"),
            "sitio_web": dato.get("www")
        },
        "actividad": {
            "actividad": dato.get("nombre_act")
        }
    }

    return perfil


# 7. Búsqueda geoespacial
@app.get("/api/unidades/cercanas")
def unidades_cercanas(lat: float, lon: float, radio: float):
    respuesta = supabase.table(TABLA).select("*").execute()

    cercanas = []

    for unidad in respuesta.data:
        try:
            lat2 = float(unidad.get("latitud"))
            lon2 = float(unidad.get("longitud"))

            distancia = calcular_distancia(lat, lon, lat2, lon2)

            if distancia <= radio:
                unidad["distancia_km"] = round(distancia, 2)
                cercanas.append(unidad)

        except:
            pass

    return cercanas


def calcular_distancia(lat1, lon1, lat2, lon2):
    radio_tierra = 6371

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return radio_tierra * c