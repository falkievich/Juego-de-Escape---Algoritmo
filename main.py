from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# CORS (si accedieras desde otro dominio, aunque en este caso no hace falta)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servimos el archivo estático
app.mount("/static", StaticFiles(directory="static"), name="static")

# Ruta raíz: devuelve tu HTML
@app.get("/")
def root():
    return FileResponse("static/index.html")

# Parámetros del juego
filas, columnas = 3, 3
pos_roja = [2, 0]
pos_amarilla = [0, 2]
pos_salida = [0, 2]
turno_actual = 1
juego_terminado = False
mensaje_final = None

MOVIMIENTOS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

def es_movimiento_valido(nueva_pos, pos_roja, pos_amarilla):
    x, y = nueva_pos
    if 0 <= x < filas and 0 <= y < columnas:
        if nueva_pos != pos_roja and nueva_pos != pos_amarilla:
            return True
    return False

def mover_hacia_objetivo(pos_actual, objetivo, otra_ficha):
    posibles = []
    for dx, dy in MOVIMIENTOS:
        nueva = [pos_actual[0] + dx, pos_actual[1] + dy]
        if es_movimiento_valido(nueva, otra_ficha, pos_actual):
            distancia = abs(nueva[0] - objetivo[0]) + abs(nueva[1] - objetivo[1])
            posibles.append((distancia, nueva))
    if posibles:
        posibles.sort(key=lambda x: x[0])
        return posibles[0][1]
    return pos_actual

@app.get("/estado")
def get_estado():
    global pos_roja, pos_amarilla, pos_salida, turno_actual, juego_terminado, mensaje_final

    if juego_terminado:
        return {
            "posRoja": pos_roja,
            "posAmarilla": pos_amarilla,
            "posSalida": pos_salida,
            "turno": turno_actual,
            "mensaje": mensaje_final
        }

    # Turno impar -> ficha roja se mueve
    if turno_actual % 2 == 1:
        pos_roja = mover_hacia_objetivo(pos_roja, pos_salida, pos_amarilla)
    else:
        pos_amarilla = mover_hacia_objetivo(pos_amarilla, pos_roja, pos_roja)

    # Verificamos condiciones de finalización
    if pos_roja == pos_salida:
        juego_terminado = True
        mensaje_final = "✅ ¡La ficha roja escapó con éxito!"
    elif pos_roja == pos_amarilla:
        juego_terminado = True
        mensaje_final = "🛑 ¡La ficha amarilla bloqueó a la roja!"

    estado = {
        "posRoja": pos_roja,
        "posAmarilla": pos_amarilla,
        "posSalida": pos_salida,
        "turno": turno_actual,
        "mensaje": mensaje_final
    }

    turno_actual += 1
    return estado
