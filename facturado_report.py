from logica import (
    leer_fechas_existentes,
    generar_rango_fechas,
    detectar_fechas_faltantes,
    consultar_informix,
    agregar_columnas_fecha,
    subir_dataframe
)
from queries import query_datos
import pandas as pd

def actualizar_facturado(dias_rango, excluir_ultimos_dias=0):
    sheet_name = "Facturado"

    # Leer fechas existentes
    fechas_existentes = leer_fechas_existentes(sheet_name)

    # Generar rango de fechas
    fechas_rango = generar_rango_fechas(dias_rango, excluir_ultimos_dias)

    # Detectar fechas faltantes
    fechas_faltantes = detectar_fechas_faltantes(fechas_existentes, fechas_rango)

    if not fechas_faltantes:
        print("No hay fechas nuevas para actualizar en Facturado.")
        return

    # Consultar Informix solo por fechas faltantes
    df_total = consultar_informix(fechas_faltantes, lambda fecha: query_datos(fecha, fecha))

    if df_total.empty:
        print("No se encontraron datos nuevos en Informix.")
        return

    # Asegurar tipo datetime
    df_total['fecha'] = pd.to_datetime(df_total['fecha'])

    # 🔁 Pivot: una fila por fecha, columnas por tipo de etiqueta
    df_pivot = pd.pivot_table(
        df_total,
        index='fecha',
        columns='label_type_desc',
        values='cajas',
        aggfunc='sum',
        fill_value=0
    ).reset_index()

    # Limpiar nombre del índice de columnas
    df_pivot.columns.name = None

    df_total = df_pivot

    # Agregar columnas año, mes, semana, día
    df_total = agregar_columnas_fecha(df_total)

    # Subir a Excel
    subir_dataframe(sheet_name, df_total)

    print("Reporte Facturado actualizado correctamente!")
