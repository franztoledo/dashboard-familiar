# Contenido para core_logic.py

import pandas as pd
from io import BytesIO
from datetime import datetime

# --- NUEVA FUNCIÓN ---
def calcular_saldo_disponible(df_total):
    """Calcula el balance total histórico (ingresos - gastos)."""
    ingresos_totales = df_total[df_total['tipo'] == 'Ingreso']['monto'].sum()
    gastos_totales = df_total[df_total['tipo'] == 'Gasto']['monto'].sum()
    return ingresos_totales - gastos_totales

def detectar_gastos_anomalos(df_mes_seleccionado):
    """Detecta gastos anómalos para el mes seleccionado."""
    df_gastos = df_mes_seleccionado[df_mes_seleccionado['tipo'] == 'Gasto'].copy()
    if len(df_gastos) < 5:
        return pd.DataFrame()
    stats_categoria = df_gastos.groupby('categoria')['monto'].agg(['mean', 'std']).fillna(0)
    anomalias = []
    for index, row in df_gastos.iterrows():
        categoria = row['categoria']
        if categoria in stats_categoria.index:
            media = stats_categoria.loc[categoria]['mean']
            std = stats_categoria.loc[categoria]['std']
            if std > 0 and row['monto'] > media + 1.5 * std:
                anomalias.append(row)
    return pd.DataFrame(anomalias)

# --- FUNCIÓN MODIFICADA ---
def calcular_kpis(df_total, presupuesto, meta_ahorro, anio_seleccionado, mes_seleccionado):
    """
    Calcula todos los KPIs para un mes y año específicos.
    """
    # Filtrar transacciones para el mes seleccionado
    df_mes_seleccionado = df_total[
        (df_total['fecha'].dt.month == mes_seleccionado) & 
        (df_total['fecha'].dt.year == anio_seleccionado)
    ]
    
    # Datos del mes anterior para comparación
    fecha_mes_anterior = (datetime(anio_seleccionado, mes_seleccionado, 1) - pd.DateOffset(days=1))
    df_mes_anterior = df_total[
        (df_total['fecha'].dt.month == fecha_mes_anterior.month) & 
        (df_total['fecha'].dt.year == fecha_mes_anterior.year)
    ]

    ingresos_actual = df_mes_seleccionado[df_mes_seleccionado['tipo'] == 'Ingreso']['monto'].sum()
    gastos_actual = df_mes_seleccionado[df_mes_seleccionado['tipo'] == 'Gasto']['monto'].sum()
    ahorro_actual = ingresos_actual - gastos_actual
    
    ahorro_anterior = df_mes_anterior[df_mes_anterior['tipo'] == 'Ingreso']['monto'].sum() - df_mes_anterior[df_mes_anterior['tipo'] == 'Gasto']['monto'].sum()

    porcentaje_gastado = (gastos_actual / presupuesto) * 100 if presupuesto > 0 else 0
    porcentaje_meta = (ahorro_actual / meta_ahorro) * 100 if meta_ahorro > 0 else 0
    
    if ahorro_anterior != 0:
        variacion_ahorro = ((ahorro_actual - ahorro_anterior) / abs(ahorro_anterior)) * 100
    else:
        variacion_ahorro = 100.0 if ahorro_actual > 0 else 0.0

    df_anomalias = detectar_gastos_anomalos(df_mes_seleccionado)
    
    # La proyección solo tiene sentido para el mes actual
    hoy = datetime.now()
    proyeccion_ahorro = 0
    if anio_seleccionado == hoy.year and mes_seleccionado == hoy.month:
        dias_transcurridos = hoy.day
        dias_en_mes = pd.Period(f'{hoy.year}-{hoy.month}').days_in_month
        proyeccion_ahorro = (ahorro_actual / dias_transcurridos) * dias_en_mes if dias_transcurridos > 0 else 0
        
    return {
        "df_mes_seleccionado": df_mes_seleccionado, "gastado_hoy": gastos_actual,
        "porcentaje_gastado": porcentaje_gastado, "ahorro_actual": ahorro_actual,
        "porcentaje_meta_alcanzado": porcentaje_meta, "conteo_anomalias": len(df_anomalias),
        "df_anomalias": df_anomalias, "variacion_ahorro_anterior": variacion_ahorro,
        "proyeccion_ahorro": proyeccion_ahorro
    }

def exportar_a_excel(df):
    """Convierte un DataFrame a un archivo Excel en memoria para su descarga."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Transacciones')
    return output.getvalue()