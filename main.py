from facturado_report import actualizar_facturado
from dummy_report import actualizar_dummy
from cdp_report import actualizar_cdp

DIAS_RANGO = 45

print("\nConsultando Facturado...")
actualizar_facturado(DIAS_RANGO, excluir_ultimos_dias=1)

print("\nConsultando Dummy...")
actualizar_dummy(DIAS_RANGO, excluir_ultimos_dias=1)

print("\nConsultando CDP...")
actualizar_cdp(DIAS_RANGO, excluir_ultimos_dias=2)
