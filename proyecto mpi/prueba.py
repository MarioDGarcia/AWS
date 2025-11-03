import boto3
import pandas as pd
from io import StringIO
import streamlit as st
import plotly.express as px
import credencialesAWS
from datetime import datetime

# --- CONEXIÓN S3 ---
s3 = credencialesAWS.getCredentials()

# --- SELECCIÓN DE BUCKET ---
try:
    buckets = [b['Name'] for b in s3.list_buckets()['Buckets']]
except Exception as e:
    st.error(f"No se pudieron listar los buckets: {e}")
    st.stop()

st.sidebar.header("Configuración S3")
bucket_selected = st.sidebar.selectbox("Selecciona un bucket", options=buckets)

# --- LISTAR CARPETAS PRINCIPALES ---
try:
    response = s3.list_objects_v2(Bucket=bucket_selected, Delimiter='/')
    folders = [prefix['Prefix'].rstrip('/') for prefix in response.get('CommonPrefixes', [])]
    if not folders:
        st.warning("No hay carpetas en este bucket")
except Exception as e:
    st.error(f"No se pudieron listar carpetas: {e}")
    st.stop()

folder_selected = st.sidebar.selectbox("Selecciona carpeta (raw/curated)", options=folders)

# --- LISTAR SUBCARPETAS CON FECHA ---
try:
    response = s3.list_objects_v2(Bucket=bucket_selected, Prefix=f"{folder_selected}/", Delimiter='/')
    subfolders = [prefix['Prefix'].replace(folder_selected + '/', '').rstrip('/') for prefix in response.get('CommonPrefixes', [])]
    if not subfolders:
        st.warning("No hay subcarpetas con fecha, se tomará la carpeta principal")
        subfolders = ['']
except Exception as e:
    st.error(f"No se pudieron listar subcarpetas: {e}")
    st.stop()

subfolder_selected = st.sidebar.selectbox("Selecciona subcarpeta de fecha", options=subfolders)

# --- SELECCIÓN DE ARCHIVO DENTRO DE LA SUBCARPETA ---
prefix = f"{folder_selected}/"
if subfolder_selected:
    prefix += f"{subfolder_selected}/"

try:
    response = s3.list_objects_v2(Bucket=bucket_selected, Prefix=prefix)
    files = [obj['Key'].replace(prefix, '') for obj in response.get('Contents', [])]
    if not files:
        st.warning("No hay archivos en esta carpeta")
        st.stop()
except Exception as e:
    st.error(f"No se pudieron listar archivos: {e}")
    st.stop()

file_selected = st.sidebar.selectbox("Selecciona archivo CSV", options=files)

# --- CARGA DEL ARCHIVO ---
key = f"{prefix}{file_selected}"

try:
    obj = s3.get_object(Bucket=bucket_selected, Key=key)
    data = obj['Body'].read().decode('utf-8')
    df = pd.read_csv(StringIO(data))

    # Procesar columnas
    df.rename(columns={
        'fecha_venta': 'Fecha',
        'nombrePais': 'País',
        'unidades': 'Unidades',
        'Venta_Total': 'Ventas',
        'rango_edad': 'Categoría',
        'continente': 'Continente',
        'Precio': 'Precio'
    }, inplace=True)
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df['Año'] = df['Fecha'].dt.year

except Exception as e:
    st.error(f"Error cargando el archivo: {e}")
    st.stop()

# --- DASHBOARD ---
st.set_page_config(page_title="Dashboard Juguetes", page_icon="🧩", layout="wide")
st.title("🧩 Dashboard de Ventas de Juguetes Educativos")
st.markdown("### Impulsando la Educación de Calidad (ODS 4) y la Innovación (ODS 9)")

# --- Barra lateral: filtros ---
años = sorted(df['Año'].unique())
continentes = sorted(df['Continente'].unique())
paises = sorted(df['País'].unique())
categorias = sorted(df['Categoría'].unique())

año_seleccionado = st.sidebar.multiselect('Año:', options=años, default=años)
continente_seleccionado = st.sidebar.multiselect('Continente:', options=continentes, default=continentes)

paises_filtrados = df[df['Continente'].isin(continente_seleccionado)]['País'].unique()
pais_seleccionado = st.sidebar.multiselect('País:', options=sorted(paises_filtrados), default=sorted(paises_filtrados))
categoria_seleccionada = st.sidebar.multiselect('Rango de Edad:', options=categorias, default=categorias)

df_filtrado = df.query(
    "Año == @año_seleccionado & Continente == @continente_seleccionado & País == @pais_seleccionado & Categoría == @categoria_seleccionada"
)

if df_filtrado.empty:
    st.warning("No hay datos disponibles para la selección actual. Ajusta los filtros.")
    st.stop()

# --- Métricas ---
ventas_totales = df_filtrado['Ventas'].sum()
unidades_totales = df_filtrado['Unidades'].sum()
precio_promedio = df_filtrado['Precio'].mean()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Ventas Totales", f"${ventas_totales:,.2f}")
with col2:
    st.metric("Unidades Vendidas", f"{unidades_totales:,}")
with col3:
    st.metric("Precio Promedio", f"${precio_promedio:,.2f}")
st.markdown("---")

# --- Mapa Mundial ---
st.markdown("#### Ventas Totales por País")
ventas_mapa = df_filtrado.groupby('País')['Ventas'].sum().reset_index()
fig_mapa = px.choropleth(
    ventas_mapa,
    locations="País",
    locationmode='country names',
    color="Ventas",
    hover_name="País",
    color_continuous_scale=px.colors.sequential.Plasma,
    template='plotly_dark'
)
fig_mapa.update_layout(margin=dict(l=0,r=0,t=0,b=0), geo=dict(showframe=False, showcoastlines=False))
st.plotly_chart(fig_mapa, use_container_width=True)
st.markdown("---")



# --- Insights del mapa ---
# --- Análisis narrativo ---
st.markdown(
    """
    <h4 style='text-align: center;'>🧠 Análisis de Ventas Globales</h4>
    """,
    unsafe_allow_html=True
)

# País con más ventas
pais_top = ventas_mapa.loc[ventas_mapa['Ventas'].idxmax(), 'País']
ventas_top_pais = ventas_mapa.loc[ventas_mapa['Ventas'].idxmax(), 'Ventas']
porcentaje_top_pais = (ventas_top_pais / ventas_mapa['Ventas'].sum()) * 100

# Categoría más popular
categoria_top = df_filtrado.groupby('Categoría')['Ventas'].sum().idxmax()
ventas_top_categoria = df_filtrado.groupby('Categoría')['Ventas'].sum().max()
porcentaje_categoria = (ventas_top_categoria / df_filtrado['Ventas'].sum()) * 100

# Producto más vendido
producto_top = df_filtrado.groupby('Producto')['Ventas'].sum().idxmax()
ventas_top_producto = df_filtrado.groupby('Producto')['Ventas'].sum().max()
porcentaje_producto = (ventas_top_producto / df_filtrado['Ventas'].sum()) * 100

# Texto descriptivo
st.markdown(f"""
En este conjunto de datos, el **país con mayores ventas** es **{pais_top}**, 
con un total de **${ventas_top_pais:,.2f}**, lo que representa aproximadamente 
**{porcentaje_top_pais:.2f}%** de las ventas globales.

La **categoría más popular** es **{categoria_top}**, concentrando el **{porcentaje_categoria:.2f}%** 
del total de ventas, lo que sugiere una fuerte preferencia en ese rango de edad.

Por otro lado, el **producto estrella** es **{producto_top}**, responsable de 
**{porcentaje_producto:.2f}%** de las ventas totales registradas.
""")

st.info("Estos resultados ayudan a identificar los mercados y productos más rentables, facilitando la toma de decisiones estratégicas en campañas o inventarios.")


# --- Gráficos dinámicos ---
col_graf_1, col_graf_2 = st.columns(2)

with col_graf_1:
    ventas_por_pais = df_filtrado.groupby('País')['Ventas'].sum().sort_values(ascending=True).reset_index()
    fig_bar_pais = px.bar(
        ventas_por_pais.tail(10),
        y='País',
        x='Ventas',
        orientation='h',
        title='<b>Top 10 Países por Ventas</b>',
        color_discrete_sequence=['#2ca02c'],
        template='plotly_dark'
    )
    st.plotly_chart(fig_bar_pais, use_container_width=True)

with col_graf_2:
    ventas_por_categoria = df_filtrado.groupby('Categoría')['Ventas'].sum().reset_index()
    fig_pie_categoria = px.pie(
        ventas_por_categoria,
        names='Categoría',
        values='Ventas',
        title='<b>Distribución de Ventas por Rango de Edad</b>',
        color_discrete_sequence=px.colors.qualitative.Pastel,
        template='plotly_dark'
    )
    fig_pie_categoria.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pie_categoria, use_container_width=True)

# --- Evolución temporal ---
df_area = df_filtrado.set_index('Fecha').groupby(pd.Grouper(freq='M'))['Ventas'].sum().reset_index()
fig_area_tiempo = px.area(
    df_area,
    x='Fecha',
    y='Ventas',
    title='<b>Evolución Mensual de Ventas</b>',
    template='plotly_dark',
    color_discrete_sequence=['#1f77b4']
)
st.plotly_chart(fig_area_tiempo, use_container_width=True)

st.markdown("---")
col_prod, col_tabla = st.columns(2)

with col_prod:
    ventas_por_producto = df_filtrado.groupby('Producto')['Ventas'].sum().sort_values(ascending=True).reset_index()
    fig_bar_producto = px.bar(
        ventas_por_producto.tail(10),
        y='Producto',
        x='Ventas',
        orientation='h',
        title='<b>Top 10 Productos por Ventas</b>',
        color_discrete_sequence=['#ff7f0e'],
        template='plotly_dark'
    )
    st.plotly_chart(fig_bar_producto, use_container_width=True)

with col_tabla:
    st.markdown("#### Datos Detallados")
    st.dataframe(df_filtrado[['Fecha', 'País', 'Categoría', 'Producto', 'Unidades', 'Ventas']].reset_index(drop=True), height=350)

# --- Estilo personalizado ---
st.markdown("""
<style>
[data-testid="stAppViewContainer"] > .main {
    background-color: #0E1117;
}
h1, h2, h3, h4, h5, h6 {
    color: #FAFAFA;
}
.stMetric {
    background-color: #161A25;
    border: 1px solid #262730;
    border-radius: 10px;
    padding: 15px;
    color: #FAFAFA;
    box-shadow: 0 4px 6px rgba(0,0,0,0.2);
}
[data-testid="stMetricLabel"] {
    color: #A0A0A0;
}
</style>
""", unsafe_allow_html=True)
