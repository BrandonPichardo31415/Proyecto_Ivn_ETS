import streamlit as st
import os
import json

from visualizacion import *
from cargar_datos import cargar_dataset
from simulacion import simular_demanda
from recomendaciones import *
from prediccion import predecir_demanda
from caducidad import *

st.set_page_config(page_title="Gestión Inteligente de Almacén", layout="wide")

# ------------- Inicio de sesión --------------
st.sidebar.header("Inicio de sesión")
usuario = st.sidebar.text_input("Usuario")
clave = st.sidebar.text_input("Contraseña", type="password")

# Ruta absoluta del archivo de usuarios
base_dir = os.path.dirname(os.path.abspath(__file__))

# Construye la ruta completa al archivo CSV
ruta_usuarios = os.path.join(base_dir, "..", "data", "usuarios.json")

# Cargar datos de usuarios
if os.path.exists(ruta_usuarios):
    with open(ruta_usuarios, "r", encoding="utf-8") as f:
        usuarios_data = json.load(f)
else:
    usuarios_data = {}

# Función para validar credenciales
def autenticar(usuario, clave):
    return usuario in usuarios_data and usuarios_data[usuario]["clave"] == clave

# Función para obtener rol
def obtener_rol(usuario):
    return usuarios_data[usuario]["rol"] if usuario in usuarios_data else None

if autenticar(usuario, clave):
    rol = obtener_rol(usuario)
    st.sidebar.success(f"Bienvenido, {usuario} ({rol})")
    st.title("Dashboard de Gestión Inteligente de Almacén")

    # Cargar datos
    df = cargar_dataset()

    # ------------- Gráficos iniciales --------------
    st.subheader("📊 Visualizaciones iniciales")

    if rol == "admin" or rol == "operador":
        fig1 = grafico_stock_por_categoria(df)
        if fig1:
            st.pyplot(fig1)

        fig2 = grafico_ingresos_estimados(df)
        if fig2:
            st.pyplot(fig2)

        fig3 = grafico_productos_mas_vendidos(df)
        if fig3:
            st.pyplot(fig3)

        fig4 = grafico_productos_por_vencer(df)
        if fig4:
            st.pyplot(fig4)
        else:
            st.write("No hay productos próximos a vencer para mostrar.")

    # ------------- Promociones para productos próximos a vencer --------------
    if rol == "admin" or rol == "marketing":
        st.subheader("Promociones para Productos Próximos a Vencer")

        dias_caducidad = st.slider("Días para considerar proximidad a caducar", 5, 30, 15)
        min_productos = st.slider("Mínimo productos por promoción", 2, 5, 2)
        max_productos = st.slider("Máximo productos por promoción", min_productos, 5, 3)

        df_promociones = generar_promociones_caducidad(
            df,
            dias=dias_caducidad,
            min_productos=min_productos,
            max_productos=max_productos,
            ruta_salida=None
        )

        if df_promociones is not None and not df_promociones.empty:
            st.dataframe(df_promociones)
        else:
            st.write("No hay promociones generadas para productos próximos a vencer.")

    # ------------- Recomendaciones de reabastecimiento --------------
    if rol == "admin" or rol == "almacen":
        st.subheader("Recomendaciones de Reabastecimiento")
        recomendaciones = recomendaciones_reabastecimiento(df)
        if recomendaciones is not None and not recomendaciones.empty:
            st.dataframe(recomendaciones)
        else:
            st.write("No hay recomendaciones de reabastecimiento disponibles.")

    # ------------- Simulación de aumento de demanda --------------
    if rol == "admin" or rol == "operador":
        st.subheader("Simulación de Aumento de Demanda")
        porcentaje_simulacion = st.slider("Aumento de demanda (%)", 0, 100, 20)
        resultado_simulacion = simular_demanda(df, aumento_porcentual=porcentaje_simulacion)
        if resultado_simulacion is not None and not resultado_simulacion.empty:
            st.dataframe(resultado_simulacion)
        else:
            st.write("No hay datos para la simulación.")

    # ------------- Predicciones ARIMA --------------
    if rol == "admin" or rol == "analista":
        st.subheader("Predicción ARIMA")

        producto_seleccionado = st.selectbox("Selecciona un producto para predicción:", df['Catagory'].unique())
        df_producto = df[df['Catagory'] == producto_seleccionado]

        st.markdown("**Predicción de ventas**")
        fig_ventas, df_pred_ventas = predecir_demanda(df_producto, columna_agrupacion='Catagory', target_column='Sales_Volume')
        if fig_ventas is not None:
            st.pyplot(fig_ventas)
        if df_pred_ventas is not None and not df_pred_ventas.empty:
            with st.expander("Ver predicción de ventas"):
                st.dataframe(df_pred_ventas)

        st.markdown("**Predicción de inventario**")
        fig_inventario, df_pred_inventario = predecir_demanda(df_producto, columna_agrupacion='Catagory', target_column='Stock_Quantity')
        if fig_inventario is not None:
            st.pyplot(fig_inventario)
        if df_pred_inventario is not None and not df_pred_inventario.empty:
            with st.expander("Ver predicción de inventario"):
                st.dataframe(df_pred_inventario)

        # ------------- Propuesta de Recompra Automática --------------
        st.subheader("Propuesta de Recompra Automática")

        if st.button("Generar alertas y propuesta de recompra"):
            alertas = generar_alertas_demanda_vs_inventario(
                df_pred_ventas=df_pred_ventas,
                df_pred_inventario=df_pred_inventario,
                columna_agrupacion='Catagory'
            )

            if not alertas.empty:
                df_recompra = generar_propuesta_recompra(df, alertas)
                st.success("Alertas y propuesta de recompra generadas")
                st.dataframe(alertas)

                if not df_recompra.empty:
                    with st.expander("Ver propuesta de recompra"):
                        st.dataframe(df_recompra)
                else:
                    st.write("No se requiere recompras urgentes según las predicciones.")
            else:
                st.warning("No se pudieron generar alertas.")

    # ------------- Datos completos de inventario al final --------------
    if rol == "admin":
        st.subheader("Datos completos del inventario y venta")
        st.dataframe(df)

else:
    st.sidebar.warning("Credenciales incorrectas o no registradas.")
