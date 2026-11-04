# ejemplos.py
# =====================================================================
# Programas de ejemplo para el editor. Cada botón de "Ejemplos" carga
# uno de estos textos. Solo son datos: no importan nada.
# =====================================================================

EJEMPLO_VALIDO = 'var edad : entero = 2 + 3 * 4;\nmostrar edad;\n'
EJEMPLO_ERROR_LEXICO = 'var x : entero = 5 @ 3;\n'
EJEMPLO_ERROR_SINTACTICO = 'var x : entero = 2 + ;\n'
EJEMPLO_ERROR_SEMANTICO = 'var nombre : entero = "hola";\n'
EJEMPLO_PRECEDENCIA = 'var resultado : entero = (2 + 3) * 4;\nmostrar resultado;\n'
EJEMPLO_RELACIONAL = 'var x : booleano = 2 < 3 < 4;\n'
EJEMPLO_NO_DECLARADA = 'z = 5;\n'
EJEMPLO_DUPLICADA = 'var x : entero = 1;\nvar x : entero = 2;\n'