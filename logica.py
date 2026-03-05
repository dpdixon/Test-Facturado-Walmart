import os
import pandas as pd
from datetime import datetime, timedelta
from db_connection import get_connection  # tu conexión Informix

# ruta fija de Excel
EXCEL_FILE = os.path.join(os.environ['OneDriveCommercial'], 'Facturado.xlsx')

# -----------------------------
# Leer fechas existentes en la hoja
# -----------------------------
def leer_fechas_existentes(sheet_name):
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name=sheet_name)
        if 'fecha' in df.columns:
            return [pd.to_datetime(d) for d in df['fecha'].dropna()]
        return []
    except FileNotFoundError:
        return []
    except ValueError:  # sheet no existe
        return []

# -----------------------------
# Generar rango de fechas
# -----------------------------
def generar_rango_fechas(dias_rango, excluir_ultimos_dias=0):
    fecha_fin = datetime.today() - timedelta(days=excluir_ultimos_dias)
    fecha_inicio = fecha_fin - timedelta(days=dias_rango - 1)
    return pd.date_range(fecha_inicio, fecha_fin).tolist()

# -----------------------------
# Detectar fechas faltantes
# -----------------------------
def detectar_fechas_faltantes(fechas_existentes, fechas_rango):
    fechas_existentes_str = [d.strftime('%Y-%m-%d') for d in fechas_existentes]
    return [d for d in fechas_rango if d.strftime('%Y-%m-%d') not in fechas_existentes_str]

# -----------------------------
# Consultar Informix
# -----------------------------
def consultar_informix(fechas_faltantes, query_func):
    conn = get_connection()
    df_total = pd.DataFrame()
    for fecha in fechas_faltantes:
        try:
            query = query_func(fecha)
            df_bloque = pd.read_sql(query, conn)
            if not df_bloque.empty:
                df_total = pd.concat([df_total, df_bloque], ignore_index=True)
        except Exception as e:
            print(f"Error consultando {fecha.strftime('%Y-%m-%d')}: {e}")
    conn.close()
    return df_total

def consultar_informix_dummy(fechas_faltantes, query_func):
    conn = get_connection()
    df_total = pd.DataFrame()
    for fecha in fechas_faltantes:
        try:
            query = query_func(fecha)
            df_bloque = pd.read_sql(query, conn)
            if not df_bloque.empty:
                df_total = pd.concat([df_total, df_bloque.iloc[[0]]], ignore_index=True)
        except Exception as e:
            print(f"Error consultando {fecha.strftime('%Y-%m-%d')}: {e}")
    conn.close()
    return df_total

# -----------------------------
# Agregar columnas de fecha
# -----------------------------
def agregar_columnas_fecha(df):
    df['fecha'] = pd.to_datetime(df['fecha']).dt.date  # solo fecha, sin hora
    df['año'] = pd.to_datetime(df['fecha']).dt.year
    df['mes'] = pd.to_datetime(df['fecha']).dt.month
    df['semana'] = pd.to_datetime(df['fecha']).dt.isocalendar().week
    df['dia'] = pd.to_datetime(df['fecha']).dt.day
    return df

# -----------------------------
# Subir DataFrame a Excel Online
# -----------------------------
def subir_dataframe(sheet_name, df):
    import os
    import pandas as pd

    EXCEL_FILE = os.path.join(os.environ['OneDriveCommercial'], 'Facturado.xlsx')

    # crear Excel si no existe
    if not os.path.exists(EXCEL_FILE):
        df.to_excel(EXCEL_FILE, sheet_name=sheet_name, index=False)
        print(f"Archivo Excel creado con hoja {sheet_name}, {len(df)} filas agregadas.")
        return

    # leer hoja existente
    try:
        df_existente = pd.read_excel(EXCEL_FILE, sheet_name=sheet_name)
    except ValueError:  # sheet no existe
        df_existente = pd.DataFrame()

    # identificar filas nuevas por fecha (solo si hay columna 'fecha')
    if 'fecha' in df_existente.columns and 'fecha' in df.columns:
        df_existente['fecha'] = pd.to_datetime(df_existente['fecha']).dt.date
        df['fecha'] = pd.to_datetime(df['fecha']).dt.date
        fechas_existentes = set(df_existente['fecha'])
        df = df[~df['fecha'].isin(fechas_existentes)]

    if df.empty:
        print("No hay filas nuevas para agregar.")
        return

    # unir existente + nuevo
    df_final = pd.concat([df_existente, df], ignore_index=True)

    # ✅ reemplazar NaN por 0 en todas las columnas numéricas
    num_cols = df_final.select_dtypes(include='number').columns
    df_final[num_cols] = df_final[num_cols].fillna(0)

    # escribir hoja, reemplazando si ya existe
    with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        df_final.to_excel(writer, sheet_name=sheet_name, index=False)

    print(f"{len(df)} filas nuevas agregadas correctamente a {sheet_name}!")