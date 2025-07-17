import pandas as pd
from prediccion import *

# Genera un reporte basico con recomendaciones para recomprar
# Las reomendacines incluyen bajo nivel de inventario, alta demanda y caducidad 
def recomendaciones_reabastecimiento(df):
    df = df.copy()

    # Asegurar que la columna Expiration_Date esté en formato datetime
    df['Expiration_Date'] = pd.to_datetime(df['Expiration_Date'], errors='coerce')

    # Calcular los días para caducidad (ignorando fechas inválidas)
    df['Dias_Caducidad'] = (df['Expiration_Date'] - pd.Timestamp.now()).dt.days

    # Filtro de productos que cumplen con las condiciones para reabastecerse
    recomendaciones = df[
        (df['Stock_Quantity'] < df['Reorder_Level']) &
        (df['Inventory_Turnover_Rate'] > 20) &
        (df['Dias_Caducidad'] > 15)
    ]

    # Devolver columnas clave para reabastecimiento
    return recomendaciones[[
        'Product_ID', 'Product_Name', 'Stock_Quantity', 'Reorder_Level', 'Dias_Caducidad'
    ]]

def generar_alertas_demanda_vs_inventario(
    df_pred_ventas,
    df_pred_inventario,
    columna_agrupacion='Catagory',
    umbral_reabastecimiento=1.1,
    umbral_sobreinventario=0.7
):
    """
    Compara la demanda estimada vs el inventario estimado y genera alertas por categoría.
    """
    if df_pred_ventas is None or df_pred_ventas.empty:
        print("El DataFrame de predicción de ventas está vacío.")
        return pd.DataFrame()

    if df_pred_inventario is None or df_pred_inventario.empty:
        print("El DataFrame de predicción de inventario está vacío.")
        return pd.DataFrame()

    # Validar columnas
    for df, nombre, columna in [
        (df_pred_ventas, "ventas", 'Sales_Volume'),
        (df_pred_inventario, "inventario", 'Stock_Quantity'),
    ]:
        if columna_agrupacion not in df.columns:
            raise ValueError(f"La columna '{columna_agrupacion}' no está en el DataFrame de {nombre}.")
        if columna not in df.columns:
            raise ValueError(f"La columna '{columna}' no está en el DataFrame de {nombre}.")

    # Filtrar predicciones solamente
    ventas_pred = df_pred_ventas[df_pred_ventas['Tipo'] == 'Predicción']
    inv_pred = df_pred_inventario[df_pred_inventario['Tipo'] == 'Predicción']

    # Agrupar por categoría
    demanda_promedio = ventas_pred.groupby(columna_agrupacion)['Sales_Volume'].mean()
    inventario_promedio = inv_pred.groupby(columna_agrupacion)['Stock_Quantity'].mean()

    comparacion = pd.DataFrame({
        'Demanda_Promedio': demanda_promedio,
        'Inventario_Promedio': inventario_promedio
    })

    comparacion['Alerta'] = 'Inventario adecuado'

    for idx, row in comparacion.iterrows():
        demanda = row['Demanda_Promedio']
        inventario = row['Inventario_Promedio']

        if pd.isna(demanda) or pd.isna(inventario):
            comparacion.at[idx, 'Alerta'] = 'Datos insuficientes'
        elif demanda > inventario * umbral_reabastecimiento:
            comparacion.at[idx, 'Alerta'] = 'Reabastecimiento urgente: demanda alta'
        elif inventario > demanda / umbral_sobreinventario:
            comparacion.at[idx, 'Alerta'] = 'Sobreinventario: disminuir compras o promover ventas'

    return comparacion

def generar_propuesta_recompra(df_original, alertas):
    """
    Genera una propuesta de recompra para categorías con alerta de alta demanda.
    """
    if alertas is None or alertas.empty:
        print("No se proporcionaron alertas válidas.")
        return pd.DataFrame()

    categorias_urgentes = alertas[alertas['Alerta'].str.contains('Reabastecimiento')].index.tolist()

    if not categorias_urgentes:
        print("No hay categorías con alerta de reabastecimiento.")
        return pd.DataFrame()

    df_resultado = []

    for cat in categorias_urgentes:
        subset = df_original[df_original['Catagory'] == cat].copy()
        if subset.empty:
            continue

        subset = subset.sort_values(by='Sales_Volume', ascending=False).head(10)

        if 'Reorder_Quantity' not in subset.columns:
            subset['Reorder_Quantity'] = 10  # Valor por defecto

        resultado = subset[['Product_ID', 'Product_Name', 'Catagory', 'Reorder_Quantity']]
        df_resultado.append(resultado)

    if df_resultado:
        df_final = pd.concat(df_resultado, ignore_index=True)
        return df_final
    else:
        print("No se generó propuesta de recompra.")
        return pd.DataFrame()
