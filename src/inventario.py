# Retorna los productos con inventario bajo basandose en el nivel de repedido
def productos_bajo_stock(df):
    return df[df['Stock_Quantity'] < df['Reorder_Level']][
        ['Product_ID', 'Product_Name', 'Stock_Quantity', 'Reorder_Level']
    ]
# Retorna los productos para los cuales el inventario supera en un multiplo el nivel de reorden
# En este caso es el doble, pero puede ajustarse a otro parametro
def productos_sobreinventario(df):
    return df[df['Stock_Quantity'] > 2 * df['Reorder_Level']][
        ['Product_ID', 'Product_Name', 'Stock_Quantity', 'Reorder_Level']
    ]

# Retorna los productos con ingreso estimado, por orden descendente respecto al ingreso estimado
# El ingreso estimado = Precio Unitario * Volumen de venta [piezas]
def ingresos_estimados(df):
    df['Ingresos_Estimados'] = df['Unit_Price'] * df['Sales_Volume']
    return df[['Product_ID', 'Product_Name', 'Ingresos_Estimados']].sort_values(by='Ingresos_Estimados', ascending=False)