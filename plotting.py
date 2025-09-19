# Contenido para plotting.py

import pandas as pd
import plotly.express as px

def crear_grafico_distribucion(df_mes_actual):
    """
    Genera un gráfico de pie con la distribución de gastos del mes.
    """
    df_gastos = df_mes_actual[df_mes_actual['tipo'] == 'Gasto'].copy()
    if not df_gastos.empty:
        fig = px.pie(
            df_gastos,
            names='categoria',
            values='monto',
            hole=.3,
            title="Distribución de Gastos"
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        return fig
    return None