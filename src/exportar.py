import os

# Ruta absoluta al directorio 'data' dentro del proyecto
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, 'data')

def exportar_csv(df, nombre):
    os.makedirs(DATA_DIR, exist_ok=True)
    # Asegura que solo se tome el nombre del archivo, sin subcarpetas duplicadas
    nombre_archivo = os.path.basename(nombre)
    ruta = os.path.join(DATA_DIR, nombre_archivo)
    df.to_csv(ruta, index=False)

def exportar_excel(df, nombre):
    os.makedirs(DATA_DIR, exist_ok=True)
    nombre_archivo = os.path.basename(nombre)
    ruta = os.path.join(DATA_DIR, nombre_archivo)
    df.to_excel(ruta, index=False)

