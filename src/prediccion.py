import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
import warnings
import matplotlib.cm as cm
import os  

warnings.filterwarnings("ignore")

import matplotlib.pyplot as plt
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import matplotlib.cm as cm

def predecir_demanda(
    df,
    columna_agrupacion='Catagory',
    target_column='Stock_Quantity',
    meses_reales=6,
    meses_prediccion=3
):
    if columna_agrupacion not in df.columns:
        raise ValueError(f"La columna '{columna_agrupacion}' no existe en el DataFrame.")
    if target_column not in df.columns:
        raise ValueError(f"La columna '{target_column}' no existe en el DataFrame.")

    df['Last_Order_Date'] = pd.to_datetime(df['Last_Order_Date'], errors='coerce')
    df = df.dropna(subset=['Last_Order_Date'])

    grupos = df[columna_agrupacion].dropna().unique()
    predicciones_total = []

    fig, ax = plt.subplots(figsize=(12, 6))

    colores = cm.get_cmap('tab20', len(grupos))
    color_map = {grupo: colores(i) for i, grupo in enumerate(grupos)}

    for grupo in grupos:
        subset = df[df[columna_agrupacion] == grupo].copy()

        if subset[target_column].sum() < 10:
            continue

        niveles_mensuales = (
            subset.groupby(subset['Last_Order_Date'].dt.to_period('M'))[target_column]
            .sum()
            .sort_index()
        )
        niveles_mensuales = niveles_mensuales[niveles_mensuales > 0]
        niveles_mensuales.index = niveles_mensuales.index.to_timestamp()

        if len(niveles_mensuales) < meses_reales:
            continue

        try:
            modelo = ARIMA(niveles_mensuales, order=(1, 1, 1))
            modelo_entrenado = modelo.fit()

            ultimos_reales = niveles_mensuales.iloc[-meses_reales:]

            pred = modelo_entrenado.forecast(steps=meses_prediccion)
            pred.index = pd.date_range(
                start=ultimos_reales.index[-1] + pd.offsets.MonthBegin(1),
                periods=meses_prediccion,
                freq='MS'
            )

            df_pred = pd.DataFrame({
                'Fecha': list(ultimos_reales.index) + list(pred.index),
                target_column: list(ultimos_reales.values) + list(pred.values),
                'Tipo': ['Real'] * len(ultimos_reales) + ['Predicción'] * len(pred),
                columna_agrupacion: grupo
            })

            predicciones_total.append(df_pred)

            color = color_map[grupo]

            ax.plot(
                ultimos_reales.index,
                ultimos_reales.values,
                label=f"{grupo} - Real",
                color=color,
                linestyle='-',
                marker='o'
            )
            ax.plot(
                pred.index,
                pred.values,
                label=f"{grupo} - Predicción",
                color=color,
                linestyle='--',
                marker='x'
            )

        except Exception as e:
            print(f"Error con grupo '{grupo}': {e}")
            continue

    if predicciones_total:
        df_final = pd.concat(predicciones_total, ignore_index=True)
    else:
        df_final = pd.DataFrame()  # DataFrame vacío si no hay predicciones

    ax.set_title(f"Niveles de {target_column} reales y predicción por {columna_agrupacion}")
    ax.set_xlabel("Fecha")
    ax.set_ylabel(target_column)
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(True)
    plt.tight_layout()

    return fig, df_final

