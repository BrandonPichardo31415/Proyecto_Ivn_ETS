import pandas as pd
import os

# Lee los datos desde el dataset de muestra
def cargar_dataset():
    # Obtiene el directorio donde está este archivo .py
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Construye la ruta completa al archivo CSV
    ruta = os.path.join(base_dir, "..", "data", "Grocery_Inventory_and_Sales_Dataset.csv")

    # Carga el CSV con las fechas parseadas y limpia el precio
    df = pd.read_csv(ruta, parse_dates=['Date_Received', 'Last_Order_Date', 'Expiration_Date'])
    df['Unit_Price'] = df['Unit_Price'].replace('[\$,]', '', regex=True).astype(float)
    return df
