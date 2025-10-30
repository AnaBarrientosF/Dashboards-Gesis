import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px


# Configuración de la página
st.set_page_config(page_title="Dashboard Proyectos Gesis", layout="wide")

# CSS para cambiar el color del sidebar y el header
st.markdown("""
    <style>
    
    .stApp {
        background-color: #FBFBFB;
    }
    
    /* Color del texto */
    h1, h2, h3, p, div, span {
        color: black !important;
    }
            
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0B2A85;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    /* Header (barra superior donde está Deploy) */
    [data-testid="stHeader"] {
        background-color: #1043D4;
    }
    [data-testid="stHeader"] * {
        color: white !important;
    }

    
/* Contenedor de métricas */
    
    div[data-testid="stMetric"] {
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin: 5px;
        text-align: center;
    }



    </style>
""", unsafe_allow_html=True)

estado_counts = {
    "Activo": 12,
    "En pausa": 5,
    "En cierre": 3,
    "Finalizado": 8
}


# ==============================
# CARGAR DATOS
# ==============================
#archivo = "Proyectos nacionales\\Base de datos Proyectos.xlsx"
#df = pd.read_excel(archivo, engine="openpyxl")

url = "https://grupoesisgt-my.sharepoint.com/personal/ana_barrientos_grupoesis_com/_layouts/15/download.aspx?share=EQOt_RvJMaVJq4St58tXnFEBglnlksyqfGDbsWJHeIiq8g"
df = pd.read_excel(url, engine="openpyxl")


# Limpiar nombres de columnas
df.columns = df.columns.str.strip()

# Limpiar valores en columnas clave
df['INGENIERO DE IMPLEMENTACION'] = df['INGENIERO DE IMPLEMENTACION'].astype(str).str.strip()
df['ESTADO'] = df['ESTADO'].astype(str).str.strip()
df['ESTADO'] = df['ESTADO'].str.replace(r'\s+', ' ', regex=True)  # eliminar espacios extra

# Convertir fechas
if 'FECHA DE INICIO' in df.columns:
    df['FECHA DE INICIO'] = pd.to_datetime(df['FECHA DE INICIO'], format='%d-%m-%y', errors='coerce').dt.strftime('%d-%m-%Y')
if 'FECHA DE FINALIZACION' in df.columns:
    df['FECHA DE FINALIZACION'] = pd.to_datetime(df['FECHA DE FINALIZACION'], format='%d-%m-%y', errors='coerce').dt.strftime('%d-%m-%Y')
    

# Sidebar
# Imagen en el sidebar

st.sidebar.image("logo.jpeg", width=110)
st.sidebar.title("Dashboard")
menu = st.sidebar.radio("Menú", ["Inicio", "Proyectos"])

# Contenido principal
if menu == "Inicio":
    st.title("Dashboard General")
    st.write("")
    st.write("")

    # ==============================
    # FILTRO POR ESTADO EN SIDEBAR
    # ==============================
    st.sidebar.header("Filtros")
    estado_options = ["Todos"] + sorted(df['ESTADO'].unique())
    selected_estado = st.sidebar.radio("Filtrar por Estado:", estado_options)

    # ==============================
    # APLICAR FILTRO
    # ==============================
    filtered_df = df.copy()
    if selected_estado != "Todos":
        filtered_df = filtered_df[filtered_df['ESTADO'] == selected_estado]

    # ==============================
    # MÉTRICAS DINÁMICAS
    # ==============================
    estado_counts = filtered_df['ESTADO'].value_counts()

    if selected_estado == "Todos":
        total_proyectos = filtered_df['PROYECTO'].nunique()
        cols = st.columns(len(estado_counts) + 1)
        cols[0].metric("Total Proyectos", total_proyectos)
        for i, (estado, cantidad) in enumerate(estado_counts.items(), start=1):
            cols[i].metric(estado, cantidad)
    else:
        st.markdown("""
            <style>
            .metric-wrapper {
                max-width: 50px;
                margin: auto;
            }
            </style>
            <div class="metric-wrapper">
        """, unsafe_allow_html=True)

        cols = st.columns(len(estado_counts))
        for i, (estado, cantidad) in enumerate(estado_counts.items()):
            cols[i].metric(estado, cantidad)

        st.markdown("</div>", unsafe_allow_html=True)

    st.write("---")

   
    # ==============================
    # AGRUPAR DATOS POR CLIENTE
    # ==============================
    grouped = filtered_df.groupby('CLIENTE').agg(
        cantidad_proyectos=('PROYECTO', 'count'),
        progreso_promedio=('PORCENTAJE', 'mean'),
        Ingeniero=('INGENIERO DE IMPLEMENTACION', lambda x: ', '.join(x.unique()))  
    ).reset_index()

    # Agregar columna con estados concatenados
    estados_por_cliente = filtered_df.groupby('CLIENTE')['ESTADO'].apply(lambda x: ', '.join(x.unique())).reset_index()
    grouped = grouped.merge(estados_por_cliente, on='CLIENTE')

    # ==============================
    # GRÁFICO
    # ==============================
    if not grouped.empty:
        grouped = grouped.sort_values(by='progreso_promedio', ascending=True)

        fig = px.bar(
            grouped,
            x='progreso_promedio',
            y='CLIENTE',
            orientation='h',
            text='progreso_promedio',  # ✅ Mostrar progreso en la barra
            labels={
                'progreso_promedio': 'Progreso promedio (%)',
                'CLIENTE': 'Cliente',
                'cantidad_proyectos': 'Cantidad de proyectos'
            },
            title='Progreso de Proyectos por Cliente',
            hover_data={
                'cantidad_proyectos': True,
                'ESTADO': True,
                'Ingeniero': True  # ✅ Ingeniero en tooltip
            }
        )

        # Ajustes visuales
        fig.update_xaxes(range=[0, 100])
        fig.update_traces(textposition='outside')
        fig.update_layout(
            xaxis_title="Progreso promedio (%)",
            yaxis_title="Cliente",
            height=600,
            margin=dict(l=50, r=50, t=80, b=50)
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No hay datos para los filtros seleccionados.")


elif menu == "Proyectos":

    
    st.title("Dashboard de Proyectos")
    st.write("")
    st.write("")

    # ==============================
    # FILTROS EN SIDEBAR
    # ==============================
    st.sidebar.header("Filtros")

    # Filtro por Ingeniero
    ingeniero_options = ["Todos"] + sorted(df['INGENIERO DE IMPLEMENTACION'].unique())
    selected_ingeniero = st.sidebar.radio("Filtrar por Ingeniero:", ingeniero_options)

    # Filtro por Estado
    estado_options = ["Todos"] + sorted(df['ESTADO'].unique())
    selected_estado = st.sidebar.radio("Filtrar por Estado:", estado_options)

    # ==============================
    # APLICAR FILTROS
    # ==============================
    filtered_df = df.copy()
    if selected_ingeniero != "Todos":
        filtered_df = filtered_df[filtered_df['INGENIERO DE IMPLEMENTACION'] == selected_ingeniero]
    if selected_estado != "Todos":
        filtered_df = filtered_df[filtered_df['ESTADO'] == selected_estado]

    # ==============================
    # MÉTRICAS DINÁMICAS
    # ==============================
    estado_counts = filtered_df['ESTADO'].value_counts()

    
    if selected_estado == "Todos" and selected_ingeniero == "Todos":
        total_proyectos = filtered_df['PROYECTO'].nunique()
        cols = st.columns(len(estado_counts) + 1)
        cols[0].metric("Total Proyectos", total_proyectos)
        for i, (estado, cantidad) in enumerate(estado_counts.items(), start=1):
            cols[i].metric(estado, cantidad)
    else:
        st.write("Métricas filtradas:")
        num_cols = max(min(len(estado_counts), 2), 1) 
        cols = st.columns(num_cols)
        for i, (estado, cantidad) in enumerate(estado_counts.items()):
            with cols[i % num_cols]:
                st.metric(estado, cantidad)


    st.write("---")

    # ==============================
    # GRÁFICO AGRUPADO POR CLIENTE
    # ==============================
    grouped = filtered_df.groupby('CLIENTE').agg(
        cantidad_proyectos=('PROYECTO', 'count'),
        progreso_promedio=('PORCENTAJE', 'mean'),
        ingeniero=('INGENIERO DE IMPLEMENTACION', lambda x: ', '.join(x.unique()))
    ).reset_index()

    estados_por_cliente = filtered_df.groupby('CLIENTE')['ESTADO'].apply(lambda x: ', '.join(x.unique())).reset_index()
    grouped = grouped.merge(estados_por_cliente, on='CLIENTE')

    if not grouped.empty:
        grouped = grouped.sort_values(by='progreso_promedio', ascending=True)

        fig = px.bar(
            grouped,
            x='progreso_promedio',
            y='CLIENTE',
            orientation='h',
            text='progreso_promedio',
            labels={
                'progreso_promedio': 'Progreso promedio (%)',
                'CLIENTE': 'Cliente',
                'cantidad_proyectos': 'Cantidad de proyectos'
            },
            title='Progreso de Proyectos por Cliente',
            hover_data={'ESTADO': True, 'ingeniero': True}
        )

        fig.update_xaxes(range=[0, 100])
        fig.update_traces(textposition='outside')
        fig.update_layout(
            xaxis_title="Progreso promedio (%)",
            yaxis_title="Cliente",
            height=600,
            margin=dict(l=50, r=50, t=80, b=50)
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No hay datos para los filtros seleccionados.")

    # ==============================
    # EXPANDER CON TARJETAS DETALLADAS
    # ==============================
    st.write("---")
    with st.expander("Ver proyectos"):
        for _, row in filtered_df.iterrows():
            estado = row['ESTADO']
            cliente = row['CLIENTE']
            ingeniero = row['INGENIERO DE IMPLEMENTACION']
            inicio = row.get('FECHA DE INICIO', 'No disponible')
            fin = row.get('FECHA DE FINALIZACION', 'No disponible')
            progreso = row['PORCENTAJE']

            # ✅ Colores dinámicos según estado (incluye En pausa)
            if "Finalizado" in estado:
                color = "#28A745"  # Verde
            elif "Activo" in estado:
                color = "#FFA500"  # Naranja
            elif "En pausa" in estado:
                color = "#6C757D"  # Gris para En pausa
            else:
                color = "#FF4C4C"  # Rojo para otros estados

            st.markdown(f"""
                <div style="background:{color};padding:15px;border-radius:10px;margin-bottom:10px;color:white;">
                    <strong>Cliente:</strong> {cliente}<br>
                    <strong>Ingeniero:</strong> {ingeniero}<br>
                    <strong>Estado:</strong> {estado}<br>
                    <strong>Inicio:</strong> {inicio}<br>
                    <strong>Finalización:</strong> {fin}<br>
                    <strong>Progreso:</strong> {progreso:.1f}%
                </div>

            """, unsafe_allow_html=True)
