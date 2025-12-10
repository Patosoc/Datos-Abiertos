import pandas as pd
import streamlit as st

st.set_page_config(page_title="Dashboard Equidad" )

# ----- 1. CARGA DE DATOS -----
df = pd.read_excel("Dataframe1.xlsx")

# Normalización básica
df["Pais de Estudios"] = df["Pais de Estudios"].astype(str).str.strip()
df["Destino Pais"] = df["Pais de Estudios"].str.title()


# ----- 2. CÁLCULO DE INDICADORES -----

# Totales globales
total_hombres = (df["Sexo"] == "Masculino").sum()
total_mujeres = (df["Sexo"] == "Femenino").sum()

# Totales por año
genero_por_ano = df.groupby(["Año de la convocatoria", "Sexo"]).size().unstack(fill_value=0)

# Totales por región
genero_por_region = df.groupby(["Depto_nacimi", "Sexo"]).size().unstack(fill_value=0)

# Totales por destino país
genero_por_destino = df.groupby(["Pais de Estudios", "Sexo"]).size().unstack(fill_value=0)

# % de participación por país destino
participacion_por_pais = (df["Pais de Estudios"].value_counts(normalize=True) * 100).round(2)

# País dominante por región
pais_por_region = df.groupby("Región de nacimiento")["Pais de Estudios"].agg(lambda x: x.value_counts().idxmax())

# Brecha de equidad por país destino (%)
equidad_destino_pct = df.groupby("Pais de Estudios")["Sexo"].value_counts(normalize=True).unstack().fillna(0) * 100
equidad_destino_pct = equidad_destino_pct.round(2)
if "Masculino" in equidad_destino_pct.columns and "Femenino" in equidad_destino_pct.columns:
    equidad_destino_pct["Brecha Equidad (|H-M|)"] = (equidad_destino_pct["Masculino"] - equidad_destino_pct["Femenino"]).abs()
else:
    equidad_destino_pct["Brecha Equidad (|H-M|)"] = 0

# Región con mayor movilidad internacional (conteo)
movilidad_por_region = df.groupby("Región de nacimiento").size().sort_values(ascending=False)

# Diversidad de destinos por año
diversidad_destinos_ano = df.groupby("Año de la convocatoria")["Pais de Estudios"].nunique()

# Ranking de destinos por año
ranking_destino_ano = df.groupby("Año de la convocatoria")["Pais de Estudios"].value_counts().groupby(level=0).head(5)

# Duración promedio por género (si existe el campo "Duracion" en el df)
if "Duracion" in df.columns:
   duracion_prom_genero = df.groupby("Sexo")["Duracion"].mean().round(2)
else:
    duracion_prom_genero = "No disponible en la matriz"

# Proyección 2026 (tendencia lineal simple con promedio móvil)
proyeccion_genero_2026 = df.groupby("Año de la convocatoria")["Sexo"].value_counts().groupby(level=0).apply(lambda x: x).unstack(fill_value=0)
proyeccion_genero_2026 = proyeccion_genero_2026.mean().round()


# ----- 3. DASHBOARD EN STREAMLIT -----

st.set_page_config(layout="wide")
st.title("📊 Dashboard Avanzado – Financiación Académica")

# --- FILTROS ---
st.sidebar.header("🔎 Filtros")
años = st.sidebar.multiselect("Año", options=sorted(df["Año de la convocatoria"].unique()), default=sorted(df["Año de la convocatoria"].unique()))
regiones = st.sidebar.multiselect("Región", options=sorted(df["Región de nacimiento"].unique()), default=sorted(df["Región de nacimiento"].unique()))
generos = st.sidebar.multiselect("Género", options=sorted(df["Sexo"].unique()), default=sorted(df["Sexo"].unique()))

df_filtrado = df[df["Año de la convocatoria"].isin(años) & df["Región de nacimiento"].isin(regiones) & df["Sexo"].isin(generos)]

# ---- TARJETAS PRINCIPALES ----
st.subheader("👥 Indicadores Globales")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total financiados", len(df_filtrado))
c2.metric("Total hombres", (df_filtrado["Sexo"] == "Masculino").sum())
c3.metric("Total mujeres", (df_filtrado["Sexo"] == "Femenino").sum())
c4.metric("Destinos únicos", df_filtrado["Pais de Estudios"].nunique())

# ---- SECCIÓN DE DATOS FILTRADOS ----
st.subheader("📍 País dominante de estudio por región")
st.dataframe(pais_por_region.loc[regiones])

st.subheader("🌍 Movilidad internacional por región")
st.dataframe(movilidad_por_region.loc[regiones])

st.subheader("⚖️ Brecha de Equidad por País Destino (%)")
st.dataframe(equidad_destino_pct.loc[df_filtrado["Pais de Estudios"].unique()])

st.subheader("📈 Hombres vs Mujeres por Año")
st.dataframe(genero_por_ano.loc[años])

#st.subheader("🏢 Hombres vs Mujeres por Región")
#st.dataframe(genero_por_region.loc[regiones])

st.subheader("🎯 % Participación por país destino (todos financiados)")
st.dataframe((df_filtrado["Pais de Estudios"].value_counts(normalize=True) * 100).round(2))

st.subheader("🔥 Ranking Top 5 países destino del período filtrado")
top5 = df_filtrado["Pais de Estudios"].value_counts().head(5)
st.dataframe(top5)

# --- GRÁFICOS ---
st.subheader("📊 Visualizaciones")

# Gráfico H vs M global
st.write("### Total Hombres vs Total Mujeres")
genero_global = df_filtrado["Sexo"].value_counts()
st.bar_chart(genero_global)

# H vs M por año
st.write("### Total Hombres vs Mujeres por Año")
genero_ano_graf = df_filtrado.groupby(["Año de la convocatoria", "Sexo"]).size().unstack(fill_value=0)
st.bar_chart(genero_ano_graf)

# H vs M por región
st.write("### Total Hombres vs Mujeres por Región")
genero_region_graf = df_filtrado.groupby(["Depto_nacimi", "Sexo"]).size().unstack(fill_value=0)
st.bar_chart(genero_region_graf)

# Mujeres vs hombres por destino
st.write("### Mujeres vs Hombres por País Destino")
destino_region_graf = df_filtrado.groupby(["Pais de Estudios", "Sexo"]).size().unstack(fill_value=0)
st.bar_chart(destino_region_graf)

# Movilidad por región (orden)
st.write("### Región con mayor movilidad")
st.bar_chart(movilidad_por_region.loc[regiones])

# Proyección 2026
st.write("### 🔮 Proyección 2026 – promedio lineal por género")
st.write(proyeccion_genero_2026)

# ---------------------------------------------
# NUEVOS GRÁFICOS SOLICITADOS
# ---------------------------------------------


st.write("### 🚻 Selección de Sexo por Modalidad")

# Validación de columnas
if all(col in df_filtrado.columns for col in ["Modalidad", "Sexo"]):
    sexo_modalidad = df_filtrado.groupby(["Modalidad", "Sexo"]).size().unstack(fill_value=0)

    st.bar_chart(sexo_modalidad)
else:
    st.warning("⚠️ El dataframe no contiene las columnas 'Modalidad' y 'Sexo'. Verifica los nombres.")

# ---------------------------------------------
# TABLA Y GRÁFICA: SEXO POR OCDE (INTERACTIVO)
# ---------------------------------------------

st.write("### 🎓 Distribución de Sexo por OCDE (Top N Interactivo)")

# Validación de columnas
if all(col in df_filtrado.columns for col in ["OCDE", "Sexo"]):

    # Selector Top N
    top_n = st.selectbox(
        "Seleccionar Top N categorías OCDE",
        [5, 10, 20, 30, "Todos"],
        index=1
    )

    # Conteo total por OCDE para determinar los más frecuentes
    conteo_ocde = df_filtrado["OCDE"].value_counts()

    # Filtrar por Top N
    if top_n == "Todos":
        ocde_seleccionadas = conteo_ocde.index.tolist()
    else:
        ocde_seleccionadas = conteo_ocde.head(top_n).index.tolist()

    df_ocde_top = df_filtrado[df_filtrado["OCDE"].isin(ocde_seleccionadas)]

    # Tabla Sexo vs OCDE
    tabla_sexo_ocde = (
        df_ocde_top.groupby(["OCDE", "Sexo"])
        .size()
        .reset_index(name="Total")
        .sort_values(["OCDE", "Sexo"])
    )

    st.write("#### 📋 Tabla Sexo por OCDE (ordenada por OCDE → Sexo)")
    st.dataframe(tabla_sexo_ocde, use_container_width=True)

    # Pivot para la gráfica
    pivot_ocde = (
        df_ocde_top.groupby(["OCDE", "Sexo"]).size().unstack(fill_value=0)
    )

    st.write("#### 📊 Gráfica Sexo vs OCDE (Top N)")
    st.bar_chart(pivot_ocde)

else:
    st.warning("⚠️ El dataframe no contiene las columnas 'OCDE' y 'Sexo'. Verifica los nombres.")


# Registros de detalle
st.subheader("📄 Detalle de registros financiados filtrados")
st.dataframe(df_filtrado)

# Exportar datos
st.download_button(
    label="📥 Descargar datos filtrados en CSV",
    data=df_filtrado.to_csv(index=False),
    file_name="financiados_filtrados.csv",
    mime="text/csv"
)
