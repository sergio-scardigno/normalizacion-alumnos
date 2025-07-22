# Normalización de Datos de Alumnos (Ubicación y Nacionalidad)

Este proyecto incluye dos scripts principales en Python:

- `analizar_csv.py`: normaliza y audita las columnas de **localidad**, **distrito**, **provincia** y **código postal** mediante una API de geodatos y un archivo auxiliar de localidades.
- `agregar_nacionalidad_csv.py`: analiza la columna **nacionalidad** para determinar si el alumno es argentino y normaliza el texto de la nacionalidad con ayuda de un modelo LLM local (Ollama).

Cada uno genera un CSV de salida con columnas adicionales que facilitan la auditoría.

## ¿Qué hace el script?

- Lee un archivo CSV principal (por defecto `fp_alumnos.csv`) con datos de alumnos.
- Normaliza las columnas de **localidad**, **distrito** y **provincia** usando la API de geodatos, priorizando siempre el **código postal** si está presente.
- Si la API no encuentra coincidencias, utiliza un archivo auxiliar (`localidades.csv`) para sugerir la localidad según el código postal.
- Genera un archivo de salida nuevo (por ejemplo, `ubicaciones_normalizadas_1_50.csv`) con los resultados y columnas de auditoría.

## ¿Cómo usarlo?

1. Asegúrate de tener los archivos `fp_alumnos.csv` y `localidades.csv` en el mismo directorio que el script.
2. Ejecuta el script con Python 3:

```bash
python analizar_csv.py
```

Por defecto, procesará los primeros 50 registros. Puedes modificar el rango de registros cambiando los parámetros `inicio` y `fin` en la última línea del script.

## Columnas del archivo de salida

- **localidad_original**: Valor de la columna "localidad" en el archivo original.
- **localidad_normalizada**: Nombre de la localidad normalizada según la API o el CSV auxiliar.
- **localidad_fuente**: Cómo se obtuvo la localidad normalizada:
  - `normalizada`: Encontrada por la API (con o sin código postal).
  - `sugerida_csv`: Sugerida por el archivo auxiliar `localidades.csv`.
  - `no_encontrada`: No se pudo normalizar.
- **distrito_original**: Valor de la columna "distrito" en el archivo original.
- **distrito_normalizado**: Nombre del distrito normalizado (por la API o inferido de la localidad).
- **distrito_fuente**: Cómo se obtuvo el distrito:
  - `inferida`: Inferido a partir de la localidad normalizada.
  - `normalizada`: Encontrado por la API.
  - `no_encontrada`: No se pudo normalizar.
- **provincia_original**: Valor de la columna "provincia" en el archivo original.
- **provincia_normalizada**: Nombre de la provincia normalizada (por la API o inferida de la localidad).
- **provincia_fuente**: Cómo se obtuvo la provincia:
  - `inferida`: Inferida a partir de la localidad normalizada.
  - `normalizada`: Encontrada por la API.
  - `no_encontrada`: No se pudo normalizar.
- **codigo_postal_original**: Código postal del registro original (si existe).
- **cp_coincide_con_localidad**: Indica si el código postal original corresponde a la localidad normalizada según el CSV auxiliar:
  - `SI`: Coincide.
  - `NO`: No coincide.
  - `NO_APLICA`: No hay código postal o no está en el CSV auxiliar.

## Ejemplo de uso por lotes

Para procesar registros del 51 al 100, modifica la última línea del script así:

```python
analizar_csv("fp_alumnos.csv", inicio=50, fin=100)
```

Esto generará un archivo `ubicaciones_normalizadas_51_100.csv`.

## Requisitos
- Python 3
- Paquete `requests` (puedes instalarlo con `pip install requests`)
- [Ollama](https://ollama.ai/) en funcionamiento en `http://localhost:11434` con un modelo cargado (por defecto se usa `llama3:8b`)

## Scripts de Nacionalidad (`agregar_nacionalidad_csv.py` y `analizar_csv.py`)

### ¿Qué hacen estos scripts?

- `analizar_csv.py` contiene la función `analizar_nacionalidad()` que usa reglas heurísticas y un modelo LLM local para clasificar y normalizar nacionalidades.
- `agregar_nacionalidad_csv.py` aplica esa función a todas las filas de un CSV y agrega tres columnas nuevas.

### Columnas añadidas por `agregar_nacionalidad_csv.py`

- **es_argentino**: `true`/`false` si la nacionalidad corresponde a Argentina.
- **nacionalidad_normalizada**: Texto normalizado de la nacionalidad.
- **confianza_nacionalidad**: Nivel de confianza (`alta`, `media`, `baja`).

### Ejemplos de uso

```bash
# Procesar todo el archivo
python agregar_nacionalidad_csv.py --entrada fp_alumnos.csv --salida fp_alumnos_nacionalidad.csv --hilos 8

# Procesar sólo 500 filas
python agregar_nacionalidad_csv.py --muestras 500
```

---

## Notas
- El archivo original **nunca se modifica**.
- Los scripts son robustos ante errores de codificación y priorizan siempre la mejor fuente de datos disponible.
- Si tienes dudas sobre alguna columna o el funcionamiento, revisa los comentarios en el código fuente.