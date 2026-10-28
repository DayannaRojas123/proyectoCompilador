# analizador_lexico.py
# =====================================================================
# Analizador léxico del lenguaje educativo.
# Convierte el texto fuente en una lista de tokens y una lista de
# errores léxicos. Cada token es una lista [tipo, lexema, linea,
# columna, valor_interpretado].
#
# ---------------------------------------------------------------------
# EJEMPLO TRAZADO
# ---------------------------------------------------------------------
# Entrada:
#     var edad : entero = 2 + 3 * 4;
#     mostrar edad;
#
# Salida (tokens, errores):
#     tokens[0]  = [PALABRA_RESERVADA, "var",    1, 1,  "var"]
#     tokens[1]  = [IDENTIFICADOR,     "edad",   1, 5,  "edad"]
#     tokens[2]  = [DOS_PUNTOS,        ":",      1, 10, None]
#     tokens[3]  = [TIPO_DATO,         "entero", 1, 12, "entero"]
#     tokens[4]  = [ASIGNACION,        "=",      1, 19, None]
#     tokens[5]  = [ENTERO,            "2",      1, 21, 2]
#     tokens[6]  = [SUMA,              "+",      1, 23, None]
#     tokens[7]  = [ENTERO,            "3",      1, 25, 3]
#     tokens[8]  = [MULTIPLICACION,    "*",      1, 27, None]
#     tokens[9]  = [ENTERO,            "4",      1, 29, 4]
#     tokens[10] = [PUNTO_COMA,        ";",      1, 30, None]
#     ...
#     tokens[-1] = [FIN,               "",       2, 14, None]
#     errores = []
#
# Entrada con error:
#     var x = 5 @ 3;
# Salida:
#     errores = [["LEXICO", "Caracter no permitido: @", 1, 11]]
# ---------------------------------------------------------------------

# Importamos las constantes del lenguaje (todas las que usamos aquí).
from lenguaje import (
    PALABRAS_RESERVADAS_SIMPLES, TIPOS_DATOS, LITERALES_BOOLEANOS,  # listas de palabras del lenguaje
    TIPO_PALABRA_RESERVADA, TIPO_TIPO_DATO, TIPO_BOOLEANO_LITERAL,  # tipos de palabra reservada
    TIPO_OPERADOR_Y, TIPO_OPERADOR_O, TIPO_OPERADOR_NO,             # operadores lógicos como palabra
    TIPO_IDENTIFICADOR, TIPO_ENTERO, TIPO_DECIMAL, TIPO_CADENA,      # literales y nombres
    TIPO_ASIGNACION, TIPO_SUMA, TIPO_RESTA, TIPO_MULTIPLICACION, TIPO_DIVISION,  # operadores básicos
    TIPO_IGUAL_IGUAL, TIPO_DIFERENTE, TIPO_MENOR, TIPO_MAYOR,        # operadores relacionales
    TIPO_MENOR_IGUAL, TIPO_MAYOR_IGUAL,                              # operadores relacionales dobles
    TIPO_PARENTESIS_IZQUIERDO, TIPO_PARENTESIS_DERECHO,              # paréntesis
    TIPO_DOS_PUNTOS, TIPO_PUNTO_COMA, TIPO_FIN                        # puntuación y fin
)

# ------------------ Diagrama de flujo: saltar_espacios_y_comentarios
#   [posición, línea, col] -> ¿espacio/salto/comentario? --sí--> avanzar
#                                    |                              |
#                                    no                             v
#                                    +--> devolver (pos, línea, col)
# ---------------------------------------------------------------------
def saltar_espacios_y_comentarios(fuente, posicion, linea, columna):
    while posicion < len(fuente):                                             # mientras haya texto por leer
        caracter = fuente[posicion]                                           # carácter actual
        if caracter == '\n':                                                  # si es salto de línea
            posicion += 1                                                     # avanzar posición
            linea += 1                                                        # nueva línea
            columna = 1                                                       # columna vuelve a 1
        elif caracter in ' \t\r':                                             # si es espacio/tab/CR
            posicion += 1                                                     # avanzar posición
            columna += 1                                                      # avanzar columna
        elif caracter == '/' and posicion+1 < len(fuente) and fuente[posicion+1] == '/':  # comentario //
            while posicion < len(fuente) and fuente[posicion] != '\n':        # consumir hasta el fin de línea
                posicion += 1                                                 # avanzar carácter a carácter
                columna += 1                                                  # CORRECCIÓN: también avanzar columna
        else:                                                                 # cualquier otro carácter
            break                                                             # se detiene el salto
    return posicion, linea, columna                                           # devolver estado actualizado

# ------------------ Diagrama de flujo: analizar_identificador --------
#   [posición] -> leer letras/dígitos/_ -> comparar con listas:
#       ¿palabra simple?  -> token PALABRA_RESERVADA
#       ¿tipo de dato?    -> token TIPO_DATO
#       ¿literal bool?    -> token BOOLEANO_LITERAL
#       ¿y/o/no?          -> token OPERADOR_*
#       si no             -> token IDENTIFICADOR
# ---------------------------------------------------------------------
def analizar_identificador(fuente, posicion, linea, columna):
    inicio = posicion                                                          # guardamos el inicio
    while posicion < len(fuente) and (fuente[posicion].isalnum() or fuente[posicion] == '_'):  # letra/dígito/_
        posicion += 1                                                          # avanzar
    lexema = fuente[inicio:posicion]                                           # texto extraído
    nueva_columna = columna + (posicion - inicio)                              # columna desplazada
    if lexema in PALABRAS_RESERVADAS_SIMPLES:                                  # var, mostrar
        return [TIPO_PALABRA_RESERVADA, lexema, linea, columna, lexema], posicion, nueva_columna, None  # token y avance
    if lexema in TIPOS_DATOS:                                                  # entero, decimal, etc.
        return [TIPO_TIPO_DATO, lexema, linea, columna, lexema], posicion, nueva_columna, None  # token de tipo
    if lexema in LITERALES_BOOLEANOS:                                          # verdadero, falso
        valor_booleano = (lexema == "verdadero")                               # True si es 'verdadero'
        return [TIPO_BOOLEANO_LITERAL, lexema, linea, columna, valor_booleano], posicion, nueva_columna, None  # token bool
    if lexema == "y":                                                          # operador AND
        return [TIPO_OPERADOR_Y, lexema, linea, columna, lexema], posicion, nueva_columna, None  # token 'y'
    if lexema == "o":                                                          # operador OR
        return [TIPO_OPERADOR_O, lexema, linea, columna, lexema], posicion, nueva_columna, None  # token 'o'
    if lexema == "no":                                                         # operador NOT
        return [TIPO_OPERADOR_NO, lexema, linea, columna, lexema], posicion, nueva_columna, None  # token 'no'
    return [TIPO_IDENTIFICADOR, lexema, linea, columna, lexema], posicion, nueva_columna, None  # identificador común

# ------------------ Diagrama de flujo: analizar_numero ---------------
#   [posición] -> leer dígitos -> ¿hay punto seguido de dígito?
#       sí -> leer fracción -> token DECIMAL
#       sí pero sin fracción -> error "decimal mal formado"
#       no -> token ENTERO
# ---------------------------------------------------------------------
def analizar_numero(fuente, posicion, linea, columna):
    inicio = posicion                                                          # guardamos el inicio
    while posicion < len(fuente) and fuente[posicion].isdigit():              # leer parte entera
        posicion += 1                                                          # avanzar
    es_decimal = False                                                         # aún no sabemos si es decimal
    if posicion < len(fuente) and fuente[posicion] == '.':                    # hay un punto tras dígitos
        if posicion+1 < len(fuente) and fuente[posicion+1].isdigit():         # y hay dígito después
            es_decimal = True                                                  # confirmamos decimal
            posicion += 1                                                      # saltamos el punto
            while posicion < len(fuente) and fuente[posicion].isdigit():      # leer fracción
                posicion += 1                                                  # avanzar
        else:                                                                  # punto sin dígito: mal formado
            lexema = fuente[inicio:posicion+1]                                 # incluye el punto en el error
            return None, posicion+1, columna+(posicion+1-inicio), ["LEXICO", "Numero decimal mal formado: " + lexema, linea, columna]  # error léxico
    lexema = fuente[inicio:posicion]                                           # texto final del número
    if es_decimal:                                                             # si es decimal
        return [TIPO_DECIMAL, lexema, linea, columna, float(lexema)], posicion, columna+(posicion-inicio), None  # token decimal
    return [TIPO_ENTERO, lexema, linea, columna, int(lexema)], posicion, columna+(posicion-inicio), None  # token entero

# ------------------ Diagrama de flujo: analizar_cadena ---------------
#   [posición] -> saltar comilla de apertura -> leer hasta '"' o fin
#       ¿nueva línea o fin? -> error "cadena sin cerrar"
#       cerrada -> token CADENA con el texto interior
# ---------------------------------------------------------------------
def analizar_cadena(fuente, posicion, linea, columna):
    inicio = posicion                                                          # inicio de la cadena
    posicion += 1                                                              # saltamos comilla de apertura
    while posicion < len(fuente) and fuente[posicion] != '"':                 # leer hasta cierre
        if fuente[posicion] == '\n':                                          # nueva línea dentro de cadena
            return None, posicion, columna, ["LEXICO", "Cadena sin cerrar", linea, columna]  # error léxico
        posicion += 1                                                          # avanzar carácter
    if posicion >= len(fuente):                                                # fin de archivo sin cierre
        return None, posicion, columna, ["LEXICO", "Cadena sin cerrar", linea, columna]  # error léxico
    posicion += 1                                                              # saltamos comilla de cierre
    lexema = fuente[inicio:posicion]                                           # texto completo con comillas
    contenido = lexema[1:-1]                                                   # texto interior sin comillas
    return [TIPO_CADENA, lexema, linea, columna, contenido], posicion, columna+(posicion-inicio), None  # token cadena

# ------------------ Diagrama de flujo: analizar_operador_doble -------
#   [carácter, siguiente] -> ¿'==', '!=', '<=', '>='?
#       sí -> token doble
#       no -> devolver None (que analizar_operador pruebe el simple)
# ---------------------------------------------------------------------
def analizar_operador_doble(fuente, posicion, linea, columna):
    caracter = fuente[posicion]                                                # carácter actual
    siguiente = fuente[posicion+1] if posicion+1 < len(fuente) else ''        # carácter siguiente (o vacío)
    if caracter == '=' and siguiente == '=':                                   # operador ==
        return [TIPO_IGUAL_IGUAL, "==", linea, columna, None], posicion+2, columna+2  # token ==
    if caracter == '!' and siguiente == '=':                                   # operador !=
        return [TIPO_DIFERENTE, "!=", linea, columna, None], posicion+2, columna+2  # token !=
    if caracter == '<' and siguiente == '=':                                   # operador <=
        return [TIPO_MENOR_IGUAL, "<=", linea, columna, None], posicion+2, columna+2  # token <=
    if caracter == '>' and siguiente == '=':                                   # operador >=
        return [TIPO_MAYOR_IGUAL, ">=", linea, columna, None], posicion+2, columna+2  # token >=
    return None, posicion, columna                                             # ningún operador doble

# ------------------ Diagrama de flujo: analizar_operador -------------
#   [posición] -> ¿doble? -> token doble
#             -> ¿uno simple? -> token simple
#             -> ninguno -> error "carácter no permitido"
# ---------------------------------------------------------------------
def analizar_operador(fuente, posicion, linea, columna):
    token_doble, nueva_posicion, nueva_columna = analizar_operador_doble(fuente, posicion, linea, columna)  # probar dobles
    if token_doble is not None:                                                # si encontramos doble
        return token_doble, nueva_posicion, nueva_columna, None                # devolver token doble
    caracter = fuente[posicion]                                                # carácter actual
    if caracter == '=':                                                        # asignación
        return [TIPO_ASIGNACION, "=", linea, columna, None], posicion+1, columna+1, None
    if caracter == '+':                                                        # suma
        return [TIPO_SUMA, "+", linea, columna, None], posicion+1, columna+1, None
    if caracter == '-':                                                        # resta
        return [TIPO_RESTA, "-", linea, columna, None], posicion+1, columna+1, None
    if caracter == '*':                                                        # multiplicación
        return [TIPO_MULTIPLICACION, "*", linea, columna, None], posicion+1, columna+1, None
    if caracter == '/':                                                        # división
        return [TIPO_DIVISION, "/", linea, columna, None], posicion+1, columna+1, None
    if caracter == '<':                                                        # menor que
        return [TIPO_MENOR, "<", linea, columna, None], posicion+1, columna+1, None
    if caracter == '>':                                                        # mayor que
        return [TIPO_MAYOR, ">", linea, columna, None], posicion+1, columna+1, None
    if caracter == '(':                                                        # paréntesis abre
        return [TIPO_PARENTESIS_IZQUIERDO, "(", linea, columna, None], posicion+1, columna+1, None
    if caracter == ')':                                                        # paréntesis cierra
        return [TIPO_PARENTESIS_DERECHO, ")", linea, columna, None], posicion+1, columna+1, None
    if caracter == ':':                                                        # dos puntos
        return [TIPO_DOS_PUNTOS, ":", linea, columna, None], posicion+1, columna+1, None
    if caracter == ';':                                                        # punto y coma
        return [TIPO_PUNTO_COMA, ";", linea, columna, None], posicion+1, columna+1, None
    return None, posicion+1, columna+1, ["LEXICO", "Caracter no permitido: " + caracter, linea, columna]  # error

# ------------------ Diagrama de flujo: analizar_lexico --------------
#   [fuente] -> iterar posición a posición:
#     saltar espacios/comentarios -> clasificar carácter:
#       letra/_ -> identificador  |  dígito -> número
#       '"' -> cadena             |  otro -> operador/símbolo
#     agregar token o error a la lista correspondiente
#   agregar token FIN al final -> devolver (tokens, errores)
# ---------------------------------------------------------------------
def analizar_lexico(fuente):
    tokens = []                                                                # lista de tokens de salida
    errores = []                                                               # lista de errores de salida
    posicion = 0                                                               # posición inicial
    linea = 1                                                                  # línea inicial
    columna = 1                                                                # columna inicial
    while posicion < len(fuente):                                              # mientras haya texto
        posicion, linea, columna = saltar_espacios_y_comentarios(fuente, posicion, linea, columna)  # saltar blancos
        if posicion >= len(fuente):                                            # llegamos al final
            break                                                              # salir del bucle
        caracter = fuente[posicion]                                            # carácter actual
        if caracter.isalpha() or caracter == '_':                             # inicio de identificador
            token, posicion, columna, error = analizar_identificador(fuente, posicion, linea, columna)  # analizar
        elif caracter.isdigit():                                               # inicio de número
            token, posicion, columna, error = analizar_numero(fuente, posicion, linea, columna)  # analizar
        elif caracter == '"':                                                  # inicio de cadena
            token, posicion, columna, error = analizar_cadena(fuente, posicion, linea, columna)  # analizar
        else:                                                                  # operador o símbolo
            token, posicion, columna, error = analizar_operador(fuente, posicion, linea, columna)  # analizar
        if error is not None:                                                  # si hubo error
            errores.append(error)                                              # guardar error
        else:                                                                  # si fue correcto
            tokens.append(token)                                               # guardar token
    tokens.append([TIPO_FIN, "", linea, columna, None])                        # token de fin de archivo
    return tokens, errores                                                     # devolver resultados

# ------------------ Bloque de comprobación manual ---------------------
if __name__ == "__main__":
    codigo_demostracion = 'var edad : entero = 2 + 3 * 4;\nmostrar edad;'      # código de ejemplo
    lista_tokens, lista_errores = analizar_lexico(codigo_demostracion)         # ejecutar lexer
    print("TOKENS:")                                                           # encabezado
    for token_actual in lista_tokens:                                          # recorrer tokens
        print("  ", token_actual)                                              # imprimir cada uno
    print("ERRORES:")                                                          # encabezado
    for error_actual in lista_errores:                                         # recorrer errores
        print("  ", error_actual)                                              # imprimir cada uno