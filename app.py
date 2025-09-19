# Contenido para app.py

import streamlit as st
import pandas as pd
from datetime import datetime

# Importar los módulos con funcionalidades separadas
import database as db
import core_logic
import plotting
import config

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Dashboard Financiero", layout="wide")

# --- DEFINICIÓN DE LAS VISTAS (PÁGINAS) ---

def render_dashboard_page(df_transacciones, presupuesto, meta_ahorro):
    """Muestra el contenido del Dashboard Principal."""
    st.title("Dashboard Financiero General")
    st.markdown("Bienvenido a su centro de control financiero.")

    # Cálculo del Saldo Disponible Total
    st.header("Situación Financiera Global")
    saldo_disponible = core_logic.calcular_saldo_disponible(df_transacciones)
    st.metric(
        "Saldo Disponible Total", 
        f"S/ {saldo_disponible:,.2f}",
        help="Suma de todos los ingresos menos todos los gastos registrados."
    )
    st.markdown("---")

    # Resumen del Mes Actual
    st.header(f"Resumen del Mes Actual ({datetime.now().strftime('%B %Y')})")
    hoy = datetime.now()
    kpis_actuales = core_logic.calcular_kpis(df_transacciones, presupuesto, meta_ahorro, hoy.year, hoy.month)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Gasto Total del Mes", f"S/ {kpis_actuales['gastado_hoy']:,.2f}")
    col2.metric("Ahorro del Mes", f"S/ {kpis_actuales['ahorro_actual']:,.2f}")
    col3.metric("Ahorro vs. Mes Anterior", f"{kpis_actuales['variacion_ahorro_anterior']:.1f}%", delta=f"{kpis_actuales['variacion_ahorro_anterior']:.1f}%")
    col4.metric("Gastos Anómalos", kpis_actuales['conteo_anomalias'])

def render_reporte_page(df_transacciones, presupuesto, meta_ahorro):
    """Muestra el contenido de la página de Reporte Mensual."""
    st.title("Reporte Mensual Detallado")

    # Inicialización y lógica de navegación de meses
    if 'fecha_vista' not in st.session_state:
        st.session_state.fecha_vista = datetime.now()

    fecha_actual = st.session_state.fecha_vista
    meses_espanol = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    mes_seleccionado_nombre = meses_espanol[st.session_state.fecha_vista.month - 1]
    
    col1, col2, col3, col4 = st.columns([1.5, 3, 2, 1.5])
    if col1.button("Mes Anterior"):
        st.session_state.fecha_vista -= pd.DateOffset(months=1)
        st.rerun()
    col2.header(f"{mes_seleccionado_nombre} {st.session_state.fecha_vista.year}")
    if col3.button("Volver al Mes Actual"):
        st.session_state.fecha_vista = datetime.now()
        st.rerun()
    if col4.button("Mes Siguiente"):
        st.session_state.fecha_vista += pd.DateOffset(months=1)
        st.rerun()
    
    st.markdown("---")

    # Calcular KPIs para el período seleccionado
    kpis = core_logic.calcular_kpis(df_transacciones, presupuesto, meta_ahorro, fecha_actual.year, fecha_actual.month)

    # Mostrar KPIs, proyecciones, anomalías y gráficos
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Gasto Total", f"S/ {kpis['gastado_hoy']:,.2f}")
    c2.metric("Ahorro", f"S/ {kpis['ahorro_actual']:,.2f}")
    c3.metric("Ahorro vs. Mes Anterior", f"{kpis['variacion_ahorro_anterior']:.1f}%", delta=f"{kpis['variacion_ahorro_anterior']:.1f}%")
    c4.metric("Gastos Anómalos", kpis['conteo_anomalias'])
    st.markdown("---")
    
    col_proy, col_anom = st.columns(2)
    with col_proy:
        st.subheader("Proyecciones")
        hoy = datetime.now()
        if fecha_actual.year == hoy.year and fecha_actual.month == hoy.month:
            st.info(f"Proyección de ahorro a fin de mes: S/ {kpis['proyeccion_ahorro']:,.2f}")
            if kpis['proyeccion_ahorro'] >= meta_ahorro:
                st.success("Se proyecta que alcanzará su meta de ahorro.")
            else:
                st.warning("A este ritmo, no alcanzará su meta de ahorro.")
        else:
            st.info("Las proyecciones solo están disponibles para el mes actual.")
    
    with col_anom:
        st.subheader("Gastos Anómalos")
        if not kpis['df_anomalias'].empty:
            st.warning(f"Se detectaron {kpis['conteo_anomalias']} gastos inusuales.")
            with st.expander("Mostrar detalles"):
                st.dataframe(kpis['df_anomalias'][['fecha', 'categoria', 'monto', 'descripcion']])
        else:
            st.success("No se detectaron gastos anómalos en este período.")

    st.markdown("---")
    fig_pie = plotting.crear_grafico_distribucion(kpis['df_mes_seleccionado'])
    if fig_pie: 
        st.plotly_chart(fig_pie, use_container_width=True)

    # --- NUEVA SECCIÓN: EXPORTAR REPORTE MENSUAL ---
    st.markdown("---")
    st.header("Exportar Reporte")
    
    df_del_mes = kpis['df_mes_seleccionado']
    if not df_del_mes.empty:
        # Prepara los datos del DataFrame para la descarga
        datos_excel = core_logic.exportar_a_excel(df_del_mes)
        
        # Crea el botón de descarga
        st.download_button(
            label="Descargar Reporte del Mes en Excel",
            data=datos_excel,
            file_name=f"Reporte_{mes_seleccionado_nombre}_{fecha_actual.year}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("No hay datos en este mes para exportar.")


# --- INICIO DE LA APLICACIÓN ---

# 1. Inicializar la base de datos
db.inicializar_db()

# 2. Renderizar la barra lateral y configurar la navegación
st.sidebar.title("Menú Principal")
pagina_seleccionada = st.sidebar.radio(
    "Seleccione una vista",
    ["Dashboard Principal", "Reporte Mensual"]
)
st.sidebar.markdown("---")

# Formularios de la barra lateral
st.sidebar.header("Registrar Transacción")
tipo_transaccion = st.sidebar.selectbox("Tipo de Transacción", ["Gasto", "Ingreso"])
categorias = config.categorias_gasto if tipo_transaccion == "Gasto" else config.categorias_ingreso

with st.sidebar.form("formulario_transaccion", clear_on_submit=True):
    categoria = st.selectbox("Categoría", categorias)
    monto = st.number_input("Monto (S/)", min_value=0.01, format="%.2f")
    fecha = st.date_input("Fecha", datetime.now())
    descripcion = st.text_input("Descripción (Opcional)")
    if st.form_submit_button("Añadir Transacción"):
        db.insertar_transaccion(tipo_transaccion, categoria, monto, fecha.strftime("%Y-%m-%d"), descripcion)
        st.sidebar.success("Transacción registrada.")
        st.rerun()

st.sidebar.header("Configuración Financiera")
presupuesto_actual = db.obtener_configuracion('presupuesto')
meta_ahorro_actual = db.obtener_configuracion('meta_ahorro')

with st.sidebar.form("config_form"):
    presupuesto_mensual = st.number_input("Presupuesto Mensual (S/)", value=presupuesto_actual)
    meta_ahorro_mensual = st.number_input("Meta de Ahorro Mensual (S/)", value=meta_ahorro_actual)
    if st.form_submit_button("Guardar Configuración"):
        db.guardar_configuracion('presupuesto', presupuesto_mensual)
        db.guardar_configuracion('meta_ahorro', meta_ahorro_mensual)
        st.sidebar.success("Configuración actualizada.")
        st.rerun()

# 3. Cargar datos
df_transacciones = db.obtener_transacciones()
if not df_transacciones.empty:
    df_transacciones['fecha'] = pd.to_datetime(df_transacciones['fecha'])

# 4. Mostrar la página seleccionada por el usuario
if pagina_seleccionada == "Dashboard Principal":
    if df_transacciones.empty:
        st.info("No hay transacciones registradas. Utilice el menú para comenzar.")
    else:
        render_dashboard_page(df_transacciones, presupuesto_mensual, meta_ahorro_mensual)
        
elif pagina_seleccionada == "Reporte Mensual":
    if df_transacciones.empty:
        st.info("No hay transacciones registradas para generar un reporte.")
    else:
        render_reporte_page(df_transacciones, presupuesto_mensual, meta_ahorro_mensual)