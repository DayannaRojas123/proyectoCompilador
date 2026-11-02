# formato.py
# =====================================================================
# Funciones puras que convierten resultados del compilador en texto
# para los paneles. No tocan ningún widget, por eso se pueden probar solas.
# (El árbol y la tabla de símbolos se formatean en el paquete compilador.)
# =====================================================================


# ------------------ Diagrama: formatear_tokens_a_texto ---------------
#   [tokens] -> texto tabular con encabezado y una fila por token
# ---------------------------------------------------------------------
def formatear_tokens_a_texto(tokens):
    resultado = "  Linea  Columna  Tipo                    Lexema                Valor\n"  # encabezado
    resultado += "  " + "-" * 78 + "\n"                                                    # línea separadora
    for token in tokens:                                                                    # recorrer tokens
        tipo = token[0]                                                                     # categoría
        lexema = token[1]                                                                   # texto original
        linea = str(token[2])                                                               # línea
        columna = str(token[3])                                                             # columna
        valor = "" if token[4] is None else str(token[4])                                   # valor o vacío
        resultado += "  " + linea.ljust(7) + columna.ljust(9) + tipo.ljust(24) + lexema.ljust(22) + valor + "\n"
    return resultado                                                                        # texto listo


# ------------------ Diagrama: formatear_error ------------------------
#   [error] -> "[TIPO] mensaje (linea N, columna M)"
# ---------------------------------------------------------------------
def formatear_error(error):
    texto = "[" + error[0] + "] " + error[1]                                                # prefijo con tipo
    texto += " (linea " + str(error[2]) + ", columna " + str(error[3]) + ")\n"              # agregar posición
    return texto
