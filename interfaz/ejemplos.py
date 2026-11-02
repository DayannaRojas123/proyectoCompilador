# ejemplos.py
# =====================================================================
# Programas de ejemplo para el editor. Cada botón de "Ejemplos" carga
# uno de estos textos. Solo son datos: no importan nada.
# =====================================================================

EJEMPLO_VALIDO = 'var edad : entero = 2 + 3 * 4;\nmostrar edad;\n'                         # sin errores
EJEMPLO_ERROR_LEXICO = 'var x : entero = 5 @ 3;\n'                                         # '@' no permitido
EJEMPLO_ERROR_SINTACTICO = 'var x : entero = 2 + ;\n'                                      # expresión incompleta
EJEMPLO_ERROR_SEMANTICO = 'var nombre : entero = "hola";\n'                              # tipos incompatibles (ojo: 'y' es palabra reservada)
EJEMPLO_PRECEDENCIA = 'var resultado : entero = (2 + 3) * 4;\nmostrar resultado;\n'        # paréntesis
