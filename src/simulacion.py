# Simula un aumento de 20% en las ventas 
def simular_demanda(df, aumento_porcentual=20):
    df = df.copy()
    df['Demanda_Simulada'] = df['Sales_Volume'] * (1 + aumento_porcentual / 100)
    return df[['Product_ID', 'Product_Name', 'Sales_Volume', 'Demanda_Simulada']]
