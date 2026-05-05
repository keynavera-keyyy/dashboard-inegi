import plotly
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Dashboard INEGI",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Dashboard de Unidades Económicas INEGI")
st.write("Análisis visual de establecimientos registrados en la base de datos normalizada.")

@st.cache_data
def cargar_datos():
    df = pd.read_csv("normalizado INEGI.csv", encoding="latin1")
    return df

df = cargar_datos()

# Limpieza básica de columnas
df.columns = df.columns.str.strip()

st.sidebar.header("Filtros")

if "entidad" in df.columns:
    estados = st.sidebar.multiselect(
        "Filtrar por estado",
        options=sorted(df["entidad"].dropna().unique()),
        default=sorted(df["entidad"].dropna().unique())
    )
    df_filtrado = df[df["entidad"].isin(estados)]
else:
    df_filtrado = df.copy()

if "municipio" in df.columns:
    municipios = st.sidebar.multiselect(
        "Filtrar por municipio",
        options=sorted(df_filtrado["municipio"].dropna().unique()),
        default=sorted(df_filtrado["municipio"].dropna().unique())
    )
    df_filtrado = df_filtrado[df_filtrado["municipio"].isin(municipios)]

# KPIs
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total de unidades", len(df_filtrado))

with col2:
    if "entidad" in df_filtrado.columns:
        st.metric("Estados registrados", df_filtrado["entidad"].nunique())
    else:
        st.metric("Estados registrados", "N/A")

with col3:
    if "municipio" in df_filtrado.columns:
        st.metric("Municipios registrados", df_filtrado["municipio"].nunique())
    else:
        st.metric("Municipios registrados", "N/A")

st.divider()

# Gráfica 1: unidades por estado
if "entidad" in df_filtrado.columns:
    conteo_estado = df_filtrado["entidad"].value_counts().reset_index()
    conteo_estado.columns = ["Estado", "Total"]

    fig_estado = px.bar(
        conteo_estado,
        x="Estado",
        y="Total",
        title="Unidades económicas por estado",
        text="Total"
    )

    st.plotly_chart(fig_estado, use_container_width=True)

# Gráfica 2: unidades por municipio
if "municipio" in df_filtrado.columns:
    conteo_municipio = df_filtrado["municipio"].value_counts().head(10).reset_index()
    conteo_municipio.columns = ["Municipio", "Total"]

    fig_municipio = px.bar(
        conteo_municipio,
        x="Municipio",
        y="Total",
        title="Top 10 municipios con más unidades económicas",
        text="Total"
    )

    st.plotly_chart(fig_municipio, use_container_width=True)

# Gráfica 3: actividad económica
if "nombre_act" in df_filtrado.columns:
    conteo_actividad = df_filtrado["nombre_act"].value_counts().head(10).reset_index()
    conteo_actividad.columns = ["Actividad", "Total"]

    fig_actividad = px.pie(
        conteo_actividad,
        names="Actividad",
        values="Total",
        title="Principales actividades económicas"
    )

    st.plotly_chart(fig_actividad, use_container_width=True)

# Mapa si existen latitud y longitud
if "latitud" in df_filtrado.columns and "longitud" in df_filtrado.columns:
    df_mapa = df_filtrado.copy()
    df_mapa["latitud"] = pd.to_numeric(df_mapa["latitud"], errors="coerce")
    df_mapa["longitud"] = pd.to_numeric(df_mapa["longitud"], errors="coerce")
    df_mapa = df_mapa.dropna(subset=["latitud", "longitud"])

    if not df_mapa.empty:
        st.subheader("📍 Mapa de unidades económicas")
        st.map(df_mapa, latitude="latitud", longitude="longitud")

st.divider()

st.subheader("📋 Vista de datos")
st.dataframe(df_filtrado, use_container_width=True)

st.success("Dashboard generado correctamente con datos del archivo normalizado INEGI.")