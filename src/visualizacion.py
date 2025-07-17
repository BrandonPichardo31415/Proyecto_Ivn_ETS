import matplotlib.pyplot as plt
import pandas as pd

def grafico_stock_por_categoria(df):
    fig, ax = plt.subplots()
    df.groupby('Catagory')['Stock_Quantity'].sum().plot(
        kind='bar', title='Stock total por categoría', color='skyblue', ax=ax
    )
    ax.set_ylabel('Cantidad en stock')
    plt.tight_layout()
    return fig

def grafico_ingresos_estimados(df):
    df = df.copy()
    df['Ingresos_Estimados'] = df['Unit_Price'] * df['Sales_Volume']
    top_ingresos = df.sort_values(by='Ingresos_Estimados', ascending=False).head(10)
    fig, ax = plt.subplots()
    top_ingresos.plot(x='Product_Name', y='Ingresos_Estimados', kind='barh', legend=False, color='green', ax=ax)
    ax.set_title('Top 10 productos por ingresos estimados')
    ax.set_xlabel('Ingresos ($)')
    plt.tight_layout()
    return fig

def grafico_productos_mas_vendidos(df):
    top_ventas = df.sort_values(by='Sales_Volume', ascending=False).head(10)
    fig, ax = plt.subplots()
    top_ventas.plot(x='Product_Name', y='Sales_Volume', kind='bar', legend=False, color='orange', ax=ax)
    ax.set_title('Top 10 productos más vendidos')
    ax.set_ylabel('Unidades vendidas')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    return fig

def grafico_productos_por_vencer(df):
    df = df.copy()
    df['Expiration_Date'] = pd.to_datetime(df['Expiration_Date'], errors='coerce')
    df = df[df['Expiration_Date'].notna()]
    df = df[df['Expiration_Date'] >= pd.Timestamp.now()]
    df['Dias_para_vencer'] = (df['Expiration_Date'] - pd.Timestamp.now()).dt.days
    df = df.sort_values(by='Dias_para_vencer').head(10)

    if df.empty:
        return None

    fig, ax = plt.subplots()
    df.plot(x='Product_Name', y='Dias_para_vencer', kind='barh', legend=False, color='red', ax=ax)
    ax.set_title('Productos más cercanos a vencer')
    ax.set_xlabel('Días restantes')
    plt.tight_layout()
    return fig