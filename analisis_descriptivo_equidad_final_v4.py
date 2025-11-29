import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Configuración para que Matplotlib muestre tildes y caracteres especiales
plt.rcParams['font.family'] = 'DejaVu Sans'

# --- Configuración Inicial ---
FILE_PATH = 'Dataframe1.xlsx'
SHEET_NAME = 'Hoja1'

# Nombres de columnas confirmados por el diagnóstico
COL_GENERO = 'Sexo'
COL_DEPARTAMENTO = 'Depto_nacimi'
COL_AREA = 'OCDE'

# Lógica confirmada por el usuario: TODOS SON FINANCIADOS.
# El análisis se centra en la distribución de la oportunidad.

def cargar_y_limpiar_datos(file_path, sheet_name):
    """Carga los datos y realiza una limpieza básica."""
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        # Limpieza de nombres de columna (eliminando espacios al inicio/final)
        df.columns = [col.strip() for col in df.columns]
        
        # Limpieza básica: convertir a mayúsculas para evitar errores de case-sensitivity
        # y convertir a string para evitar errores de tipo
        df[COL_GENERO] = df[COL_GENERO].astype(str).str.upper().str.strip()
        df[COL_DEPARTAMENTO] = df[COL_DEPARTAMENTO].astype(str).str.upper().str.strip()
        df[COL_AREA] = df[COL_AREA].astype(str).str.upper().str.strip()

        # Filtrar datos nulos en columnas clave
        df.dropna(subset=[COL_GENERO, COL_DEPARTAMENTO, COL_AREA], inplace=True)

        return df
    except FileNotFoundError:
        print(f"Error: Archivo no encontrado en la ruta: {file_path}")
        return None
    except KeyError as e:
        print(f"Error: Columna {e} no encontrada. Verifique los nombres de las columnas en el archivo.")
        return None
    except Exception as e:
        print(f"Error al cargar o limpiar los datos: {e}")
        return None

def analisis_descriptivo_genero(df):
    """Realiza el análisis descriptivo por género (Distribución de la Oportunidad)."""
    print("\n--- 1. Análisis Descriptivo por Género (Distribución de la Oportunidad) ---")

    # 1.1 Distribución de aspirantes financiados por género
    distribucion_genero = df[COL_GENERO].value_counts()
    distribucion_genero_pct = df[COL_GENERO].value_counts(normalize=True).mul(100).round(2)
    
    print("\n1.1 Distribución de Aspirantes Financiados por Género:")
    print(distribucion_genero)
    print("\n1.2 Distribución Porcentual:")
    print(distribucion_genero_pct)

    # 1.3 Visualización: Distribución por Género
    plt.figure(figsize=(8, 6))
    sns.barplot(x=distribucion_genero.index, y=distribucion_genero.values, palette="viridis")
    plt.title('Distribución de Becas Financiadas por Género')
    plt.ylabel('Número de Becas Financiadas')
    plt.xlabel('Género')
    plt.grid(axis='y', linestyle='--')
    plt.savefig('distribucion_genero.png')
    plt.close()
    print("Gráfico 'distribucion_genero.png' generado.")

def analisis_descriptivo_regional(df):
    """Realiza el análisis descriptivo por región (Distribución de la Oportunidad)."""
    print("\n--- 2. Análisis Descriptivo Regional (Distribución de la Oportunidad) ---")

    # 2.1 Top 10 de Departamentos con más aspirantes financiados
    top_departamentos = df[COL_DEPARTAMENTO].value_counts().head(10)
    print("\n2.1 Top 10 Departamentos con Mayor Número de Becas Financiadas:")
    print(top_departamentos)

    # 2.2 Visualización: Distribución Regional (Top 10)
    plt.figure(figsize=(12, 7))
    sns.barplot(x=top_departamentos.index, y=top_departamentos.values, palette="magma")
    plt.title('Top 10 Departamentos con Mayor Número de Becas Financiadas')
    plt.ylabel('Número de Becas Financiadas')
    plt.xlabel('Departamento de Nacimiento')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('distribucion_regional.png')
    plt.close()
    print("Gráfico 'distribucion_regional.png' generado.")

def analisis_brecha_genero_area(df):
    """Analiza la distribución de género por Área de Conocimiento (OCDE)."""
    print("\n--- 3. Análisis de Brecha de Género por Área de Conocimiento (OCDE) ---")

    # 3.1 Distribución de Becas por Género y Área de Conocimiento
    distribucion_brecha = df.groupby([COL_AREA, COL_GENERO]).size().unstack(fill_value=0)
    
    # 3.2 Calcular la proporción de mujeres por área (para medir la equidad)
    
    # Se calcula el total de becas por área
    distribucion_brecha['TOTAL'] = distribucion_brecha.sum(axis=1)
    
    # Se intenta identificar la columna de mujeres (asumiendo 'F' o 'FEMENINO' es el valor)
    col_mujeres = None
    for col in distribucion_brecha.columns:
        if 'F' in col or 'FEMENINO' in col or 'MUJER' in col:
            col_mujeres = col
            break
    
    if col_mujeres:
        distribucion_brecha['PROPORCION_MUJERES'] = (distribucion_brecha[col_mujeres] / distribucion_brecha['TOTAL']) * 100
        distribucion_brecha = distribucion_brecha.sort_values(by='PROPORCION_MUJERES', ascending=True)
        
        print(f"\n3.1 Áreas de Conocimiento con Menor Proporción de Mujeres Financiadas (Top 10):")
        print(distribucion_brecha[['TOTAL', col_mujeres, 'PROPORCION_MUJERES']].head(10))

        # 3.3 Visualización: Proporción de Mujeres por Área (Top 10)
        plt.figure(figsize=(12, 7))
        sns.barplot(x=distribucion_brecha['PROPORCION_MUJERES'].head(10).index, y=distribucion_brecha['PROPORCION_MUJERES'].head(10).values, palette="coolwarm")
        plt.title('Top 10 Áreas de Conocimiento con Menor Proporción de Mujeres Financiadas')
        plt.ylabel('Proporción de Mujeres Financiadas (%)')
        plt.xlabel('Área de Conocimiento (OCDE)')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig('proporcion_mujeres_area.png')
        plt.close()
        print("Gráfico 'proporcion_mujeres_area.png' generado.")

    else:
        print("\nADVERTENCIA: No se pudo identificar la columna de mujeres para calcular la proporción. Verifique los valores de la columna 'Sexo'.")
        print("Valores únicos en la columna Sexo:", df[COL_GENERO].unique())


if __name__ == "__main__":
    # 1. Cargar y Limpiar Datos
    df_analisis = cargar_y_limpiar_datos(FILE_PATH, SHEET_NAME)

    if df_analisis is not None:
        # 2. Análisis Descriptivo por Género
        analisis_descriptivo_genero(df_analisis)

        # 3. Análisis Descriptivo Regional
        analisis_descriptivo_regional(df_analisis)

        # 4. Análisis de Brecha de Género por Área
        analisis_brecha_genero_area(df_analisis)

        print("\n--- Proceso de Análisis Descriptivo Finalizado ---")
        print("Los resultados en texto se muestran arriba. Los gráficos se guardaron como PNG en el directorio actual.")
