from logica import (
    leer_fechas_existentes,
    generar_rango_fechas,
    detectar_fechas_faltantes,
    consultar_informix,
    agregar_columnas_fecha,
    subir_dataframe
)
from queries import query_cdp
import pandas as pd

def actualizar_cdp(dias_rango, excluir_ultimos_dias=0):
    sheet_name = "CDP"

    # Leer fechas existentes
    fechas_existentes = leer_fechas_existentes(sheet_name)

    # Generar rango de fechas a consultar
    fechas_rango = generar_rango_fechas(dias_rango, excluir_ultimos_dias)

    # Detectar fechas faltantes
    fechas_faltantes = detectar_fechas_faltantes(fechas_existentes, fechas_rango)

    if not fechas_faltantes:
        print("No hay fechas nuevas para CDP.")
        return

    # Consultar Informix
    df_total = consultar_informix(fechas_faltantes, query_cdp)
    if df_total.empty:
        print("No se encontraron datos nuevos en Informix para CDP.")
        return

    # Filtrar las fechas que ya existen
    if 'order_date' in df_total.columns:
        fechas_existentes_str = [d.strftime('%Y-%m-%d') for d in fechas_existentes]
        df_total = df_total[~df_total['order_date'].isin(fechas_existentes_str)]

    # Renombrar columna a 'fecha'
    df_total.rename(columns={'order_date':'fecha'}, inplace=True)

    # Agregar columnas adicionales de fecha (día, mes, año, semana)
    df_total['fecha'] = pd.to_datetime(df_total['fecha'])
    df_total = agregar_columnas_fecha(df_total)

    # Agregar columna "fecha_salida" = fecha + 1 día (datetime real)
    df_total['fecha_salida'] = df_total['fecha'] + pd.Timedelta(days=1)

    # Reordenar columnas para que fecha_salida quede junto a fecha
    cols = df_total.columns.tolist()
    fecha_idx = cols.index('fecha')
    if 'fecha_salida' in cols:
        cols.remove('fecha_salida')
        cols.insert(fecha_idx + 1, 'fecha_salida')
        df_total = df_total[cols]

    # ✅ reemplazar NaN por 0 en todas las columnas numéricas
    num_cols = df_total.select_dtypes(include='number').columns
    df_total[num_cols] = df_total[num_cols].fillna(0)

    # Subir dataframe a Excel
    subir_dataframe(sheet_name, df_total)
    print("CDP actualizado correctamente!")
