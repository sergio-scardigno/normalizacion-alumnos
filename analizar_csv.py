# analizar_csv.py mejorado con limpieza de nacionalidades, IA Ollama, y cache persistente

import csv
import requests
import unicodedata
import re
import time
import json
import shelve

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


def analizar_nacionalidad(nacionalidad_texto, lugar_nacimiento=None):
    nacionalidad = limpiar_texto(nacionalidad_texto or "")
    nacimiento = limpiar_texto(lugar_nacimiento or "")
    clave_cache = normalizar_str(f"{nacionalidad}|{nacimiento}")

    with shelve.open(_cache_archivo) as cache:
        if clave_cache in cache:
            return cache[clave_cache]

        prompt = f"""Dado el siguiente registro, responde en formato JSON la nacionalidad real basada en lugar de nacimiento y nacionalidad reportada. Priorizá el lugar de nacimiento si hay contradicción.

Datos:
- Nacionalidad declarada: "{nacionalidad}"
- Lugar de nacimiento: "{nacimiento}"

Formato de respuesta:
{{
  "es_argentino": true/false,
  "nacionalidad_normalizada": "Nombre del país",
  "confianza": "alta" / "media" / "baja"
}}

Solo responde el JSON. No agregues explicación ni texto adicional."""

        respuesta = consultar_ollama(prompt)

        # DEBUG
        if not respuesta or not respuesta.strip():
            print(f"🟥 Respuesta vacía de Ollama para:\n→ Nacionalidad: {nacionalidad}\n→ Lugar de nacimiento: {nacimiento}")
        else:
            print(f"\n🟡 Respuesta de Ollama:\n{respuesta}\n")

        try:
            if not respuesta or not respuesta.strip():
                raise ValueError("Respuesta vacía de Ollama")

            inicio = respuesta.find("{")
            fin = respuesta.rfind("}") + 1
            if inicio == -1 or fin == -1:
                raise ValueError("No se encontró JSON válido en la respuesta")

            json_str = respuesta[inicio:fin]
            resultado = json.loads(json_str)

            if not all(k in resultado for k in ["es_argentino", "nacionalidad_normalizada", "confianza"]):
                raise ValueError("JSON incompleto")

        except Exception as e:
            print(f"❌ Error procesando con IA: {e}")
            print(f"🟥 Respuesta cruda:\n{respuesta}")
            resultado = {
                "es_argentino": False,
                "nacionalidad_normalizada": nacionalidad or "No especificada",
                "confianza": "baja"
            }

        cache[clave_cache] = resultado
        return resultado


# Prueba rápida
if __name__ == "__main__":
    ejemplos = [
        {"nacionalidad": "Argentinian", "lugar_nacimiento": "Perú"},
        {"nacionalidad": "extraterrestre", "lugar_nacimiento": "Buenos Aires"},
        {"nacionalidad": "Paraguay", "lugar_nacimiento": ""},
        {"nacionalidad": "", "lugar_nacimiento": "Avellaneda"},
    ]
    for e in ejemplos:
        print(f"{e} → {analizar_nacionalidad(e['nacionalidad'], e['lugar_nacimiento'])}")
