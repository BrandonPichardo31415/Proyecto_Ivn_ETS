from datetime import datetime, timedelta
import pandas as pd
from itertools import combinations
import os

# Retorna los productos cuya fecha de caducidad esté entre hoy y un límite de días definidos
def productos_proximo_vencer(df, dias=15):
    hoy = pd.Timestamp(datetime.now().date())
    limite = hoy + timedelta(days=dias)
    
    # Convertir a fecha si no lo es ya
    df['Expiration_Date'] = pd.to_datetime(df['Expiration_Date'], errors='coerce')

    # Filtrar productos con fecha válida y dentro del rango
    proximos = df[
        (df['Expiration_Date'].notna()) &
        (df['Expiration_Date'] >= hoy) & 
        (df['Expiration_Date'] <= limite) &
        (df['Stock_Quantity'] > 0)
    ][['Product_ID', 'Product_Name', 'Catagory', 'Expiration_Date', 'Stock_Quantity']]

    return proximos


import os
import pandas as pd
from itertools import combinations

def generar_promociones_caducidad(df, dias=15, min_productos=2, max_productos=3, ruta_salida='data/promociones_caducidad.csv'):
    proximos = productos_proximo_vencer(df, dias)
    promociones = []

    # Agrupar por categoría para mantener coherencia en la promoción
    for categoria, grupo in proximos.groupby('Catagory'):
        productos = grupo.to_dict('records')

        # Generar combinaciones de productos en la misma categoría
        for r in range(min_productos, max_productos + 1):
            for combo in combinations(productos, r):
                total_stock = sum(p['Stock_Quantity'] for p in combo)
                productos_ids = [p['Product_ID'] for p in combo]
                productos_nombres = [p['Product_Name'] for p in combo]
                fechas = [p['Expiration_Date'] for p in combo]

                promociones.append({
                    'Categoria': categoria,
                    'Productos_ID': ', '.join(productos_ids),
                    'Productos_Nombres': ' + '.join(productos_nombres),
                    'Stock_Total': total_stock,
                    'Fecha_Caducidad_Mas_Cercana': min(fechas)
                })

    df_promos = pd.DataFrame(promociones)

    # Guardar solo si ruta_salida es una cadena no vacía
    if ruta_salida is not None and isinstance(ruta_salida, str) and len(df_promos) > 0:
        carpeta = os.path.dirname(ruta_salida)
        if carpeta and not os.path.exists(carpeta):
            os.makedirs(carpeta)
        df_promos.to_csv(ruta_salida, index=False)
        print(f"Promociones por caducidad generadas en {ruta_salida}")
    else:
        if len(df_promos) == 0:
            print("No hay productos cercanos a caducar para generar promociones.")
        else:
            print("No se guardó el archivo porque ruta_salida no fue especificada.")

    return df_promos
