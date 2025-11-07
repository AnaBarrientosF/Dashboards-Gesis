import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Dashboard Proyectos Gesis", layout="wide")

# CSS para cambiar el color del sidebar y el header
st.markdown("""
<style>

/* ==================== FONDO GENERAL ==================== */
.stApp {
    background-color: #FBFBFB;
}

/* ==================== TEXTO GENERAL ==================== */
h1, h2, h3, p, div, span {
    color: black !important;
}

/* ==================== SIDEBAR ==================== */
[data-testid="stSidebar"] {
    background-color: #0B2A85;
}
[data-testid="stSidebar"] * {
    color: white !important;
}

/* ==================== HEADER SUPERIOR ==================== */
[data-testid="stHeader"] {
    background-color: #1043D4;
}
[data-testid="stHeader"] * {
    color: white !important;
}

/* ==================== MÉTRICAS ==================== */
div[data-testid="stMetric"] {
    padding: 15px;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    margin: 5px;
    text-align: center;
}

/* ==================== SELECT / MULTISELECT ==================== */

/* Caja visible del selector */
[data-baseweb="select"] > div {
    border: 1px solid #ffffff66 !important;
}

/* Texto dentro del selector (valor seleccionado) */
[data-baseweb="select"] * {
    color: #FFFFFF !important;
}                       

/* Menú desplegable (lista al abrir el select) */
[data-baseweb="menu"],
[data-baseweb="popover"],
[data-baseweb="popover-content"] {
    color: #FFFFFF !important;
    background-color: #FFFFFF !important;
    
}
            
[data-baseweb="menu"] [role="option"],
[data-baseweb="popover"] [role="option"],
[data-baseweb="popover-content"] [role="option"] {
    background-color: #FFFF !important;    /* fondo negro */
    color: #FFFF !important;               /* texto gris claro (puedes cambiarlo) */
    font-weight: 500;
    padding: 6px 10px;

}
            
/* ==================== Hover visual (cuando pasas el mouse) ==================== */
[data-baseweb="menu"] [role="option"]:hover,
[data-baseweb="popover"] [role="option"]:hover,
[data-baseweb="popover-content"] [role="option"]:hover,
[data-baseweb="menu"] div[role="option"]:hover {
    background-color: #B0B0B0  !important;
    color: #FFFF !important;
    cursor: pointer;         


                      
        
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

url = "https://grupoesisgt-my.sharepoint.com/personal/ana_barrientos_grupoesis_com/_layouts/15/download.aspx?share=EVR3xXpC1f9Nt0f_9067bvYB5KG1O6YowbuJGpZL7yvUqA"
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
    


elif menu == "Proyectos":

    st.title("Dashboard de Proyectos")
    st.write("")
    st.write("")

    # ==============================
    # 🎛️ FILTROS PERSONALIZADOS
    # ==============================
    st.sidebar.header("Filtros Personalizados")

    # Selección de columnas filtrables (solo texto)
    columnas_filtrables = df.select_dtypes(include=["object"]).columns.tolist()
    columnas_seleccionadas = st.sidebar.multiselect(
        "Selecciona columnas para filtrar:",
        opciones := columnas_filtrables,
        default=[]
    )

    # Crear selectboxes dinámicos según columnas seleccionadas
    filtros = {}
    for col in columnas_seleccionadas:
        valores_unicos = ["Todos"] + sorted(df[col].dropna().astype(str).unique().tolist())
        valor_sel = st.sidebar.selectbox(
            f"Filtrar por {col}:",
            valores_unicos,
            key=f"filter_{col}"
        )
        if valor_sel != "Todos":
            filtros[col] = valor_sel

   

    # ==============================
    # 🧩 APLICAR FILTROS
    # ==============================
    filtered_df = df.copy()
    for col, val in filtros.items():
        filtered_df = filtered_df[filtered_df[col].astype(str) == val]

    # ==============================
    # 📊 MÉTRICAS DINÁMICAS
    # ==============================
    estado_counts = filtered_df["ESTADO"].value_counts()

    if not estado_counts.empty:
        total_proyectos = filtered_df["PROYECTO"].nunique()
        num_cols = len(estado_counts) + 1
        cols = st.columns(num_cols)
        cols[0].metric("Total Proyectos", total_proyectos)
        for i, (estado, cantidad) in enumerate(estado_counts.items(), start=1):
            cols[i].metric(estado, cantidad)
    else:
        st.warning("No hay métricas para mostrar con los filtros seleccionados.")

    st.write("---")

    # ==============================
    # 📈 GRÁFICO AGRUPADO POR CLIENTE
    # ==============================
    grouped = (
        filtered_df.groupby("CLIENTE")
        .agg(
            cantidad_proyectos=("PROYECTO", "count"),
            progreso_promedio=("PORCENTAJE", "mean"),
            Ingeniero=("INGENIERO DE IMPLEMENTACION", lambda x: ", ".join(x.dropna().astype(str).unique())),
            Pais=("PAIS", lambda x: ", ".join(x.dropna().astype(str).unique())),
        )
        .reset_index()
    )

    estados_por_cliente = (
        filtered_df.groupby("CLIENTE")["ESTADO"]
        .apply(lambda x: ", ".join(x.dropna().astype(str).unique()))
        .reset_index()
    )
    grouped = grouped.merge(estados_por_cliente, on="CLIENTE")

    if not grouped.empty:
        grouped = grouped.sort_values(by="progreso_promedio", ascending=True)

        fig = px.bar(
            grouped,
            x="progreso_promedio",
            y="CLIENTE",
            orientation="h",
            text="progreso_promedio",
            labels={
                "progreso_promedio": "Progreso promedio (%)",
                "CLIENTE": "Cliente",
                "cantidad_proyectos": "Cantidad de proyectos",
            },
            title="Progreso de Proyectos por Cliente",
            hover_data={"ESTADO": True, "Ingeniero": True, "Pais": True},
        )

        fig.update_xaxes(range=[0, 100])
        fig.update_traces(textposition="outside")
        fig.update_layout(
            xaxis_title="Progreso promedio (%)",
            yaxis_title="Cliente",
            height=600,
            margin=dict(l=50, r=50, t=80, b=50),
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No hay datos para los filtros seleccionados.")

    # ==============================
    # 🗂️ EXPANDER CON TARJETAS DETALLADAS
    # ==============================
    st.write("---")
    with st.expander("Ver proyectos"):
        if filtered_df.empty:
            st.warning("No hay proyectos para mostrar.")
        else:
            for _, row in filtered_df.iterrows():
                cliente = row["CLIENTE"]
                proyecto = row["PROYECTO"]
                descripcion = row["STATUS"]
                ingeniero = row["INGENIERO DE IMPLEMENTACION"]
                inicio = row.get("FECHA DE INICIO", "No disponible")
                fin = row.get("FECHA DE FINALIZACION", "No disponible")
                fechas_siguientes = row.get("FECHA SIGUIENTES PASOS", "No disponible")
                progreso = row["PORCENTAJE"]

                # ✅ Colores dinámicos según estado
                if "Finalizado" in estado:
                    color = "#FFA500"  # Naranja
                elif "Activo" in estado:
                    color = "#28A745"  # Verde
                elif "En pausa" in estado:
                    color = "#6C757D"  # Gris
                else:
                    color = "#FF4C4C"  # Rojo

                st.markdown(f"""
                    <div style="background:{color};padding:15px;border-radius:10px;margin-bottom:10px;color:white;">
                        <strong>Cliente:</strong> {cliente}<br>
                        <strong>Proyecto:</strong> {proyecto}<br>
                        <strong>Status:</strong> {descripcion}<br>
                        <strong>Ingeniero:</strong> {ingeniero}<br>
                        <strong>Inicio:</strong> {inicio}<br>
                        <strong>Finalización:</strong> {fin}<br>
                        <strong>Fecha siguientes pasos:</strong> {fechas_siguientes}<br>
                        <strong>Progreso:</strong> {progreso:.1f}%
                    </div>
                """, unsafe_allow_html=True)
