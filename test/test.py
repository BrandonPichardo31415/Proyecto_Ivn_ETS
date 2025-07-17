import sys
import os

# Agregar src al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# Importaciones desde src
from cargar_datos import *
from inventario import *
from caducidad import *
from reportes import *
from recomendaciones import *
from simulacion import simular_demanda
from exportar import exportar_csv, exportar_excel
from visualizacion import (
    grafico_stock_por_categoria,
    grafico_ingresos_estimados,
    grafico_productos_mas_vendidos,
    grafico_productos_por_vencer
)
from prediccion import *


def test_componentes():
    print("📦 Cargando dataset...")
    df = cargar_dataset()

    # ---------------- INVENTARIO ----------------
    print("\n🔎 Productos bajo stock:")
    bajo_stock = productos_bajo_stock(df)
    print(bajo_stock)

    print("\n🔎 Productos sobreinventario:")
    sobre_stock = productos_sobreinventario(df)
    print(sobre_stock)

    print("\n💰 Ingresos estimados por producto:")
    print(ingresos_estimados(df))

    # ---------------- CADUCIDAD ----------------
    print("\n⏳ Productos próximos a vencer (15 días):")
    por_vencer = productos_proximo_vencer(df, dias=15)
    print(por_vencer)

    print("\n🎯 Generando promociones por caducidad...")
    promociones = generar_promociones_caducidad(
        df,
        dias=15,
        min_productos=2,
        max_productos=3,
        ruta_salida='data/promociones_caducidad.csv'
    )
    print(promociones)

    # ---------------- REPORTES ----------------
    print("\n📊 Reporte de rotación por categoría:")
    print(reporte_rotacion_categoria(df))

    # ---------------- RECOMENDACIONES ----------------
    print("\n🛒 Recomendaciones de reabastecimiento:")
    print(recomendaciones_reabastecimiento(df))

    # ---------------- SIMULACIÓN ----------------
    print("\n📈 Simulación de aumento de demanda (20%):")
    print(simular_demanda(df))

    # ---------------- PREDICCIÓN ----------------
    print("\n📉 Ejecutando predicciones de demanda y stock:")
    predecir_demanda(df, target_column='Sales_Volume')
    predecir_demanda(df, target_column='Stock_Quantity')

    print("\n⚠️ Generando alertas por demanda vs inventario...")
    alertas = generar_alertas_demanda_vs_inventario()

    if alertas is not None:
        print("⚠️ Alertas encontradas:")
        print(alertas)
        print("\n📋 Generando propuesta de recompra...")
        generar_propuesta_recompra(df, alertas)
    else:
        print("✅ Sin alertas. No se generó propuesta de recompra.")

    # ---------------- EXPORTAR ----------------
    print("\n💾 Exportando reportes de ejemplo...")
    exportar_csv(bajo_stock, 'data/bajo_stock.csv')
    exportar_excel(por_vencer, 'data/productos_por_vencer.xlsx')

    # ---------------- VISUALIZACIÓN ----------------
    print("\n📊 Mostrando visualizaciones...")
    grafico_stock_por_categoria(df)
    grafico_ingresos_estimados(df)
    grafico_productos_mas_vendidos(df)
    grafico_productos_por_vencer(df)


if __name__ == "__main__":
    test_componentes()

  