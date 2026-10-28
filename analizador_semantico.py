# analizador_semantico.py
# =====================================================================
# Analizador semántico del lenguaje educativo.
# Recorre el AST, construye la tabla de símbolos y detecta errores
# semánticos: variables no declaradas, redeclaraciones y tipos
# incompatibles en declaraciones, asignaciones y expresiones.
#
# ---------------------------------------------------------------------
# EJEMPLO TRAZADO
# ---------------------------------------------------------------------
# Entrada (AST generado por analizador_sintactico.py):
#   var x : entero = 2 + 3 * 4; mostrar x;
#
# AST recibido:
#   ["programa", [
#     ["declaracion", "x", "entero",
#       ["binaria", "+",
#         ["entero", 2, 1, 18],
#         ["binaria", "*",
#           ["entero", 3, 1, 22],
#           ["entero", 4, 1, 26],
#           1, 24],
#         1, 20],
#       1, 5],
#     ["mostrar", ["identificador", "x", 1, 37], 1, 29]
#   ]]
#
# Salida:
#   tabla_simbolos     = [["x", "entero", 1, 5]]
#   errores_semanticos = []
#
# Con error: var y : entero = "hola";
#   errores_semanticos = [["SEMANTICO",
#     "Tipo incompatible en declaracion: se esperaba entero pero la expresion es cadena",
#     1, 5]]
# ---------------------------------------------------------------------

# Estado global del análisis semántico.
tabla_simbolos = []          # cada entrada es [nombre, tipo, linea, columna]
errores_semanticos = []      # cada entrada es [tipo_error, mensaje, linea, columna]

# ------------------ Diagrama: analizar_semantico ---------------------
#   [arbol] -> limpiar estado -> recorrer instrucciones una por una
#           -> devolver (tabla_simbolos, errores_semanticos)
# ---------------------------------------------------------------------
def analizar_semantico(arbol):
    global tabla_simbolos, errores_semanticos       # modificamos el estado global
    tabla_simbolos = []                             # tabla vacía al comenzar
    errores_semanticos = []                         # errores vacíos al comenzar
    lista_instrucciones = arbol[1]                  # posición 1 del programa = lista
    for instruccion in lista_instrucciones:         # recorrer cada instrucción
        procesar_instruccion(instruccion)           # procesarla (modifica el estado global)
    return tabla_simbolos, errores_semanticos       # devolver resultados finales

# ------------------ Diagrama: procesar_instruccion -------------------
#   [categoría] -> ¿declaracion? -> procesar_declaracion
#               -> ¿asignacion?  -> procesar_asignacion
#               -> ¿mostrar?     -> procesar_mostrar
# ---------------------------------------------------------------------
def procesar_instruccion(instruccion):
    categoria = instruccion[0]                      # categoría del nodo
    if categoria == "declaracion":                  # declaración de variable
        procesar_declaracion(instruccion)           # delegar
    elif categoria == "asignacion":                 # asignación a variable existente
        procesar_asignacion(instruccion)            # delegar
    elif categoria == "mostrar":                    # instrucción mostrar
        procesar_mostrar(instruccion)               # delegar

# ------------------ Diagrama: procesar_declaracion -------------------
#   [nodo] -> ¿ya existe? --sí--> error, return
#                        --no--> inferir tipo -> comparar con declarado
#                              -> agregar a tabla (con o sin error)
# ---------------------------------------------------------------------
def procesar_declaracion(nodo):
    nombre = nodo[1]                                # nombre de la variable
    tipo_declarado = nodo[2]                        # tipo declarado explícitamente
    linea = nodo[4]                                 # línea del nombre
    columna = nodo[5]                               # columna del nombre
    if variable_ya_declarada(nombre):               # ¿redeclaración?
        reportar_error_semantico("Variable ya declarada: " + nombre, linea, columna)  # error
        return                                      # no agregar de nuevo
    tipo_expresion = inferir_tipo_expresion(nodo[3])  # tipo inferido del lado derecho
    if tipo_expresion not in ["error", tipo_declarado]:  # ¿tipo incompatible?
        reportar_error_semantico(                   # construir mensaje detallado
            "Tipo incompatible en declaracion: se esperaba " + tipo_declarado +
            " pero la expresion es " + tipo_expresion, linea, columna)
    tabla_simbolos.append([nombre, tipo_declarado, linea, columna])  # agregar a la tabla

# ------------------ Diagrama: procesar_asignacion --------------------
#   [nodo] -> ¿existe la variable? --no--> error, return
#                                 --sí--> inferir tipo -> comparar con el de la variable
# ---------------------------------------------------------------------
def procesar_asignacion(nodo):
    nombre = nodo[1]                                # nombre destino
    linea = nodo[3]                                 # línea del nombre
    columna = nodo[4]                               # columna del nombre
    tipo_variable = buscar_tipo_variable(nombre)    # tipo de la variable destino
    if tipo_variable is None:                       # variable no existe
        reportar_error_semantico("Asignacion a variable no declarada: " + nombre, linea, columna)
        return                                      # no continuar
    tipo_expresion = inferir_tipo_expresion(nodo[2])  # tipo del lado derecho
    if tipo_expresion not in ["error", tipo_variable]:  # ¿tipos incompatibles?
        reportar_error_semantico(                   # reportar detalle
            "Tipo incompatible en asignacion: se esperaba " + tipo_variable +
            " pero la expresion es " + tipo_expresion, linea, columna)

# ------------------ Diagrama: procesar_mostrar -----------------------
#   [nodo] -> inferir tipo de la expresión (para detectar errores internos)
# ---------------------------------------------------------------------
def procesar_mostrar(nodo):
    inferir_tipo_expresion(nodo[1])                 # solo queremos detectar errores

# ------------------ Diagrama: inferir_tipo_expresion -----------------
#   [nodo] -> según categoría: literal | identificador | binaria | unaria
#   devuelve: "entero" | "decimal" | "cadena" | "booleano" | "error"
# ---------------------------------------------------------------------
def inferir_tipo_expresion(nodo):
    categoria = nodo[0]                             # categoría del nodo
    if categoria in ["entero", "decimal", "cadena", "booleano"]:  # literales
        return categoria                            # el tipo es la categoría misma
    if categoria == "identificador":                # uso de variable
        return inferir_tipo_identificador(nodo)     # delegar
    if categoria == "binaria":                      # operación binaria
        return inferir_tipo_binaria(nodo)           # delegar
    if categoria == "unaria":                       # operación unaria
        return inferir_tipo_unaria(nodo)            # delegar
    return "error"                                  # caso no contemplado

# ------------------ Diagrama: inferir_tipo_identificador -------------
#   [nodo] -> buscar_tipo_variable -> ¿existe? --sí--> tipo
#                                            --no--> error + reporte
# ---------------------------------------------------------------------
def inferir_tipo_identificador(nodo):
    nombre = nodo[1]                                # nombre de la variable
    tipo = buscar_tipo_variable(nombre)             # buscar en la tabla
    if tipo is None:                                # no fue declarada antes
        reportar_error_semantico("Variable no declarada: " + nombre, nodo[2], nodo[3])
        return "error"                              # propagar error
    return tipo                                     # devolver su tipo

# ------------------ Diagrama: inferir_tipo_binaria -------------------
#   [nodo] -> inferir tipo_izq y tipo_der -> si alguno es error, error
#          -> según operador: aritmetico | relacional | logico
# ---------------------------------------------------------------------
def inferir_tipo_binaria(nodo):
    operador = nodo[1]                              # operador del nodo
    tipo_izq = inferir_tipo_expresion(nodo[2])      # tipo del lado izquierdo
    tipo_der = inferir_tipo_expresion(nodo[3])      # tipo del lado derecho
    if tipo_izq == "error" or tipo_der == "error":  # si algún lado falló
        return "error"                              # propagar error
    if operador in ["+", "-", "*", "/"]:            # operadores aritméticos
        return tipo_aritmetico(operador, tipo_izq, tipo_der, nodo[4], nodo[5])
    if operador in ["==", "!=", "<", ">", "<=", ">="]:  # operadores relacionales
        return tipo_relacional(operador, tipo_izq, tipo_der, nodo[4], nodo[5])
    if operador in ["y", "o"]:                      # operadores lógicos
        return tipo_logico(operador, tipo_izq, tipo_der, nodo[4], nodo[5])
    reportar_error_semantico("Operador binario desconocido: " + operador, nodo[4], nodo[5])
    return "error"                                  # operador no contemplado

# ------------------ Diagrama: tipo_aritmetico ------------------------
#   [op, izq, der] -> ¿entero/entero? -> entero (o decimal si '/')
#                  -> ¿decimal/decimal? -> decimal
#                  -> ¿cadena/cadena con '+'? -> cadena
#                  -> resto -> error
# ---------------------------------------------------------------------
def tipo_aritmetico(operador, tipo_izq, tipo_der, linea, columna):
    if tipo_izq == "entero" and tipo_der == "entero":  # ambos enteros
        if operador == "/":                         # la división produce decimal
            return "decimal"                        # resultado decimal
        return "entero"                             # resto: entero
    if tipo_izq == "decimal" and tipo_der == "decimal":  # ambos decimales
        return "decimal"                            # resultado decimal
    if tipo_izq == "cadena" and tipo_der == "cadena" and operador == "+":  # concatenación
        return "cadena"                             # resultado cadena
    reportar_error_semantico(                       # combinación inválida
        "Operador '" + operador + "' no aplica entre " + tipo_izq + " y " + tipo_der,
        linea, columna)
    return "error"                                  # propagar error

# ------------------ Diagrama: tipo_relacional ------------------------
#   [op, izq, der] -> ¿mismo tipo? --no--> error
#                  --sí--> ¿operadores < > <= >= con numero? --no--> error
#                        --sí--> booleano
# ---------------------------------------------------------------------
def tipo_relacional(operador, tipo_izq, tipo_der, linea, columna):
    if tipo_izq != tipo_der:                        # los relacionales exigen mismo tipo
        reportar_error_semantico(
            "Operador '" + operador + "' requiere operandos del mismo tipo", linea, columna)
        return "error"                              # propagar error
    if operador in ["<", ">", "<=", ">="]:          # estos solo aplican a números
        if tipo_izq not in ["entero", "decimal"]:   # si no es número
            reportar_error_semantico(
                "Operador '" + operador + "' solo aplica a numeros", linea, columna)
            return "error"                          # propagar error
    return "booleano"                               # resultado del relacional

# ------------------ Diagrama: tipo_logico ----------------------------
#   [op, izq, der] -> ¿ambos booleanos? --sí--> booleano
#                                     --no--> error
# ---------------------------------------------------------------------
def tipo_logico(operador, tipo_izq, tipo_der, linea, columna):
    if tipo_izq != "booleano" or tipo_der != "booleano":  # exige booleanos
        reportar_error_semantico(
            "Operador '" + operador + "' requiere operandos booleanos", linea, columna)
        return "error"                              # propagar error
    return "booleano"                               # resultado del lógico

# ------------------ Diagrama: inferir_tipo_unaria --------------------
#   [nodo] -> inferir operando -> según operador:
#             '-' exige numérico, 'no' exige booleano
# ---------------------------------------------------------------------
def inferir_tipo_unaria(nodo):
    operador = nodo[1]                              # operador del nodo
    tipo_operando = inferir_tipo_expresion(nodo[2]) # tipo del operando interno
    if tipo_operando == "error":                    # si el operando falló
        return "error"                              # propagar error
    if operador == "-":                             # menos unario
        if tipo_operando not in ["entero", "decimal"]:  # solo aplica a números
            reportar_error_semantico("Menos unario requiere numero", nodo[3], nodo[4])
            return "error"                          # propagar error
        return tipo_operando                        # mismo tipo que el operando
    if operador == "no":                            # negación lógica
        if tipo_operando != "booleano":             # solo aplica a booleanos
            reportar_error_semantico("'no' requiere booleano", nodo[3], nodo[4])
            return "error"                          # propagar error
        return "booleano"                           # resultado booleano
    reportar_error_semantico("Operador unario desconocido: " + operador, nodo[3], nodo[4])
    return "error"                                  # caso no contemplado

# ------------------ Diagrama: buscar_tipo_variable -------------------
#   [nombre] -> recorrer tabla_simbolos buscando coincidencia
#           -> devolver el tipo o None
# ---------------------------------------------------------------------
def buscar_tipo_variable(nombre):
    for entrada in tabla_simbolos:                  # recorrer cada fila de la tabla
        if entrada[0] == nombre:                    # comparar el nombre
            return entrada[1]                       # devolver su tipo
    return None                                     # no encontrada

# ------------------ Diagrama: variable_ya_declarada ------------------
#   [nombre] -> ¿buscar_tipo_variable devuelve algo? -> True / False
# ---------------------------------------------------------------------
def variable_ya_declarada(nombre):
    return buscar_tipo_variable(nombre) is not None  # existe si el tipo no es None

# ------------------ Diagrama: reportar_error_semantico ---------------
#   [mensaje, línea, col] -> agregar a errores_semanticos
# ---------------------------------------------------------------------
def reportar_error_semantico(mensaje, linea, columna):
    errores_semanticos.append(["SEMANTICO", mensaje, linea, columna])  # acumular error

# ------------------ Diagrama: formatear_tabla_simbolos_a_texto -------
#   [tabla] -> ¿vacía? -> texto "vacía"
#          -> construir encabezado + filas alineadas
# ---------------------------------------------------------------------
def formatear_tabla_simbolos_a_texto(tabla):
    if len(tabla) == 0:                             # tabla sin entradas
        return "  (tabla de simbolos vacia)\n"      # mensaje especial
    resultado = "  Nombre         Tipo       Linea  Columna\n"  # encabezado
    for entrada in tabla:                           # recorrer cada variable
        nombre = str(entrada[0])                    # convertir a texto
        tipo = str(entrada[1])                      # convertir a texto
        linea = str(entrada[2])                     # convertir a texto
        columna = str(entrada[3])                   # convertir a texto
        resultado += "  " + nombre.ljust(15) + tipo.ljust(11) + linea.ljust(7) + columna + "\n"
    return resultado                                # texto completo de la tabla

# ------------------ Bloque de comprobación manual ---------------------
if __name__ == "__main__":
    from analizador_lexico import analizar_lexico   # importar el lexer
    from analizador_sintactico import analizar_sintactico  # importar el parser

    def demostrar(codigo):
        tokens, errores_lexicos = analizar_lexico(codigo)          # fase 1
        arbol, errores_sintacticos = analizar_sintactico(tokens)   # fase 2
        tabla, errores = analizar_semantico(arbol)                 # fase 3
        print("Codigo:", codigo)                                   # qué se analizó
        print(formatear_tabla_simbolos_a_texto(tabla))             # tabla de símbolos
        print("Errores:", errores)                                 # errores semánticos
        print("---")                                               # separador

    demostrar('var x : entero = 2 + 3 * 4; mostrar x;')            # caso válido
    demostrar('var y : entero = "hola";')                          # error de tipo
    demostrar('z = 5;')                                            # variable no declarada