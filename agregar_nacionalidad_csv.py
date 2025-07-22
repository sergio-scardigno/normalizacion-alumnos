# agregar_nacionalidad_csv.py mejorado con paralelismo e integración con cache persistente

import csv
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from analizar_csv import analizar_nacionalidad, limpiar_texto
from pathlib import Path

def procesar_archivo(entrada: Path, salida: Path, limite_filas: int | None = None, max_workers: int = 4):
    with entrada.open(mode="r", encoding="utf-8", errors="replace") as f_in, \
            salida.open(mode="w", encoding="utf-8", newline="") as f_out:

        lector = list(csv.DictReader(f_in))
        if not lector:
            print("❌ El archivo está vacío o no tiene encabezados.")
            return

        if limite_filas:
            lector = lector[:limite_filas]

        campos_originales = lector[0].keys()
        columnas_extra = [
            "es_argentino",
            "nacionalidad_normalizada",
            "confianza_nacionalidad",
        ]
        escritor = csv.DictWriter(f_out, fieldnames=list(campos_originales) + columnas_extra)
        escritor.writeheader()

        def procesar_fila(fila):
            nacionalidad = limpiar_texto(fila.get("nacionalidad", "N/A"))
            analisis = analizar_nacionalidad(nacionalidad)
            fila["es_argentino"] = analisis["es_argentino"]
            fila["nacionalidad_normalizada"] = analisis["nacionalidad_normalizada"]
            fila["confianza_nacionalidad"] = analisis["confianza"]
            return fila

        print(f"→ Procesando {len(lector)} filas con {max_workers} hilos...")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futuros = [executor.submit(procesar_fila, fila) for fila in lector]
            for i, futuro in enumerate(as_completed(futuros), 1):
                try:
                    fila_procesada = futuro.result()
                    escritor.writerow(fila_procesada)
                    if i % 100 == 0:
                        print(f"Procesadas {i} filas", flush=True)
                except Exception as e:
                    print(f"❌ Error en fila {i}: {e}")

        print(f"\n✅ Archivo generado: {salida} (filas procesadas: {len(lector)})")

def main():
    parser = argparse.ArgumentParser(description="Agregar columnas de nacionalidad normalizada a un CSV")
    parser.add_argument("--entrada", default="alumnos/fp_alumnos.csv", help="Ruta al CSV de entrada")
    parser.add_argument("--salida", default="fp_alumnos_nacionalidad.csv", help="Ruta al CSV de salida")
    parser.add_argument("--muestras", type=int, help="Procesar solo N filas para prueba")
    parser.add_argument("--hilos", type=int, default=4, help="Cantidad de hilos para paralelizar")

    args = parser.parse_args()

    entrada = Path(args.entrada).expanduser()
    salida = Path(args.salida).expanduser()

    if not entrada.exists():
        print(f"❌ Archivo de entrada no encontrado: {entrada}")
        return

    procesar_archivo(entrada, salida, args.muestras, max_workers=args.hilos)

if __name__ == "__main__":
    main()