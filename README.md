# Normalización de Localidades, Distritos y Provincias de Alumnos

Este proyecto contiene un script en Python (`analizar_csv.py`) que permite normalizar y auditar los datos de ubicación (localidad, distrito, provincia) de un archivo CSV de alumnos, utilizando una API de geodatos y un archivo auxiliar de localidades y códigos postales.

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

## Notas
- El archivo original **nunca se modifica**.
- El script es robusto ante errores de codificación y prioriza siempre el código postal para la normalización.
- Si tienes dudas sobre alguna columna o el funcionamiento, revisa los comentarios en el código fuente. 