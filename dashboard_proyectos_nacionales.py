import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Dashboard Proyectos Nacionales Gesis", layout="wide")

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



/* Contenedor del calendario */
[data-baseweb="datepicker"] {
    background-color: #2c2c2c !important; /* Fondo oscuro */
    color: #ffffff !important; /* Texto blanco */
    border-radius: 8px;
    padding: 10px;
}

/* Encabezado del calendario */
[data-baseweb="datepicker"] .calendar-header {
    background-color: #1f1f1f !important;
    color: #ffffff !important;
}

/* Días del calendario */
[data-baseweb="datepicker"] .calendar-day {
    color: #ffffff !important;
}

/* Día seleccionado */
[data-baseweb="datepicker"] .calendar-day.selected {
    background-color: #ff4d4d !important;
    color: #ffffff !important;
    border-radius: 50%;
}

/* Hover sobre días */
[data-baseweb="datepicker"] .calendar-day:hover {
    background-color: #444444 !important;
    color: #ffffff !important;
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

url = "https://grupoesisgt-my.sharepoint.com/personal/ana_barrientos_grupoesis_com/_layouts/15/download.aspx?share=IQADrf0byTGlSauErefLV5xRAYJZ5ZLMqnxg27FiR3iIqvI"
df = pd.read_excel(url, engine="openpyxl")


# Limpiar nombres de columnas
df.columns = df.columns.str.strip()

# Limpiar valores en columnas clave
df['INGENIERO DE IMPLEMENTACION'] = df['INGENIERO DE IMPLEMENTACION'].astype(str).str.strip()
df['STATUS'] = df['STATUS'].astype(str).str.strip()
df['STATUS'] = df['STATUS'].str.replace(r'\s+', ' ', regex=True)  # eliminar espacios extra

# Convertir fechas
if 'FECHA DE INICIO' in df.columns:
    df['FECHA DE INICIO'] = pd.to_datetime(df['FECHA DE INICIO'], format='%d-%m-%y', errors='coerce').dt.strftime('%d-%m-%Y')
if 'FECHA DE FINALIZACION' in df.columns:
    df['FECHA DE FINALIZACION'] = pd.to_datetime(df['FECHA DE FINALIZACION'], format='%d-%m-%y', errors='coerce').dt.strftime('%d-%m-%Y')


# Sidebar
st.sidebar.image("logo.jpeg", width=110)
st.sidebar.title("Dashboard")
menu = st.sidebar.radio("Menú", ["Inicio", "Proyectos"])

# Contenido principal
if menu == "Inicio":
    st.title("Dashboard General")
    
elif menu == "Proyectos":

    # ==============================
    # Título
    # ==============================
    st.title("Dashboard de Proyectos Nacionales")
    st.write("")
    st.write("")

     # ==============================
    # Normaliza columnas y prepara fechas
    # ==============================
    # 1) Normalizar encabezados
    df.columns = df.columns.str.strip()

    # 2) Detectar nombre real de la columna de fecha (tolerante a variaciones)
    posibles_fechas = ["FECHA DE INICIO", "Fecha de inicio", "FECHA_INICIO", "Fecha Inicio"]
    col_fecha = next((c for c in posibles_fechas if c in df.columns), None)

    if col_fecha:
        # Limpieza básica para evitar strings raros
        df[col_fecha] = df[col_fecha].astype(str).str.strip().replace({"": None, "nan": None, "None": None})

        # 3) Intentar parseo robusto de fechas
        def parse_fecha_robusta(s):
            if pd.isna(s):
                return pd.NaT
            # Intento por formatos comunes
            for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%m/%d/%Y", "%m-%d-%Y"):
                try:
                    return pd.to_datetime(s, format=fmt)
                except Exception:
                    pass
            # Último recurso: heurística con dayfirst
            try:
                return pd.to_datetime(s, dayfirst=True, errors="coerce")
            except Exception:
                return pd.NaT

        df["FECHA_INICIO_DT"] = df[col_fecha].apply(parse_fecha_robusta)
        # 4) Extraer mes
        df["MES_INICIO"] = df["FECHA_INICIO_DT"].dt.month
    else:
        # Si no hay columna de fecha, asegúrate de no intentar filtrar por mes
        df["MES_INICIO"] = pd.NA

    # ==============================
    # 🎛️ FILTROS PERSONALIZADOS (tu bloque original)
    # ==============================
    st.sidebar.header("Filtros Personalizados")
    columnas_filtrables = df.select_dtypes(include=["object"]).columns.tolist()
    columnas_seleccionadas = st.sidebar.multiselect(
        "Selecciona columnas para filtrar:",
        columnas_filtrables,
        default=[]
    )

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
    # 📅 FILTRO POR MES (usando MES_INICIO)
    # ==============================
    st.sidebar.subheader("Filtrar por Mes")
    meses_nombres = ["Todos", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    mes_seleccionado = st.sidebar.selectbox("Selecciona un mes:", meses_nombres, index=0)

    mapa_mes = {nombre: i for i, nombre in enumerate(meses_nombres)}
    # Ajustar para que "Enero" sea 1, "Febrero" 2, ... y "Todos" -> 0
    mapa_mes = {m: i for i, m in enumerate(meses_nombres)}
    # Rehacer correctamente:
    mapa_mes = {"Todos": None, "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4, "Mayo": 5,
                "Junio": 6, "Julio": 7, "Agosto": 8, "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12}
    mes_num = mapa_mes.get(mes_seleccionado)

    # ==============================
    # 🧩 APLICAR FILTROS
    # ==============================
    filtered_df = df.copy()

    # Filtros de texto
    for col, val in filtros.items():
        filtered_df = filtered_df[filtered_df[col].astype(str) == val]

    # Filtro por mes usando la columna derivada
    if mes_num is not None and "MES_INICIO" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["MES_INICIO"] == mes_num]

    # ==============================
    # 📊 MÉTRICAS DINÁMICAS (ajuste de porcentaje a numérico)
    # ==============================
    # Asegurar que PORCENTAJE sea numérico en el filtered_df
    if "PORCENTAJE" in filtered_df.columns:
        filtered_df["PORCENTAJE"] = (
            pd.to_numeric(filtered_df["PORCENTAJE"].astype(str).str.replace("%", "", regex=False),
                        errors="coerce")
            .clip(lower=0, upper=100)
        )

    estado_counts = filtered_df["STATUS"].value_counts() if "STATUS" in filtered_df.columns else pd.Series(dtype=int)

    if not estado_counts.empty:
        total_proyectos = filtered_df["PROYECTO"].nunique() if "PROYECTO" in filtered_df.columns else len(filtered_df)
        num_cols = len(estado_counts) + 1
        cols = st.columns(num_cols)
        cols[0].metric("Total Proyectos", int(total_proyectos))
        for i, (estado, cantidad) in enumerate(estado_counts.items(), start=1):
            cols[i].metric(str(estado), int(cantidad))
    else:
        st.warning("No hay métricas para mostrar con los filtros seleccionados.")

    st.write("---")

    # ==============================
    # 📈 GRÁFICO AGRUPADO POR CLIENTE (tu bloque con pequeños resguardos)
    # ==============================
    if all(c in filtered_df.columns for c in ["CLIENTE", "PROYECTO"]):
        grouped = (
            filtered_df.groupby("CLIENTE")
            .agg(
                cantidad_proyectos=("PROYECTO", "count"),
                progreso_promedio=("PORCENTAJE", "mean"),
                Ingeniero=("INGENIERO DE IMPLEMENTACION", lambda x: ", ".join(x.dropna().astype(str).unique())
                        if "INGENIERO DE IMPLEMENTACION" in filtered_df.columns else ""),
            )
            .reset_index()
        )

        if "STATUS" in filtered_df.columns:
            estados_por_cliente = (
                filtered_df.groupby("CLIENTE")["STATUS"]
                .apply(lambda x: ", ".join(x.dropna().astype(str).unique()))
                .reset_index()
            )
            grouped = grouped.merge(estados_por_cliente, on="CLIENTE", how="left")

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
                hover_data={"STATUS": True, "Ingeniero": True} if "STATUS" in grouped.columns else None,
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
    else:
        st.warning("Faltan columnas esenciales (CLIENTE y/o PROYECTO) para el gráfico.")

    # ==============================
    # 📋 LISTA DE PROYECTOS FILTRADOS (tu bloque)
    # ==============================
    st.write("---")
    st.subheader("Lista de proyectos filtrados")

    columnas_busqueda = [c for c in ["PROYECTO", "CLIENTE", "STATUS", "INGENIERO DE IMPLEMENTACION"] if c in filtered_df.columns]
    termino_busqueda = st.text_input("Buscar (por proyecto, cliente, status, ingeniero):", value="").strip()

    df_listado = filtered_df.copy()
    if termino_busqueda and columnas_busqueda:
        mask = pd.Series(False, index=df_listado.index)
        for c in columnas_busqueda:
            mask |= df_listado[c].astype(str).str.contains(termino_busqueda, case=False, na=False)
        df_listado = df_listado[mask]

    cols_por_defecto = [c for c in ["CLIENTE", "PROYECTO", "INGENIERO DE IMPLEMENTACION", "STATUS", "PORCENTAJE"] if c in df_listado.columns]
    cols_mostrar = st.multiselect("Columnas a mostrar en la lista:", options=df_listado.columns.tolist(), default=cols_por_defecto)

    column_config = {}
    if "PORCENTAJE" in cols_mostrar:
        try:
            column_config["PORCENTAJE"] = st.column_config.ProgressColumn("Progreso", min_value=0, max_value=100, format="%d%%")
        except Exception:
            pass
    if "FECHA DE INICIO" in cols_mostrar and "FECHA_INICIO_DT" in df_listado.columns:
        # Muestra la fecha parseada si quieres consistencia
        df_listado["FECHA DE INICIO"] = df_listado["FECHA_INICIO_DT"]

    if "FECHA DE FINALIZACION" in cols_mostrar:
        df_listado["FECHA DE FINALIZACION"] = pd.to_datetime(df_listado["FECHA DE FINALIZACION"], errors="coerce")

    st.dataframe(
        df_listado[cols_mostrar],
        use_container_width=True,
        hide_index=True,
        height=400,
        column_config=column_config if column_config else None
    )


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
                fechas_siguientes = row.get("FECHA SIGUIENTES PASOS", "No disponible")
                ingeniero = row["INGENIERO DE IMPLEMENTACION"]
                estado = row["STATUS"]
                inicio = row.get("FECHA DE INICIO", "No disponible")
                fin = row.get("FECHA DE FINALIZACION", "No disponible")
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
                        <strong>Fecha siguientes pasos:</strong> {fechas_siguientes}<br>
                        <strong>Inicio:</strong> {inicio}<br>
                        <strong>Finalización:</strong> {fin}<br>
                        <strong>Progreso:</strong> {progreso:.1f}%
                    </div>
                """, unsafe_allow_html=True)
