# analizador_sintactico.py
# =====================================================================
# Analizador sintáctico por descenso recursivo del lenguaje educativo.
#
# ---------------------------------------------------------------------
# EJEMPLO TRAZADO
# ---------------------------------------------------------------------
# Entrada (tokens del lexer):
#   var x : entero = 2 + 3 * 4;
#
# Salida (AST + errores):
#   ["programa", [
#     ["declaracion", "x", "entero",
#       ["binaria", "+",
#         ["entero", 2, 1, 18],
#         ["binaria", "*",
#           ["entero", 3, 1, 22],
#           ["entero", 4, 1, 26],
#           1, 24],
#         1, 20],
#       1, 5]
#   ]]
#   errores = []
#
# Con error:
#   var x : entero = 5        (falta ';')
#   errores = [["SINTACTICO", "Se esperaba ';' al final", 1, 28]]
# ---------------------------------------------------------------------

# Importamos las constantes de tipos de token que necesita el parser.
from lenguaje import (
    TIPO_PALABRA_RESERVADA, TIPO_TIPO_DATO, TIPO_BOOLEANO_LITERAL,     # categorías especiales
    TIPO_OPERADOR_Y, TIPO_OPERADOR_O, TIPO_OPERADOR_NO,                # operadores lógicos
    TIPO_IDENTIFICADOR, TIPO_ENTERO, TIPO_DECIMAL, TIPO_CADENA,         # literales y nombres
    TIPO_ASIGNACION, TIPO_SUMA, TIPO_RESTA, TIPO_MULTIPLICACION, TIPO_DIVISION,  # operadores básicos
    TIPO_IGUAL_IGUAL, TIPO_DIFERENTE, TIPO_MENOR, TIPO_MAYOR,           # relacionales
    TIPO_MENOR_IGUAL, TIPO_MAYOR_IGUAL,                                 # relacionales compuestos
    TIPO_PARENTESIS_IZQUIERDO, TIPO_PARENTESIS_DERECHO,                 # paréntesis
    TIPO_DOS_PUNTOS, TIPO_PUNTO_COMA, TIPO_FIN                           # puntuación y fin
)

# Variables globales del módulo: aquí vive el estado del parser.
tokens_actuales = []       # lista de tokens que se está recorriendo
posicion_actual = 0        # índice del token que se está mirando
errores_sintacticos = []   # lista acumulada de errores detectados

# ------------------ Diagrama: tipo_token_actual ----------------------
#   [] -> ¿posicion_actual fuera de rango? --sí--> FIN
#                                    --no--> tokens[posicion][0]
# ---------------------------------------------------------------------
def tipo_token_actual():
    if posicion_actual >= len(tokens_actuales):   # si nos pasamos del final
        return TIPO_FIN                            # tratarlo como FIN
    return tokens_actuales[posicion_actual][0]     # categoría del token actual

# ------------------ Diagrama: valor_token_actual ---------------------
#   [] -> leer valor_interpretado -> ¿es None? --sí--> usar lexema
#                                           --no--> usar valor
# ---------------------------------------------------------------------
def valor_token_actual():
    if posicion_actual >= len(tokens_actuales):              # fuera de rango
        return ""                                            # cadena vacía
    valor = tokens_actuales[posicion_actual][4]              # posición 4 = valor interpretado
    if valor is None:                                        # si no hay valor interpretado
        return tokens_actuales[posicion_actual][1]           # usar el lexema
    return valor                                             # devolver el valor interpretado

# ------------------ Diagrama: linea_token_actual ---------------------
#   [] -> tokens[posicion][2]  ó 0 si fuera de rango
# ---------------------------------------------------------------------
def linea_token_actual():
    if posicion_actual >= len(tokens_actuales):   # fuera de rango
        return 0                                   # línea desconocida
    return tokens_actuales[posicion_actual][2]     # número de línea del token actual

# ------------------ Diagrama: columna_token_actual -------------------
#   [] -> tokens[posicion][3]  ó 0 si fuera de rango
# ---------------------------------------------------------------------
def columna_token_actual():
    if posicion_actual >= len(tokens_actuales):   # fuera de rango
        return 0                                   # columna desconocida
    return tokens_actuales[posicion_actual][3]     # columna del token actual

# ------------------ Diagrama: fin_de_tokens --------------------------
#   [] -> ¿posicion fuera de rango o tipo == FIN? -> True / False
# ---------------------------------------------------------------------
def fin_de_tokens():
    if posicion_actual >= len(tokens_actuales):   # fuera de rango
        return True                                # se considera fin
    return tipo_token_actual() == TIPO_FIN         # también fin si el token es FIN

# ------------------ Diagrama: avanzar_token --------------------------
#   [pos] -> ¿pos < len-1? --sí--> pos+1
#                         --no--> no mover
# ---------------------------------------------------------------------
def avanzar_token():
    global posicion_actual                         # modificamos el índice global
    if posicion_actual < len(tokens_actuales) - 1: # si no estamos en el último
        posicion_actual += 1                       # avanzar una posición

# ------------------ Diagrama: reportar_error -------------------------
#   [mensaje] -> agregar [SINTACTICO, mensaje, linea, col] a errores
# ---------------------------------------------------------------------
def reportar_error(mensaje):
    linea = linea_token_actual()                                     # línea actual
    columna = columna_token_actual()                                 # columna actual
    errores_sintacticos.append(["SINTACTICO", mensaje, linea, columna])  # acumular error

# ------------------ Diagrama: consumir_tipo_esperado -----------------
#   [tipo, msg] -> ¿tipo_actual == tipo? --sí--> avanzar y devolver True
#                                     --no--> reportar error y False
# ---------------------------------------------------------------------
def consumir_tipo_esperado(tipo_esperado, mensaje_error):
    if tipo_token_actual() != tipo_esperado:       # comparar con el esperado
        reportar_error(mensaje_error)              # si no coincide, error
        return False                               # señal de fallo
    avanzar_token()                                # sí coincide: consumirlo
    return True                                    # señal de éxito

# ------------------ Diagrama: analizar_sintactico --------------------
#   [tokens] -> reiniciar estado -> iterar mientras no fin:
#     intentar analizar_instruccion
#     si hubo error -> recuperar saltando hasta ';' o FIN
#   devolver (AST, errores)
# ---------------------------------------------------------------------
def analizar_sintactico(tokens):
    global tokens_actuales, posicion_actual, errores_sintacticos  # estado global
    tokens_actuales = tokens                                      # fijar los tokens
    posicion_actual = 0                                           # empezar por el primero
    errores_sintacticos = []                                      # lista limpia de errores
    lista_instrucciones = []                                      # AST en construcción
    while not fin_de_tokens():                                    # mientras haya tokens
        errores_antes = len(errores_sintacticos)                  # contar errores previos
        instruccion = analizar_instruccion()                      # intentar analizar
        if instruccion is not None:                               # si se construyó
            lista_instrucciones.append(instruccion)               # guardar en el AST
        if len(errores_sintacticos) > errores_antes:              # si hubo error
            while not fin_de_tokens() and tipo_token_actual() != TIPO_PUNTO_COMA:  # saltar
                avanzar_token()                                   # consumir token a token
            if not fin_de_tokens():                               # si encontramos ';'
                avanzar_token()                                   # consumirlo para continuar
    return ["programa", lista_instrucciones], errores_sintacticos # resultado final

# ------------------ Diagrama: analizar_instruccion -------------------
#   [tipo actual] -> ¿var? -> declaracion
#                 -> ¿mostrar? -> mostrar
#                 -> ¿identificador? -> asignacion
#                 -> otro -> error
# ---------------------------------------------------------------------
def analizar_instruccion():
    tipo = tipo_token_actual()                                     # categoría actual
    if tipo == TIPO_PALABRA_RESERVADA:                             # podría ser var o mostrar
        palabra = valor_token_actual()                             # cuál palabra reservada es
        if palabra == "var":                                       # declaración
            return analizar_declaracion()                          # delegar
        if palabra == "mostrar":                                   # instrucción mostrar
            return analizar_mostrar()                              # delegar
    if tipo == TIPO_IDENTIFICADOR:                                 # asignación
        return analizar_asignacion()                               # delegar
    reportar_error("Se esperaba una instruccion valida")           # nada de lo anterior
    return None                                                    # fallo

# ------------------ Diagrama: analizar_declaracion -------------------
#   var id : tipo = exp ;  -> nodo declaracion
# ---------------------------------------------------------------------
def analizar_declaracion():
    avanzar_token()                                                # consumir 'var'
    if tipo_token_actual() != TIPO_IDENTIFICADOR:                  # verificar identificador
        reportar_error("Se esperaba nombre de variable despues de 'var'")  # error
        return None                                                # abortar
    linea = linea_token_actual()                                   # posición del nombre
    columna = columna_token_actual()                               # posición del nombre
    nombre = valor_token_actual()                                  # guardar el nombre
    avanzar_token()                                                # consumir el nombre
    if not consumir_tipo_esperado(TIPO_DOS_PUNTOS, "Se esperaba ':' despues del nombre"):
        return None                                                # sin ':' no continuar
    if tipo_token_actual() != TIPO_TIPO_DATO:                      # verificar tipo de dato
        reportar_error("Se esperaba un tipo de dato (entero, decimal, cadena, booleano)")
        return None                                                # sin tipo no continuar
    tipo = valor_token_actual()                                    # guardar el tipo
    avanzar_token()                                                # consumir el tipo
    if not consumir_tipo_esperado(TIPO_ASIGNACION, "Se esperaba '=' despues del tipo"):
        return None                                                # sin '=' no continuar
    expresion = analizar_expresion()                               # analizar el lado derecho
    if expresion is None:                                          # si la expresión falló
        return None                                                # abortar
    if not consumir_tipo_esperado(TIPO_PUNTO_COMA, "Se esperaba ';' al final"):
        return None                                                # sin ';' no continuar
    return ["declaracion", nombre, tipo, expresion, linea, columna]  # AST de declaración

# ------------------ Diagrama: analizar_asignacion --------------------
#   id = exp ;  -> nodo asignacion
# ---------------------------------------------------------------------
def analizar_asignacion():
    linea = linea_token_actual()                                   # posición del identificador
    columna = columna_token_actual()                               # posición del identificador
    nombre = valor_token_actual()                                  # guardar nombre
    avanzar_token()                                                # consumir el identificador
    if not consumir_tipo_esperado(TIPO_ASIGNACION, "Se esperaba '=' despues del nombre"):
        return None                                                # sin '=' no continuar
    expresion = analizar_expresion()                               # analizar el lado derecho
    if expresion is None:                                          # si falló la expresión
        return None                                                # abortar
    if not consumir_tipo_esperado(TIPO_PUNTO_COMA, "Se esperaba ';' al final"):
        return None                                                # sin ';' no continuar
    return ["asignacion", nombre, expresion, linea, columna]       # AST de asignación

# ------------------ Diagrama: analizar_mostrar -----------------------
#   mostrar exp ;  -> nodo mostrar
# ---------------------------------------------------------------------
def analizar_mostrar():
    linea = linea_token_actual()                                   # posición de 'mostrar'
    columna = columna_token_actual()                               # posición de 'mostrar'
    avanzar_token()                                                # consumir 'mostrar'
    expresion = analizar_expresion()                               # analizar la expresión
    if expresion is None:                                          # si falló la expresión
        return None                                                # abortar
    if not consumir_tipo_esperado(TIPO_PUNTO_COMA, "Se esperaba ';' al final"):
        return None                                                # sin ';' no continuar
    return ["mostrar", expresion, linea, columna]                  # AST de mostrar

# ------------------ Diagrama: analizar_expresion ---------------------
#   [] -> analizar_expresion_logica (nivel más bajo de precedencia)
# ---------------------------------------------------------------------
def analizar_expresion():
    return analizar_expresion_logica()                             # delegar al nivel 'o'

# ------------------ Diagrama: analizar_expresion_logica --------------
#   exp_y { 'o' exp_y }  -> asociativa por izquierda
# ---------------------------------------------------------------------
def analizar_expresion_logica():
    izquierda = analizar_expresion_y()                             # primer operando
    if izquierda is None:                                          # si falló
        return None                                                # propagar fallo
    while tipo_token_actual() == TIPO_OPERADOR_O:                  # mientras haya 'o'
        operador = valor_token_actual()                            # guardar 'o'
        linea = linea_token_actual()                               # línea del operador
        columna = columna_token_actual()                           # columna del operador
        avanzar_token()                                            # consumir 'o'
        derecha = analizar_expresion_y()                           # operando derecho
        if derecha is None:                                        # si falló
            return None                                            # propagar
        izquierda = ["binaria", operador, izquierda, derecha, linea, columna]  # nuevo nodo
    return izquierda                                               # devolver acumulado

# ------------------ Diagrama: analizar_expresion_y -------------------
#   exp_no { 'y' exp_no }  -> asociativa por izquierda
# ---------------------------------------------------------------------
def analizar_expresion_y():
    izquierda = analizar_expresion_no()                            # primer operando
    if izquierda is None:                                          # si falló
        return None                                                # propagar
    while tipo_token_actual() == TIPO_OPERADOR_Y:                  # mientras haya 'y'
        operador = valor_token_actual()                            # guardar 'y'
        linea = linea_token_actual()                               # línea del operador
        columna = columna_token_actual()                           # columna del operador
        avanzar_token()                                            # consumir 'y'
        derecha = analizar_expresion_no()                          # operando derecho
        if derecha is None:                                        # si falló
            return None                                            # propagar
        izquierda = ["binaria", operador, izquierda, derecha, linea, columna]  # nuevo nodo
    return izquierda                                               # devolver acumulado

# ------------------ Diagrama: analizar_expresion_no ------------------
#   ['no'] exp_relacional  -> unaria
# ---------------------------------------------------------------------
def analizar_expresion_no():
    if tipo_token_actual() == TIPO_OPERADOR_NO:                    # si empieza con 'no'
        linea = linea_token_actual()                               # línea del 'no'
        columna = columna_token_actual()                           # columna del 'no'
        avanzar_token()                                            # consumir 'no'
        operando = analizar_expresion_relacional()                 # analizar operando
        if operando is None:                                       # si falló
            return None                                            # propagar
        return ["unaria", "no", operando, linea, columna]          # nodo unario
    return analizar_expresion_relacional()                         # sin 'no': siguiente nivel

# ------------------ Diagrama: analizar_expresion_relacional ----------
#   exp_aritmetica [op_relacional exp_aritmetica]  -> no encadenado
#   ¿sigue otro operador relacional? -> error explícito
# ---------------------------------------------------------------------
def analizar_expresion_relacional():
    izquierda = analizar_expresion_aritmetica()                    # primer operando
    if izquierda is None:                                          # si falló
        return None                                                # propagar
    operadores_relacionales = [TIPO_IGUAL_IGUAL, TIPO_DIFERENTE, TIPO_MENOR,
                               TIPO_MAYOR, TIPO_MENOR_IGUAL, TIPO_MAYOR_IGUAL]  # lista
    if tipo_token_actual() not in operadores_relacionales:         # ¿hay operador relacional?
        return izquierda                                           # no: devolver lo que hay
    operador = valor_token_actual()                                # guardar el operador
    linea = linea_token_actual()                                   # línea del operador
    columna = columna_token_actual()                               # columna del operador
    avanzar_token()                                                # consumir el operador
    derecha = analizar_expresion_aritmetica()                      # operando derecho
    if derecha is None:                                            # si falló
        return None                                                # propagar
    if tipo_token_actual() in operadores_relacionales:             # NUEVO: ¿viene otro relacional?
        reportar_error("Los operadores relacionales no se pueden encadenar")  # NUEVO: mensaje preciso
        return None                                                # NUEVO: abortar (recuperación global se encarga)
    return ["binaria", operador, izquierda, derecha, linea, columna]  # nodo binario normal

# ------------------ Diagrama: analizar_expresion_aritmetica ----------
#   termino { ('+' | '-') termino }  -> asociativa por izquierda
# ---------------------------------------------------------------------
def analizar_expresion_aritmetica():
    izquierda = analizar_termino()                                 # primer operando
    if izquierda is None:                                          # si falló
        return None                                                # propagar
    while tipo_token_actual() in [TIPO_SUMA, TIPO_RESTA]:          # mientras haya + o -
        operador = valor_token_actual()                            # guardar operador
        linea = linea_token_actual()                               # línea del operador
        columna = columna_token_actual()                           # columna del operador
        avanzar_token()                                            # consumirlo
        derecha = analizar_termino()                               # operando derecho
        if derecha is None:                                        # si falló
            return None                                            # propagar
        izquierda = ["binaria", operador, izquierda, derecha, linea, columna]  # acumular
    return izquierda                                               # devolver acumulado

# ------------------ Diagrama: analizar_termino -----------------------
#   factor { ('*' | '/') factor }  -> asociativa por izquierda
# ---------------------------------------------------------------------
def analizar_termino():
    izquierda = analizar_factor()                                  # primer operando
    if izquierda is None:                                          # si falló
        return None                                                # propagar
    while tipo_token_actual() in [TIPO_MULTIPLICACION, TIPO_DIVISION]:  # mientras * o /
        operador = valor_token_actual()                            # guardar operador
        linea = linea_token_actual()                               # línea del operador
        columna = columna_token_actual()                           # columna del operador
        avanzar_token()                                            # consumirlo
        derecha = analizar_factor()                                # operando derecho
        if derecha is None:                                        # si falló
            return None                                            # propagar
        izquierda = ["binaria", operador, izquierda, derecha, linea, columna]  # acumular
    return izquierda                                               # devolver acumulado

# ------------------ Diagrama: analizar_factor ------------------------
#   ['-'] primario  -> maneja el menos unario
# ---------------------------------------------------------------------
def analizar_factor():
    if tipo_token_actual() == TIPO_RESTA:                          # si empieza con '-'
        linea = linea_token_actual()                               # línea del '-'
        columna = columna_token_actual()                           # columna del '-'
        avanzar_token()                                            # consumir '-'
        operando = analizar_primario()                             # analizar el primario
        if operando is None:                                       # si falló
            return None                                            # propagar
        return ["unaria", "-", operando, linea, columna]           # nodo unario negativo
    return analizar_primario()                                     # sin '-' unario

# ------------------ Diagrama: nodo_literal ---------------------------
#   [nombre_nodo] -> construir [nombre_nodo, valor, linea, col] y avanzar
# ---------------------------------------------------------------------
def nodo_literal(nombre_nodo):
    resultado = [nombre_nodo, valor_token_actual(), linea_token_actual(), columna_token_actual()]
    avanzar_token()                                                # consumir el literal
    return resultado                                               # nodo construido

# ------------------ Diagrama: analizar_primario ----------------------
#   entero | decimal | cadena | booleano | identificador | '(' exp ')'
# ---------------------------------------------------------------------
def analizar_primario():
    tipo = tipo_token_actual()                                     # categoría actual
    if tipo == TIPO_ENTERO:                                        # literal entero
        return nodo_literal("entero")                              # construir nodo
    if tipo == TIPO_DECIMAL:                                       # literal decimal
        return nodo_literal("decimal")                             # construir nodo
    if tipo == TIPO_CADENA:                                        # literal cadena
        return nodo_literal("cadena")                              # construir nodo
    if tipo == TIPO_BOOLEANO_LITERAL:                              # literal booleano
        return nodo_literal("booleano")                            # construir nodo
    if tipo == TIPO_IDENTIFICADOR:                                 # referencia a variable
        return nodo_literal("identificador")                       # construir nodo
    if tipo == TIPO_PARENTESIS_IZQUIERDO:                          # agrupación
        return analizar_agrupacion_parentesis()                    # delegar
    reportar_error("Se esperaba un valor, identificador o parentesis")  # nada aplica
    return None                                                    # fallo

# ------------------ Diagrama: analizar_agrupacion_parentesis ---------
#   '(' exp ')'  -> devuelve el AST de exp (paréntesis no crea nodo propio)
# ---------------------------------------------------------------------
def analizar_agrupacion_parentesis():
    avanzar_token()                                                # consumir '('
    expresion = analizar_expresion()                               # analizar dentro
    if expresion is None:                                          # si falló
        return None                                                # propagar
    if tipo_token_actual() != TIPO_PARENTESIS_DERECHO:             # verificar ')'
        reportar_error("Se esperaba ')' para cerrar parentesis")   # error
        return None                                                # abortar
    avanzar_token()                                                # consumir ')'
    return expresion                                               # devolver la expresión interna

# ------------------ Diagrama: formatear_arbol_a_texto ----------------
#   [nodo, nivel] -> según tipo: programa | literal | instruccion | operacion
# ---------------------------------------------------------------------
def formatear_arbol_a_texto(nodo, nivel):
    sangria = "    " * nivel                                       # indentación
    tipo_nodo = nodo[0]                                            # categoría del nodo
    if tipo_nodo == "programa":                                    # programa completo
        return formatear_programa(nodo, nivel)                     # delegar
    if tipo_nodo in ["entero", "decimal", "cadena", "booleano", "identificador"]:  # literales
        return sangria + tipo_nodo + ": " + str(nodo[1]) + "\n"    # una línea
    if tipo_nodo in ["declaracion", "asignacion", "mostrar"]:      # instrucciones
        return formatear_instruccion(nodo, nivel)                  # delegar
    if tipo_nodo in ["binaria", "unaria"]:                         # operaciones
        return formatear_operacion(nodo, nivel)                    # delegar
    return sangria + str(nodo) + "\n"                              # por si acaso

# ------------------ Diagrama: formatear_programa ---------------------
#   ['programa', instr...] -> "Programa" + cada instrucción indentada
# ---------------------------------------------------------------------
def formatear_programa(nodo, nivel):
    sangria = "    " * nivel                                       # indentación del programa
    resultado = sangria + "Programa\n"                             # encabezado
    for instruccion in nodo[1]:                                    # recorrer instrucciones
        resultado += formatear_arbol_a_texto(instruccion, nivel + 1)  # agregar cada una
    return resultado                                               # texto completo

# ------------------ Diagrama: formatear_instruccion ------------------
#   declaracion | asignacion | mostrar -> texto indentado
# ---------------------------------------------------------------------
def formatear_instruccion(nodo, nivel):
    sangria = "    " * nivel                                       # indentación
    if nodo[0] == "declaracion":                                   # declaración
        cabecera = sangria + "Declaracion " + nodo[1] + " : " + nodo[2] + "\n"  # línea
        return cabecera + formatear_arbol_a_texto(nodo[3], nivel + 1)  # + expresión
    if nodo[0] == "asignacion":                                    # asignación
        cabecera = sangria + "Asignacion " + nodo[1] + "\n"        # línea
        return cabecera + formatear_arbol_a_texto(nodo[2], nivel + 1)  # + expresión
    cabecera = sangria + "Mostrar\n"                               # mostrar
    return cabecera + formatear_arbol_a_texto(nodo[1], nivel + 1)  # + expresión

# ------------------ Diagrama: formatear_operacion --------------------
#   binaria | unaria -> texto con hijos indentados
# ---------------------------------------------------------------------
def formatear_operacion(nodo, nivel):
    sangria = "    " * nivel                                       # indentación
    if nodo[0] == "binaria":                                       # operación binaria
        cabecera = sangria + "Binaria: " + nodo[1] + "\n"          # encabezado
        cabecera += formatear_arbol_a_texto(nodo[2], nivel + 1)    # hijo izquierdo
        return cabecera + formatear_arbol_a_texto(nodo[3], nivel + 1)  # hijo derecho
    cabecera = sangria + "Unaria: " + nodo[1] + "\n"               # operación unaria
    return cabecera + formatear_arbol_a_texto(nodo[2], nivel + 1)  # único hijo

# ------------------ Bloque de comprobación manual ---------------------
if __name__ == "__main__":
    from analizador_lexico import analizar_lexico                  # importamos el lexer
    codigo_demostracion = 'var x : entero = 2 + 3 * 4;'            # programa de ejemplo
    lista_tokens, _ = analizar_lexico(codigo_demostracion)         # obtener tokens
    arbol, lista_errores = analizar_sintactico(lista_tokens)       # analizar
    print(formatear_arbol_a_texto(arbol, 0))                       # imprimir el árbol
    print("Errores:", lista_errores)                               # imprimir errores