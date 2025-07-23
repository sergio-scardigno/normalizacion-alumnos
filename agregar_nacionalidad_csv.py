import pandas as pd
import re
import unicodedata

def limpiar_texto(texto):
    """Limpia texto removiendo espacios extras y caracteres raros, y convierte a minúsculas"""
    if pd.isna(texto) or texto == '':
        return ''
    
    # Convertir a string por si acaso
    texto = str(texto)
    
    # Remover espacios al inicio y final
    texto = texto.strip()
    
    # Normalizar caracteres unicode (convierte acentos a caracteres base)
    texto = unicodedata.normalize('NFKD', texto)
    
    # Remover caracteres no alfanuméricos excepto espacios y guiones
    texto = re.sub(r'[^\w\s-]', '', texto)
    
    # Convertir múltiples espacios en uno solo
    texto = re.sub(r'\s+', ' ', texto)
    
    # Convertir a minúsculas
    texto = texto.lower()
    
    return texto

def crear_diccionario_paises():
    """Crea un diccionario con códigos de países usando las 2 primeras letras del nombre"""
    # Lista de nombres de países (base)
    nombres_paises_base = [
        'argentina', 'uruguay', 'brasil', 'chile', 'peru', 'bolivia', 'paraguay', 
        'ecuador', 'colombia', 'venezuela', 'estados unidos', 'canada', 'mexico',
        'españa', 'francia', 'italia', 'alemania', 'reino unido', 'china', 'japon',
        'india', 'rusia', 'australia', 'sudafrica', 'egipto', 'marruecos', 'nigeria',
        'kenia', 'ghana', 'etiopia', 'argelia', 'tunez', 'libia', 'sudan', 'angola',
        'mozambique', 'zambia', 'zimbabue', 'botsuana', 'namibia', 'esuatini', 'lesoto',
        'malaui', 'madagascar', 'mauricio', 'seychelles', 'comoras', 'yibuti', 'somalia',
        'eritrea', 'republica centroafricana', 'chad', 'camerun', 'gabon', 'guinea ecuatorial',
        'santo tome y principe', 'cabo verde', 'guinea-bisau', 'guinea', 'sierra leona',
        'liberia', 'costa de marfil', 'burkina faso', 'mali', 'niger', 'senegal',
        'gambia', 'mauritania', 'sahara occidental', 'corea del sur', 'corea del norte',
        'mongolia', 'kazajistan', 'kirguistan', 'tayikistan', 'turkmenistan', 'uzbekistan',
        'afganistan', 'pakistan', 'bangladesh', 'butan', 'nepal', 'sri lanka', 'maldivas',
        'tailandia', 'birmania', 'laos', 'camboya', 'vietnam', 'malasia', 'singapur',
        'brunei', 'indonesia', 'timor oriental', 'filipinas', 'taiwan', 'hong kong',
        'macao', 'nueva zelanda', 'fiyi', 'papua nueva guinea', 'islas salomon', 'vanuatu',
        'nueva caledonia', 'polinesia francesa', 'samoa', 'tonga', 'kiribati', 'tuvalu',
        'nauru', 'palaos', 'micronesia', 'islas marshall', 'guam', 'islas marianas del norte',
        'samoa americana', 'islas cook', 'niue', 'tokelau', 'wallis y futuna', 'pitcairn',
        'noruega', 'suecia', 'finlandia', 'dinamarca', 'islandia', 'irlanda', 'paises bajos',
        'belgica', 'luxemburgo', 'suiza', 'austria', 'liechtenstein', 'monaco', 'andorra',
        'san marino', 'vaticano', 'malta', 'chipre', 'grecia', 'albania', 'macedonia del norte',
        'bulgaria', 'rumania', 'moldavia', 'ucrania', 'bielorrusia', 'lituania', 'letonia',
        'estonia', 'polonia', 'republica checa', 'eslovaquia', 'hungria', 'eslovenia',
        'croacia', 'bosnia y herzegovina', 'serbia', 'montenegro', 'kosovo', 'portugal',
        'turquia', 'georgia', 'armenia', 'azerbaiyan', 'iran', 'irak', 'siria', 'libano',
        'jordania', 'israel', 'palestina', 'arabia saudi', 'yemen', 'oman', 'emiratos arabes unidos',
        'catar', 'bahrein', 'kuwait', 'guatemala', 'belice', 'el salvador', 'honduras',
        'nicaragua', 'costa rica', 'panama', 'cuba', 'jamaica', 'haiti', 'republica dominicana',
        'puerto rico', 'trinidad y tobago', 'barbados', 'granada', 'san vicente y las granadinas',
        'santa lucia', 'dominica', 'antigua y barbuda', 'san cristobal y nieves', 'bahamas',
        'islas virgenes britanicas', 'islas virgenes estadounidenses', 'islas caiman',
        'islas turcas y caicos', 'anguila', 'montserrat', 'guadalupe', 'martinica',
        'san bartolome', 'san martin', 'sint maarten', 'curazao', 'aruba', 'bonaire',
        'surinam', 'guyana', 'guayana francesa'
    ]
    
    # Crear diccionario con códigos de 2 letras basados en las primeras 2 letras del nombre
    paises = {}
    nombres_a_codigos = {}
    
    for nombre in nombres_paises_base:
        # Generar código de 2 letras con las primeras 2 letras del nombre
        codigo = nombre[:2].lower()
        paises[codigo] = nombre
        nombres_a_codigos[nombre] = codigo
        
        # Agregar variaciones comunes para países específicos
        if nombre == 'argentina':
            nombres_a_codigos['argentino'] = codigo
            nombres_a_codigos['argentinos'] = codigo
            nombres_a_codigos['argentina'] = codigo
            nombres_a_codigos['argentinas'] = codigo
        elif nombre == 'brasil':
            nombres_a_codigos['brasileno'] = codigo
            nombres_a_codigos['brasilena'] = codigo
            nombres_a_codigos['brasilenos'] = codigo
            nombres_a_codigos['brasilenas'] = codigo
            nombres_a_codigos['brasilero'] = codigo
            nombres_a_codigos['brasilera'] = codigo
            nombres_a_codigos['brasileros'] = codigo
            nombres_a_codigos['brasileras'] = codigo
        elif nombre == 'uruguay':
            nombres_a_codigos['uruguayo'] = codigo
            nombres_a_codigos['uruguaya'] = codigo
            nombres_a_codigos['uruguayos'] = codigo
            nombres_a_codigos['uruguayas'] = codigo
        elif nombre == 'chile':
            nombres_a_codigos['chileno'] = codigo
            nombres_a_codigos['chilena'] = codigo
            nombres_a_codigos['chilenos'] = codigo
            nombres_a_codigos['chilenas'] = codigo
        elif nombre == 'peru':
            nombres_a_codigos['peruano'] = codigo
            nombres_a_codigos['peruana'] = codigo
            nombres_a_codigos['peruanos'] = codigo
            nombres_a_codigos['peruanas'] = codigo
        elif nombre == 'bolivia':
            nombres_a_codigos['boliviano'] = codigo
            nombres_a_codigos['boliviana'] = codigo
            nombres_a_codigos['bolivianos'] = codigo
            nombres_a_codigos['bolivianas'] = codigo
        elif nombre == 'paraguay':
            nombres_a_codigos['paraguayo'] = codigo
            nombres_a_codigos['paraguaya'] = codigo
            nombres_a_codigos['paraguayos'] = codigo
            nombres_a_codigos['paraguayas'] = codigo
        elif nombre == 'colombia':
            nombres_a_codigos['colombiano'] = codigo
            nombres_a_codigos['colombiana'] = codigo
            nombres_a_codigos['colombianos'] = codigo
            nombres_a_codigos['colombianas'] = codigo
        elif nombre == 'venezuela':
            nombres_a_codigos['venezolano'] = codigo
            nombres_a_codigos['venezolana'] = codigo
            nombres_a_codigos['venezolanos'] = codigo
            nombres_a_codigos['venezolanas'] = codigo
        elif nombre == 'ecuador':
            nombres_a_codigos['ecuatoriano'] = codigo
            nombres_a_codigos['ecuatoriana'] = codigo
            nombres_a_codigos['ecuatorianos'] = codigo
            nombres_a_codigos['ecuatorianas'] = codigo
    
    return paises, nombres_a_codigos

def normalizar_nacionalidad(nacionalidad_limpia, nombres_a_codigos, paises):
    """Convierte nacionalidad a código de 2 letras solo si coincide exactamente con el nombre del país"""
    if not nacionalidad_limpia or nacionalidad_limpia == '':
        return ''
    
    # Buscar coincidencia exacta en el diccionario de nombres de países
    if nacionalidad_limpia in nombres_a_codigos:
        return nombres_a_codigos[nacionalidad_limpia]
    
    # Si no encuentra coincidencia exacta, devolver vacío o la nacionalidad original
    # Puedes cambiar esto según prefieras
    return ''  # o return nacionalidad_limpia si prefieres mantener el texto original

def procesar_csv(archivo_entrada, archivo_salida=None):
    """Procesa el archivo CSV agregando las columnas solicitadas"""
    
    # Leer el CSV
    print("Leyendo archivo CSV...")
    df = pd.read_csv(archivo_entrada, low_memory=False)
    
    print(f"Archivo leído. Filas: {len(df)}, Columnas: {len(df.columns)}")
    
    # Verificar que existe la columna nacionalidad
    if 'nacionalidad' not in df.columns:
        print("Error: No se encontró la columna 'nacionalidad' en el CSV")
        print("Columnas disponibles:", list(df.columns))
        return
    
    # Crear diccionarios de países
    paises, nombres_a_codigos = crear_diccionario_paises()
    
    # Limpiar la columna nacionalidad
    print("Limpiando columna de nacionalidad...")
    df['nacionalidad_limpia'] = df['nacionalidad'].apply(limpiar_texto)
    
    # Normalizar nacionalidades a códigos de 2 letras
    print("Normalizando nacionalidades...")
    df['nacionalidad_normalizada'] = df['nacionalidad_limpia'].apply(
        lambda x: normalizar_nacionalidad(x, nombres_a_codigos, paises)
    )
    
    # Agregar columna es_argentino
    print("Agregando columna es_argentino...")
    df['es_argentino'] = df['nacionalidad_normalizada'] == 'ar'
    
    # Estadísticas
    print("\n=== ESTADÍSTICAS ===")
    print(f"Total de registros: {len(df)}")
    print(f"Registros con nacionalidad: {len(df[df['nacionalidad_limpia'] != ''])}")
    print(f"Registros argentinos: {len(df[df['es_argentino'] == True])}")
    print(f"Registros no argentinos: {len(df[df['es_argentino'] == False])}")
    
    print("\nTop 10 nacionalidades más comunes:")
    print(df['nacionalidad_normalizada'].value_counts().head(10))
    
    print("\nEjemplos de nacionalidades originales vs normalizadas:")
    ejemplos = df[['nacionalidad', 'nacionalidad_limpia', 'nacionalidad_normalizada', 'es_argentino']].drop_duplicates().head(10)
    for _, row in ejemplos.iterrows():
        if row['nacionalidad_limpia'] != '':
            print(f"'{row['nacionalidad']}' -> '{row['nacionalidad_limpia']}' -> '{row['nacionalidad_normalizada']}' -> Argentino: {row['es_argentino']}")
    
    # Guardar el archivo
    if archivo_salida is None:
        archivo_salida = archivo_entrada.replace('.csv', '_con_nacionalidad_normalizada.csv')
    
    print(f"\nGuardando archivo procesado como: {archivo_salida}")
    df.to_csv(archivo_salida, index=False)
    
    print("¡Proceso completado!")
    return df

# Ejemplo de uso
if __name__ == "__main__":
    # Cambiar por la ruta de tu archivo
    archivo_csv = "alumnos/fp_alumnos.csv"  # Reemplazar con el nombre de tu archivo
    
    # Procesar el archivo
    df_procesado = procesar_csv(archivo_csv)
    
    # Mostrar algunas filas para verificar
    if df_procesado is not None:
        print("\nPrimeras 5 filas con las nuevas columnas:")
        columnas_mostrar = ['nacionalidad', 'nacionalidad_limpia', 'nacionalidad_normalizada', 'es_argentino']
        print(df_procesado[columnas_mostrar].head())