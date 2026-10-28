# lenguaje.py
# =====================================================================
# Definiciones centrales del lenguaje educativo.
# Este archivo NO procesa código: solo declara constantes y dos
# funciones auxiliares que consultan esas constantes.

# Explicación breve: este archivo es el "diccionario del lenguaje". 
#Si mañana el profesor pide añadir un tipo de dato nuevo (por ejemplo longitud), 
#se agrega a TIPOS_DATOS y al analizador semántico; el analizador léxico y sintáctico
#lo reconocerán automáticamente como TIPO_TIPO_DATO.

# ---------------------------------------------------------------------
# EJEMPLO TRAZADO
# ---------------------------------------------------------------------
# Entrada (en Python interactivo):
#     >>> from lenguaje import es_tipo_dato, es_palabra_reservada
#     >>> es_tipo_dato("entero")
#     >>> es_tipo_dato("perro")
#     >>> es_palabra_reservada("var")
#     >>> es_palabra_reservada("miVariable")
#
# Salida esperada:
#     True
#     False
#     True
#     False
# ---------------------------------------------------------------------

# ------------------ Constantes de tipo de token ----------------------
TIPO_PALABRA_RESERVADA = "PALABRA_RESERVADA"      # para 'var' y 'mostrar'
TIPO_TIPO_DATO = "TIPO_DATO"                        # para 'entero','decimal','cadena','booleano'
TIPO_BOOLEANO_LITERAL = "BOOLEANO_LITERAL"          # para 'verdadero' y 'falso'
TIPO_OPERADOR_Y = "OPERADOR_Y"                      # palabra 'y' (AND lógico)
TIPO_OPERADOR_O = "OPERADOR_O"                      # palabra 'o' (OR lógico)
TIPO_OPERADOR_NO = "OPERADOR_NO"                    # palabra 'no' (NOT lógico)
TIPO_IDENTIFICADOR = "IDENTIFICADOR"                # nombres de variables
TIPO_ENTERO = "ENTERO"                              # números sin punto: 42
TIPO_DECIMAL = "DECIMAL"                            # números con punto: 3.14
TIPO_CADENA = "CADENA"                              # texto entre comillas dobles
TIPO_ASIGNACION = "ASIGNACION"                      # símbolo '='
TIPO_SUMA = "SUMA"                                  # símbolo '+'
TIPO_RESTA = "RESTA"                                # símbolo '-'
TIPO_MULTIPLICACION = "MULTIPLICACION"              # símbolo '*'
TIPO_DIVISION = "DIVISION"                          # símbolo '/'
TIPO_IGUAL_IGUAL = "IGUAL_IGUAL"                    # símbolo '=='
TIPO_DIFERENTE = "DIFERENTE"                        # símbolo '!='
TIPO_MENOR = "MENOR"                                # símbolo '<'
TIPO_MAYOR = "MAYOR"                                # símbolo '>'
TIPO_MENOR_IGUAL = "MENOR_IGUAL"                    # símbolo '<='
TIPO_MAYOR_IGUAL = "MAYOR_IGUAL"                    # símbolo '>='
TIPO_PARENTESIS_IZQUIERDO = "PARENTESIS_IZQUIERDO"  # símbolo '('
TIPO_PARENTESIS_DERECHO = "PARENTESIS_DERECHO"      # símbolo ')'
TIPO_DOS_PUNTOS = "DOS_PUNTOS"                      # símbolo ':'
TIPO_PUNTO_COMA = "PUNTO_COMA"                      # símbolo ';'
TIPO_FIN = "FIN"                                    # marca de fin de archivo

# ------------------ Listas de palabras del lenguaje ------------------
PALABRAS_RESERVADAS_SIMPLES = ["var", "mostrar"]                        # palabras clave sin categoría especial
TIPOS_DATOS = ["entero", "decimal", "cadena", "booleano"]               # tipos de dato válidos
LITERALES_BOOLEANOS = ["verdadero", "falso"]                            # valores booleanos escritos
OPERADORES_DE_PALABRA = ["y", "o", "no"]                                # operadores lógicos escritos como palabra
TODAS_LAS_PALABRAS_RESERVADAS = PALABRAS_RESERVADAS_SIMPLES + TIPOS_DATOS + LITERALES_BOOLEANOS + OPERADORES_DE_PALABRA  # lista combinada precalculada

# ------------------ Diagrama de flujo: es_palabra_reservada ----------
#   [texto] -> ¿está en TODAS_LAS_PALABRAS_RESERVADAS? -> True / False
# ---------------------------------------------------------------------
def es_palabra_reservada(texto):
    return texto in TODAS_LAS_PALABRAS_RESERVADAS  # consulta directa a la lista combinada

# ------------------ Diagrama de flujo: es_tipo_dato ------------------
#   [texto] -> ¿está en TIPOS_DATOS? -> True / False
# ---------------------------------------------------------------------
def es_tipo_dato(texto):
    return texto in TIPOS_DATOS  # consulta directa a la lista de tipos

# ------------------ Bloque de comprobación manual ---------------------
if __name__ == "__main__":
    print("es_tipo_dato('entero') =", es_tipo_dato("entero"))            # debe imprimir True
    print("es_tipo_dato('perro') =", es_tipo_dato("perro"))              # debe imprimir False
    print("es_palabra_reservada('var') =", es_palabra_reservada("var"))  # debe imprimir True
    print("es_palabra_reservada('x') =", es_palabra_reservada("x"))      # debe imprimir False