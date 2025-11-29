import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Configuración para que Matplotlib muestre tildes y caracteres especiales
plt.rcParams['font.family'] = 'DejaVu Sans'

# --- Configuración Inicial ---
FILE_PATH = 'Dataframe1.xlsx'
SHEET_NAME = 'Hoja1'

# Nombres de columnas confirmados
COL_GENERO = 'Sexo'
COL_DEPARTAMENTO = 'Depto_nacimi'
COL_AREA = 'OCDE'
COL_ANIO = 'Año de la convocatoria' # Nueva columna para el análisis anual

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
        
        # Asegurar que la columna de año sea numérica y filtrar valores no válidos
        df[COL_ANIO] = pd.to_numeric(df[COL_ANIO], errors='coerce').astype('Int64')

        # Filtrar datos nulos en columnas clave
        df.dropna(subset=[COL_GENERO, COL_DEPARTAMENTO, COL_AREA, COL_ANIO], inplace=True)

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

def analisis_temporal_genero(df):
    """Analiza la distribución de becas por género a lo largo de los años."""
    print("\n--- 1. Análisis Temporal por Género ---")

    # 1.1 Distribución de becas por año y género
    distribucion_anual = df.groupby([COL_ANIO, COL_GENERO]).size().unstack(fill_value=0)
    
    # 1.2 Calcular la proporción de mujeres por año
    col_mujeres = None
    for col in distribucion_anual.columns:
        if 'F' in col or 'FEMENINO' in col or 'MUJER' in col:
            col_mujeres = col
            break
    
    if col_mujeres:
        distribucion_anual['TOTAL'] = distribucion_anual.sum(axis=1)
        distribucion_anual['PROPORCION_MUJERES'] = (distribucion_anual[col_mujeres] / distribucion_anual['TOTAL']) * 100
        
        print("\n1.1 Distribución Anual de Becas por Género y Proporción de Mujeres:")
        print(distribucion_anual[[col_mujeres, 'TOTAL', 'PROPORCION_MUJERES']])

        # 1.3 Visualización: Evolución de la Proporción de Mujeres
        plt.figure(figsize=(10, 6))
        sns.lineplot(x=distribucion_anual.index, y=distribucion_anual['PROPORCION_MUJERES'], marker='o')
        plt.title('Evolución Anual de la Proporción de Mujeres Financiadas')
        plt.ylabel('Proporción de Mujeres Financiadas (%)')
        plt.xlabel('Año de la Convocatoria')
        plt.grid(axis='y', linestyle='--')
        plt.savefig('evolucion_proporcion_mujeres.png')
        plt.close()
        print("Gráfico 'evolucion_proporcion_mujeres.png' generado.")

    else:
        print("\nADVERTENCIA: No se pudo identificar la columna de mujeres para el análisis temporal. Verifique los valores de la columna 'Sexo'.")
        print("Valores únicos en la columna Sexo:", df[COL_GENERO].unique())

def analisis_temporal_regional(df):
    """Analiza la distribución de becas por región a lo largo de los años."""
    print("\n--- 2. Análisis Temporal Regional ---")

    # 2.1 Departamentos que han ganado más relevancia anualmente (ej. los que crecen más rápido)
    distribucion_anual_regional = df.groupby([COL_ANIO, COL_DEPARTAMENTO]).size().unstack(fill_value=0)
    
    # 2.2 Visualización: Evolución de los Top 5 Departamentos
    top_5_departamentos = df[COL_DEPARTAMENTO].value_counts().head(5).index
    df_top_5 = distribucion_anual_regional[top_5_departamentos]
    
    plt.figure(figsize=(12, 7))
    df_top_5.plot(kind='line', marker='o', ax=plt.gca())
    plt.title('Evolución Anual del Número de Becas Financiadas (Top 5 Departamentos)')
    plt.ylabel('Número de Becas Financiadas')
    plt.xlabel('Año de la Convocatoria')
    plt.grid(axis='y', linestyle='--')
    plt.legend(title='Departamento', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig('evolucion_regional.png')
    plt.close()
    print("Gráfico 'evolucion_regional.png' generado.")

def analisis_temporal_area(df):
    """Analiza la distribución de becas por área de conocimiento a lo largo de los años."""
    print("\n--- 3. Análisis Temporal por Área de Conocimiento ---")

    # 3.1 Evolución de la proporción de mujeres en INGENIERÍA Y TECNOLOGÍA (ejemplo de brecha)
    df_area = df[df[COL_AREA] == 'INGENIERÍA Y TECNOLOGÍA']
    
    if not df_area.empty:
        distribucion_anual_area = df_area.groupby([COL_ANIO, COL_GENERO]).size().unstack(fill_value=0)
        
        col_mujeres = None
        for col in distribucion_anual_area.columns:
            if 'F' in col or 'FEMENINO' in col or 'MUJER' in col:
                col_mujeres = col
                break
        
        if col_mujeres:
            distribucion_anual_area['TOTAL'] = distribucion_anual_area.sum(axis=1)
            distribucion_anual_area['PROPORCION_MUJERES'] = (distribucion_anual_area[col_mujeres] / distribucion_anual_area['TOTAL']) * 100
            
            print("\n3.1 Evolución de la Proporción de Mujeres en INGENIERÍA Y TECNOLOGÍA:")
            print(distribucion_anual_area[['PROPORCION_MUJERES']])

            # 3.2 Visualización: Evolución de la Proporción de Mujeres en Ingeniería
            plt.figure(figsize=(10, 6))
            sns.lineplot(x=distribucion_anual_area.index, y=distribucion_anual_area['PROPORCION_MUJERES'], marker='o')
            plt.title('Evolución de la Proporción de Mujeres Financiadas en Ingeniería y Tecnología')
            plt.ylabel('Proporción de Mujeres Financiadas (%)')
            plt.xlabel('Año de la Convocatoria')
            plt.grid(axis='y', linestyle='--')
            plt.savefig('evolucion_mujeres_ingenieria.png')
            plt.close()
            print("Gráfico 'evolucion_mujeres_ingenieria.png' generado.")
        else:
            print("\nADVERTENCIA: No se pudo identificar la columna de mujeres para el análisis temporal por área.")
    else:
        print("\nADVERTENCIA: No hay datos para 'INGENIERÍA Y TECNOLOGÍA' después de la limpieza.")


if __name__ == "__main__":
    # 1. Cargar y Limpiar Datos
    df_analisis = cargar_y_limpiar_datos(FILE_PATH, SHEET_NAME)

    if df_analisis is not None:
        # 2. Análisis Temporal por Género
        analisis_temporal_genero(df_analisis)

        # 3. Análisis Temporal Regional
        analisis_temporal_regional(df_analisis)

        # 4. Análisis Temporal por Área de Conocimiento
        analisis_temporal_area(df_analisis)

        print("\n--- Proceso de Análisis Descriptivo Anual Finalizado ---")
        print("Los resultados en texto se muestran arriba. Los gráficos se guardaron como PNG en el directorio actual.")
