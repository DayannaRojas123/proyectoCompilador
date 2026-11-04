# pruebas.py
# =====================================================================
# Pruebas automatizadas del compilador educativo.
#
# Cubre los 12 casos mínimos del enunciado:
#   1. Programa válido en las tres fases
#   2. Comentario correctamente reconocido
#   3. Carácter no permitido (error léxico)
#   4. Cadena sin cerrar (error léxico)
#   5. Expresión sintácticamente incorrecta
#   6. Precedencia de operadores
#   7. Variable no declarada (error semántico)
#   8. Asignación con tipos incompatibles
#   9. Declaración duplicada
#  10. Programa vacío
#  11. Programa corregido después de errores
#  12. Expresión nueva escrita manualmente
#
# ---------------------------------------------------------------------
# EJEMPLO TRAZADO
# ---------------------------------------------------------------------
# Entrada: python pruebas.py
# Salida:
#   ...........                                                      [100%]
#   ------------------------------------------------------------------
#   Ran 12 tests in 0.045s
#   OK
# ---------------------------------------------------------------------

# Importamos unittest (biblioteca estándar) y las tres fases del compilador.
import unittest                                                     # runner de pruebas
from analizador_lexico import analizar_lexico                       # fase léxica
from analizador_sintactico import analizar_sintactico               # fase sintáctica
from analizador_semantico import analizar_semantico                 # fase semántica

# ------------------ Diagrama: preparar_compilacion -------------------
#   [codigo] -> fase1 -> ¿errores? --sí--> cortar y devolver
#                     --no--> fase2 -> ¿errores? --sí--> cortar
#                                   --no--> fase3 -> devolver todo
# ---------------------------------------------------------------------
def preparar_compilacion(codigo_fuente):
    tokens, errores_lexicos = analizar_lexico(codigo_fuente)        # fase 1: tokens
    arbol = None                                                    # se llena solo si fase 1 pasa
    errores_sintacticos = []                                        # se llena solo si fase 1 pasa
    tabla = []                                                      # se llena solo si fase 2 pasa
    errores_semanticos = []                                         # se llena solo si fase 2 pasa
    if len(errores_lexicos) == 0:                                   # sin errores léxicos
        arbol, errores_sintacticos = analizar_sintactico(tokens)    # fase 2: AST
        if len(errores_sintacticos) == 0:                           # sin errores sintácticos
            tabla, errores_semanticos = analizar_semantico(arbol)   # fase 3: símbolos
    return tokens, errores_lexicos, arbol, errores_sintacticos, tabla, errores_semanticos

# ------------------ Diagrama: prueba_programa_valido_en_tres_fases --
#   [codigo válido] -> las tres fases sin error -> tabla con la variable
# ---------------------------------------------------------------------
def prueba_programa_valido_en_tres_fases():
    codigo = 'var x : entero = 5;'                                  # programa mínimo
    tokens, err_lex, arbol, err_sin, tabla, err_sem = preparar_compilacion(codigo)
    assert len(err_lex) == 0                                        # sin errores léxicos
    assert len(err_sin) == 0                                        # sin errores sintácticos
    assert len(err_sem) == 0                                        # sin errores semánticos
    assert len(tabla) == 1                                          # una variable declarada
    assert tabla[0][0] == "x"                                       # se llama 'x'

# ------------------ Diagrama: prueba_comentario_reconocido -----------
#   [codigo con //] -> lexer no genera tokens del comentario
#                  -> primera palabra real en línea 2 columna 1
# ---------------------------------------------------------------------
def prueba_comentario_reconocido_y_linea_correcta():
    codigo = '// comentario\nmostrar 1;'                            # comentario en línea 1
    tokens, err_lex, _, _, _, _ = preparar_compilacion(codigo)
    assert len(err_lex) == 0                                        # sin error léxico
    assert tokens[0][0] == "PALABRA_RESERVADA"                      # primer token real
    assert tokens[0][1] == "mostrar"                                # es 'mostrar'
    assert tokens[0][2] == 2                                        # línea 2
    assert tokens[0][3] == 1                                        # columna 1

# ------------------ Diagrama: prueba_caracter_no_permitido -----------
#   [codigo con @] -> error léxico con "Caracter no permitido"
# ---------------------------------------------------------------------
def prueba_caracter_no_permitido():
    codigo = 'var x : entero = 5 @ 3;'                              # '@' no es válido
    _, err_lex, _, _, _, _ = preparar_compilacion(codigo)
    assert len(err_lex) >= 1                                        # al menos un error
    assert "Caracter no permitido" in err_lex[0][1]                 # mensaje correcto

# ------------------ Diagrama: prueba_cadena_sin_cerrar ---------------
#   [codigo con comilla abierta] -> error "Cadena sin cerrar"
# ---------------------------------------------------------------------
def prueba_cadena_sin_cerrar():
    codigo = 'mostrar "hola;'                                       # falta comilla de cierre
    _, err_lex, _, _, _, _ = preparar_compilacion(codigo)
    assert len(err_lex) >= 1                                        # hubo error
    assert "Cadena sin cerrar" in err_lex[0][1]                     # mensaje correcto

# ------------------ Diagrama: prueba_expresion_sintacticamente_incorrecta
#   [codigo 2 + ;] -> error sintáctico sin bloqueo
# ---------------------------------------------------------------------
def prueba_expresion_sintacticamente_incorrecta():
    codigo = 'var x : entero = 2 + ;'                               # falta operando
    _, _, _, err_sin, _, _ = preparar_compilacion(codigo)
    assert len(err_sin) >= 1                                        # al menos un error
    assert err_sin[0][0] == "SINTACTICO"                            # categoría correcta

# ------------------ Diagrama: prueba_precedencia_multiplicacion ------
#   [2 + 3 * 4] -> árbol: raíz '+' y hijo derecho '*'
# ---------------------------------------------------------------------
def prueba_precedencia_multiplicacion_antes_que_suma():
    codigo = 'var r : entero = 2 + 3 * 4;'                          # expresión con precedencia
    _, _, arbol, err_sin, _, _ = preparar_compilacion(codigo)
    assert len(err_sin) == 0                                        # debe compilar
    declaracion = arbol[1][0]                                       # primer nodo del programa
    expresion = declaracion[3]                                      # expresión de la declaración
    assert expresion[0] == "binaria"                                # nodo binario
    assert expresion[1] == "+"                                      # raíz: suma
    hijo_derecho = expresion[3]                                     # rama derecha del '+'
    assert hijo_derecho[0] == "binaria"                             # también binaria
    assert hijo_derecho[1] == "*"                                   # y es multiplicación

# ------------------ Diagrama: prueba_variable_no_declarada -----------
#   [z = 5 sin declarar] -> error semántico "no declarada"
# ---------------------------------------------------------------------
def prueba_variable_no_declarada():
    codigo = 'z = 5;'                                               # 'z' nunca se declara
    _, _, _, _, _, err_sem = preparar_compilacion(codigo)
    assert len(err_sem) >= 1                                        # hubo error
    assert "no declarada" in err_sem[0][1]                          # mensaje correcto

# ------------------ Diagrama: prueba_asignacion_tipos_incompatibles -
#   [y entero = "hola"] -> error "Tipo incompatible"
# ---------------------------------------------------------------------
def prueba_asignacion_con_tipos_incompatibles():
    codigo = 'var y : entero = 5;\ny = "hola";'                     # asignar cadena a entero
    _, _, _, _, _, err_sem = preparar_compilacion(codigo)
    assert len(err_sem) >= 1                                        # hubo error
    assert "Tipo incompatible" in err_sem[0][1]                     # mensaje correcto

# ------------------ Diagrama: prueba_declaracion_duplicada -----------
#   [x declarada dos veces] -> error "ya declarada"; tabla no crece
# ---------------------------------------------------------------------
def prueba_declaracion_duplicada_genera_error():
    codigo = 'var x : entero = 5;\nvar x : entero = 3;'             # dos declaraciones
    _, _, _, _, tabla, err_sem = preparar_compilacion(codigo)
    assert len(err_sem) >= 1                                        # hubo error
    assert "ya declarada" in err_sem[0][1]                          # mensaje correcto
    assert len(tabla) == 1                                          # solo una entrada

# ------------------ Diagrama: prueba_programa_vacio ------------------
#   [codigo vacío] -> solo token FIN; ninguna fase falla
# ---------------------------------------------------------------------
def prueba_programa_vacio_no_falla():
    tokens, err_lex, arbol, err_sin, _, err_sem = preparar_compilacion('')
    assert len(err_lex) == 0                                        # sin errores léxicos
    assert len(err_sin) == 0                                        # sin errores sintácticos
    assert len(err_sem) == 0                                        # sin errores semánticos
    assert len(tokens) == 1                                         # solo el token FIN
    assert tokens[0][0] == "FIN"                                    # efectivamente es FIN

# ------------------ Diagrama: prueba_programa_corregido --------------
#   [malo -> bueno] -> el compilador no arrastra estado entre llamadas
# ---------------------------------------------------------------------
def prueba_programa_corregido_despues_de_errores():
    codigo_malo = 'var x : entero = 5 @ 3;'                         # programa con error léxico
    _, err_lex_malo, _, _, _, _ = preparar_compilacion(codigo_malo)
    assert len(err_lex_malo) >= 1                                   # el malo falla
    codigo_bueno = 'var x : entero = 5;'                            # versión corregida
    _, err_lex_bueno, _, err_sin, _, err_sem = preparar_compilacion(codigo_bueno)
    assert len(err_lex_bueno) == 0                                  # ya no hay error léxico
    assert len(err_sin) == 0                                        # tampoco sintáctico
    assert len(err_sem) == 0                                        # tampoco semántico

# ------------------ Diagrama: prueba_expresion_manual_nueva ----------
#   [programa inédito] -> las tres fases deben aceptarlo
# ---------------------------------------------------------------------
def prueba_expresion_manual_que_nadie_escribio_antes():
    codigo = 'var a : decimal = 7.5 / 2.5;\nvar b : decimal = a * 4.0;\nmostrar b;'
    tokens, err_lex, arbol, err_sin, tabla, err_sem = preparar_compilacion(codigo)
    assert len(err_lex) == 0                                        # sin error léxico
    assert len(err_sin) == 0                                        # sin error sintáctico
    assert len(err_sem) == 0                                        # sin error semántico
    assert len(tabla) == 2                                          # dos variables declaradas
    assert tabla[0][0] == "a"                                       # la primera es 'a'
    assert tabla[1][0] == "b"                                       # la segunda es 'b'

# ------------------ Diagrama: load_tests -----------------------------
#   [loader, tests, pattern] -> TestSuite con 12 FunctionTestCase
#   (evita usar class / herencia, prohibidas por las reglas del proyecto)
# ---------------------------------------------------------------------
def load_tests(loader_estandar, conjunto_estandar, patron_estandar):
    conjunto = unittest.TestSuite()                                 # suite vacía
    conjunto.addTest(unittest.FunctionTestCase(prueba_programa_valido_en_tres_fases))
    conjunto.addTest(unittest.FunctionTestCase(prueba_comentario_reconocido_y_linea_correcta))
    conjunto.addTest(unittest.FunctionTestCase(prueba_caracter_no_permitido))
    conjunto.addTest(unittest.FunctionTestCase(prueba_cadena_sin_cerrar))
    conjunto.addTest(unittest.FunctionTestCase(prueba_expresion_sintacticamente_incorrecta))
    conjunto.addTest(unittest.FunctionTestCase(prueba_precedencia_multiplicacion_antes_que_suma))
    conjunto.addTest(unittest.FunctionTestCase(prueba_variable_no_declarada))
    conjunto.addTest(unittest.FunctionTestCase(prueba_asignacion_con_tipos_incompatibles))
    conjunto.addTest(unittest.FunctionTestCase(prueba_declaracion_duplicada_genera_error))
    conjunto.addTest(unittest.FunctionTestCase(prueba_programa_vacio_no_falla))
    conjunto.addTest(unittest.FunctionTestCase(prueba_programa_corregido_despues_de_errores))
    conjunto.addTest(unittest.FunctionTestCase(prueba_expresion_manual_que_nadie_escribio_antes))
    return conjunto                                                 # devolver la suite completa

# ------------------ Bloque de arranque del runner --------------------
if __name__ == "__main__":
    unittest.main()                                                 # ejecuta load_tests y reporta