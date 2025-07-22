# analizar_csv.py mejorado con limpieza de nacionalidades y cache persistente

import csv
import requests
import unicodedata
import re
import time
import json
import shelve
from concurrent.futures import ThreadPoolExecutor, as_completed

# =====================
# CACHE Y SINONIMOS
# =====================
_cache_archivo = "cache_nacionalidades.db"

NACIONALIDADES_SINONIMOS = {
    "argentina": "Argentina",
    "argentino": "Argentina",
    "arg": "Argentina",
    "argenitno": "Argentina",
    "arentina": "Argentina",
    "atgentina": "Argentina",
    "atgentine": "Argentina",
    "argentinage": "Argentina",
    "argentinian": "Argentina",
    "argentine": "Argentina",
    "buenos aires": "Argentina",
    "caba": "Argentina",
    "puana": "Argentina",
    "no definida": "No especificada",
    "no especificada": "No especificada",
    "sin dato": "No especificada",
    "n/a": "No especificada",
    "extraterrestre": "No especificada"
}

localidades_comunes = {
    "avellaneda", "lujan", "laprida", "moron", "rosario",
    "general rodriguez", "san isidro", "quilmes"
}

# =====================
# FUNCIONES AUXILIARES
# =====================

def limpiar_texto(texto):
    if not texto:
        return ""
    if isinstance(texto, bytes):
        texto = texto.decode('latin-1', errors='replace')
    texto = unicodedata.normalize('NFC', str(texto))
    texto = texto.strip()
    texto = ''.join(c for c in texto if c.isprintable())
    return texto

def normalizar_str(s):
    if not isinstance(s, str):
        return s
    s = s.lower().strip()
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return s

def consultar_ollama(prompt, modelo="llama3:8b", url_ollama="http://localhost:11434", max_retries=3, timeout_seconds=60):
    payload = {
        "model": modelo,
        "prompt": prompt,
        "stream": False
    }
    for intento in range(1, max_retries + 1):
        try:
            response = requests.post(
                f"{url_ollama}/api/generate",
                json=payload,
                timeout=timeout_seconds
            )
            response.raise_for_status()
            return response.json().get('response', '').strip()
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            if intento == max_retries:
                raise
            time.sleep(2 * intento)
        except requests.exceptions.RequestException as e:
            print(f"Error al consultar Ollama: {e}")
            return None

# =====================
# FUNCION PRINCIPAL
# =====================

def analizar_nacionalidad(nacionalidad_texto):
    texto_clave = limpiar_texto(nacionalidad_texto or "").lower()
    clave_normalizada = normalizar_str(texto_clave)

    with shelve.open(_cache_archivo) as cache:
        if clave_normalizada in cache:
            return cache[clave_normalizada]

        if clave_normalizada in NACIONALIDADES_SINONIMOS:
            valor = NACIONALIDADES_SINONIMOS[clave_normalizada]
            resultado = {
                "es_argentino": valor.lower() == "argentina",
                "nacionalidad_normalizada": valor,
                "confianza": "alta" if valor != "No especificada" else "baja"
            }
            cache[clave_normalizada] = resultado
            return resultado

        if len(clave_normalizada) < 3 or not clave_normalizada.isalpha():
            resultado = {
                "es_argentino": False,
                "nacionalidad_normalizada": "No especificada",
                "confianza": "baja"
            }
            cache[clave_normalizada] = resultado
            return resultado

        if clave_normalizada in localidades_comunes:
            resultado = {
                "es_argentino": True,
                "nacionalidad_normalizada": "Argentina",
                "confianza": "media"
            }
            cache[clave_normalizada] = resultado
            return resultado

        prompt = f"""Analiza la siguiente nacionalidad y responde con un JSON valido:

Nacionalidad: \"{nacionalidad_texto}\"

Formato:
{{
  \"es_argentino\": true/false,
  \"nacionalidad_normalizada\": \"...\",
  \"confianza\": \"alta/media/baja\"
}}

Solo responde el JSON, sin texto adicional."""

        respuesta = consultar_ollama(prompt)
        resultado = {
            'es_argentino': False,
            'nacionalidad_normalizada': nacionalidad_texto,
            'confianza': 'baja'
        }

        try:
            inicio = respuesta.find('{')
            fin = respuesta.rfind('}') + 1
            json_str = respuesta[inicio:fin]
            parsed = json.loads(json_str)
            if all(k in parsed for k in resultado):
                resultado = parsed
        except:
            if 'argentin' in respuesta.lower():
                resultado = {
                    'es_argentino': True,
                    'nacionalidad_normalizada': 'Argentina',
                    'confianza': 'media'
                }

        cache[clave_normalizada] = resultado
        return resultado

# =====================
# EJEMPLO DE PRUEBA
# =====================
if __name__ == "__main__":
    ejemplos = [
        "Argentinian", "ATGENTINA", "extraterrestre", "sin dato", "Avellaneda", "brasil", "francesa"
    ]
    for e in ejemplos:
        print(f"{e} → {analizar_nacionalidad(e)}")
