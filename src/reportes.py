# Genera un reporte basico por categoria en el cual se especifican ventas e Inventory Turnover Rate
# Nota: Inventory Turnover Rate es una medida de cuantas veces se cambia el inventario por completo
def reporte_rotacion_categoria(df):
    return df.groupby('Catagory').agg({
        'Sales_Volume': 'sum',
        'Inventory_Turnover_Rate': 'mean'
    }).reset_index()