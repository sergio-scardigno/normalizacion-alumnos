import csv

def analizar_incompletos(archivo_resultados):
    total = 0
    sin_localidad = 0
    sin_distrito = 0
    sin_provincia = 0
    incompletos = 0
    with open(archivo_resultados, mode='r', encoding='utf-8') as f:
        lector = csv.DictReader(f)
        for fila in lector:
            total += 1
            localidad = fila.get('localidad_normalizada', '').lower()
            distrito = fila.get('distrito_normalizado', '').lower()
            provincia = fila.get('provincia_normalizada', '').lower()
            sin_loc = ('no encontrada' in localidad)
            sin_dis = ('no encontrado' in distrito)
            sin_prov = ('no encontrada' in provincia or 'no inferida' in provincia)
            if sin_loc:
                sin_localidad += 1
            if sin_dis:
                sin_distrito += 1
            if sin_prov:
                sin_provincia += 1
            if sin_loc or sin_dis or sin_prov:
                incompletos += 1
    print(f"Total de registros: {total}")
    print(f"Registros sin localidad normalizada: {sin_localidad}")
    print(f"Registros sin distrito normalizado: {sin_distrito}")
    print(f"Registros sin provincia normalizada: {sin_provincia}")
    print(f"Registros con algún dato incompleto: {incompletos}")

if __name__ == "__main__":
    analizar_incompletos('ubicaciones_normalizadas_completo.csv') 