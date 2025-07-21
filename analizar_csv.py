import csv
import requests
import unicodedata
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

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

def cargar_localidades_csv(ruta_archivo='localidades.csv'):
    localidades_por_cp = {}
    try:
        with open(ruta_archivo, mode='r', encoding='utf-8', errors='replace') as f:
            lector = csv.DictReader(f)
            for fila in lector:
                cp = limpiar_texto(fila.get('cp', ''))
                nombre = limpiar_texto(fila.get('nombre', ''))
                if cp and nombre:
                    localidades_por_cp[cp] = nombre
    except FileNotFoundError:
        print(f"Advertencia: No se encontró el archivo '{ruta_archivo}'. Se continuará sin él.")
    except Exception as e:
        print(f"Error al procesar el archivo de localidades: {str(e)}")
    return localidades_por_cp

def obtener_info_lugar(lugar, tipo, codigo_postal=None):
    if not lugar or not isinstance(lugar, str) or lugar.strip().lower() in ('sin provincia', 'n/a', ''):
        return None
    endpoints = {
        'provincia': ["provincias"],
        'distrito': ["departamentos", "municipios"],
        'localidad': ["localidades", "localidades-censales"]
    }
    endpoints_a_consultar = endpoints.get(tipo, [])
    for endpoint in endpoints_a_consultar:
        params = {
            "nombre": lugar,
            "campos": "id,nombre,provincia,departamento,municipio"
        }
        if codigo_postal:
            params['codigo_postal'] = codigo_postal
        try:
            response = requests.get(f"http://192.168.57.6:8080/api/{endpoint}", params=params)
            response.raise_for_status()
            data = response.json()
            time.sleep(0.1)
            if data and data.get(endpoint):
                return data[endpoint][0]
        except requests.exceptions.RequestException:
            continue
        except (KeyError, IndexError, TypeError):
            continue
    return None

def limpiar_dni(dni):
    if not isinstance(dni, str):
        return dni
    match = re.search(r'(\d+)', dni)
    return match.group(1) if match else dni

# =====================
# FUNCION PRINCIPAL
# =====================

def analizar_csv(ruta_archivo, inicio=0, fin=5000, devolver_resultados=False):
    localidades_conocidas = cargar_localidades_csv()
    resultados = []
    try:
        with open(ruta_archivo, mode='r', encoding='utf-8', errors='replace') as archivo_csv:
            lector_csv = csv.DictReader(archivo_csv)
            for i, fila in enumerate(lector_csv):
                if i < inicio:
                    continue
                if i >= fin:
                    break

                print(f"[{inicio+1}-{fin}] Procesando fila {i+1}...", flush=True)

                localidad_orig = limpiar_texto(fila.get("localidad", "N/A"))
                distrito_orig = limpiar_texto(fila.get("distrito", "N/A"))
                provincia_orig = limpiar_texto(fila.get("provincia", "N/A"))
                codigo_postal_orig = limpiar_texto(fila.get("codigo_postal", "")).strip()
                nombres = limpiar_texto(fila.get("nombres", ""))
                apellidos = limpiar_texto(fila.get("apellidos", ""))
                dni = limpiar_dni(fila.get("dni", ""))
                localidad_para_api = localidad_orig
                localidad_fuente = "no_encontrada"
                distrito_fuente = "no_encontrada"
                provincia_fuente = "no_encontrada"

                info_localidad = obtener_info_lugar(localidad_para_api, 'localidad', codigo_postal=codigo_postal_orig)
                if info_localidad:
                    localidad_fuente = "normalizada"
                if not info_localidad:
                    info_localidad = obtener_info_lugar(localidad_para_api, 'localidad')
                    if info_localidad:
                        localidad_fuente = "normalizada"
                if not info_localidad and codigo_postal_orig and codigo_postal_orig in localidades_conocidas:
                    localidad_sugerida = localidades_conocidas[codigo_postal_orig]
                    info_localidad = obtener_info_lugar(localidad_sugerida, 'localidad')
                    if info_localidad:
                        localidad_fuente = "sugerida_csv"

                localidad_norm = info_localidad['nombre'] if info_localidad else f"No encontrada: {localidad_orig}"

                if codigo_postal_orig and codigo_postal_orig in localidades_conocidas:
                    localidad_csv = localidades_conocidas[codigo_postal_orig]
                    cp_coincide = "SI" if normalizar_str(localidad_norm) == normalizar_str(localidad_csv) else "NO"
                else:
                    cp_coincide = "NO_APLICA"

                if provincia_orig.strip().lower() in ('sin provincia', 'n/a', ''):
                    if info_localidad and 'provincia' in info_localidad:
                        provincia_norm = info_localidad['provincia']['nombre']
                        provincia_fuente = 'inferida'
                    else:
                        provincia_norm = "No inferida"
                else:
                    info_provincia = obtener_info_lugar(limpiar_texto(provincia_orig), 'provincia')
                    if info_provincia:
                        provincia_norm = info_provincia['nombre']
                        provincia_fuente = 'normalizada'
                    else:
                        provincia_norm = f"No encontrada: {provincia_orig}"

                distrito_inferido = None
                if info_localidad and 'departamento' in info_localidad and info_localidad.get('departamento'):
                    distrito_inferido = info_localidad['departamento']['nombre']
                elif info_localidad and 'municipio' in info_localidad and info_localidad.get('municipio'):
                    distrito_inferido = info_localidad['municipio']['nombre']
                if distrito_inferido:
                    distrito_norm = distrito_inferido
                    distrito_fuente = 'inferida'
                else:
                    distrito_para_api = limpiar_texto(distrito_orig)
                    info_distrito = obtener_info_lugar(distrito_para_api, 'distrito', codigo_postal=codigo_postal_orig)
                    if not info_distrito:
                        info_distrito = obtener_info_lugar(distrito_para_api, 'distrito')
                    if info_distrito:
                        distrito_norm = info_distrito['nombre']
                        distrito_fuente = 'normalizada'
                    else:
                        distrito_norm = f"No encontrado: {distrito_orig}"

                resultado_fila = {
                    'nombres': nombres,
                    'apellidos': apellidos,
                    'dni': dni,
                    'localidad_original': localidad_orig, 'localidad_normalizada': localidad_norm, 'localidad_fuente': localidad_fuente,
                    'distrito_original': distrito_orig, 'distrito_normalizado': distrito_norm, 'distrito_fuente': distrito_fuente,
                    'provincia_original': provincia_orig, 'provincia_normalizada': provincia_norm, 'provincia_fuente': provincia_fuente,
                    'cp_coincide_con_localidad': cp_coincide
                }
                if codigo_postal_orig:
                    resultado_fila['codigo_postal_original'] = codigo_postal_orig
                resultados.append(resultado_fila)

        if devolver_resultados:
            print(f"✅ Lote {inicio+1}-{fin} completado con {len(resultados)} filas.", flush=True)
            return resultados

        if resultados:
            nombre_archivo_salida = f'ubicaciones_normalizadas_{inicio+1}_{fin}.csv'
            campos = list(resultados[0].keys())
            with open(nombre_archivo_salida, mode='w', encoding='utf-8', newline='') as f_out:
                escritor_csv = csv.DictWriter(f_out, fieldnames=campos, extrasaction='ignore')
                escritor_csv.writeheader()
                escritor_csv.writerows(resultados)
            print(f"✅ Lote {inicio+1}-{fin} guardado en {nombre_archivo_salida}", flush=True)

    except Exception as e:
        print(f"❌ Error al procesar lote {inicio}-{fin}: {str(e)}")
        return []

# ============================
# FUNCION PARALELA POR LOTES
# ============================

def procesar_archivo_con_threads(ruta_archivo, tamaño_lote=100, max_workers=2):
    try:
        with open(ruta_archivo, mode='r', encoding='utf-8', errors='replace') as f:
            total_lineas = sum(1 for _ in f) - 1

        print(f"📊 Total de registros a procesar: {total_lineas}")
        tareas = []
        resultados_totales = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for inicio in range(0, total_lineas, tamaño_lote):
                fin = min(inicio + tamaño_lote, total_lineas)
                print(f"→ Enviando lote {inicio+1} a {fin} al thread pool", flush=True)
                tareas.append(executor.submit(analizar_csv, ruta_archivo, inicio, fin, True))

            for i, future in enumerate(as_completed(tareas), start=1):
                try:
                    resultados = future.result()
                    resultados_totales.extend(resultados)
                    print(f"🔹 Lote {i} finalizado. Total acumulado: {len(resultados_totales)} filas", flush=True)
                except Exception as e:
                    print(f"❌ Error en lote {i}: {e}")

        if resultados_totales:
            nombre_archivo_salida = f'ubicaciones_normalizadas_completo.csv'
            campos = list(resultados_totales[0].keys())
            with open(nombre_archivo_salida, mode='w', encoding='utf-8', newline='') as f_out:
                escritor_csv = csv.DictWriter(f_out, fieldnames=campos, extrasaction='ignore')
                escritor_csv.writeheader()
                escritor_csv.writerows(resultados_totales)
            print(f"\n✅ Procesamiento completo. {len(resultados_totales)} registros guardados en '{nombre_archivo_salida}'")
        else:
            print("⚠ No se generaron resultados.")

    except Exception as e:
        print(f"❌ Error al procesar el archivo completo: {str(e)}")

# =====================
# EJECUCIÓN
# =====================

if __name__ == "__main__":
    procesar_archivo_con_threads("fp_alumnos.csv", tamaño_lote=100, max_workers=2)
