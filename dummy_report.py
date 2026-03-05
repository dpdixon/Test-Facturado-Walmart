from logica import (
    leer_fechas_existentes,
    generar_rango_fechas,
    detectar_fechas_faltantes,
    subir_dataframe,
    consultar_informix_dummy,
    agregar_columnas_fecha
)
from queries import query_dummy
import pandas as pd

def actualizar_dummy(dias_rango: int, excluir_ultimos_dias=0):
    sheet_name = "Dummy"

    fechas_existentes = leer_fechas_existentes(sheet_name)
    fechas_rango = generar_rango_fechas(dias_rango, excluir_ultimos_dias)
    fechas_faltantes = detectar_fechas_faltantes(fechas_existentes, fechas_rango)

    if not fechas_faltantes:
        print("No hay fechas nuevas para Dummy.")
        return

    df_dummy = consultar_informix_dummy(fechas_faltantes, query_dummy)
    if df_dummy.empty:
        print("No se encontraron datos nuevos en Informix para Dummy.")
        return

    # agregar columna 'fecha'
    fechas_faltantes_str = [f.strftime('%Y-%m-%d') for f in fechas_faltantes]
    df_dummy['fecha'] = fechas_faltantes_str

    # convertir valores a numéricos
    df_dummy['Dummy Total'] = pd.to_numeric(df_dummy.iloc[:, 0], errors='coerce').fillna(0).astype(int)

    # ✅ calcular en Python (no fórmula Excel)
    df_dummy['Dummy x 0,28%'] = df_dummy['Dummy Total'] * 0.0028

    # agregar columnas de fecha (día, semana, mes, año)
    df_dummy = agregar_columnas_fecha(df_dummy)

    columnas_finales = ['fecha','Dummy Total','Dummy x 0,28%','año','mes','semana','dia']
    df_dummy_final = df_dummy[columnas_finales]

    subir_dataframe(sheet_name, df_dummy_final)
    print("Dummy actualizado correctamente")
