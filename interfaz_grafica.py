# interfaz_grafica.py
# =====================================================================
# Interfaz gráfica Tkinter del compilador educativo.
# Todo procedural: no usamos clases, todo el estado va en variables
# globales del módulo, y cada botón ejecuta una función de nivel
# superior. Las tres fases del compilador se invocan realmente al
# pulsar "Analizar".
#
# ---------------------------------------------------------------------
# EJEMPLO TRAZADO
# ---------------------------------------------------------------------
# Entrada: 'var edad : entero = 2 + 3 * 4;' + 'mostrar edad;' + [Analizar]
# Salida:
#   - Pestaña Tokens: 15 filas (una por token)
#   - Pestaña Arbol: jerarquía con 'Binaria: *' colgando de 'Binaria: +'
#   - Pestaña Tabla simbolos: 1 fila con 'edad entero 1 5'
#   - Pestaña Errores: vacía
#   - Pestaña Informe: 'Estado: ANALISIS COMPLETO'
#   - Etiquetas de fase: las tres en verde 'correcta'
# ---------------------------------------------------------------------

# Importamos tkinter (ventana) y su submódulo ttk (widgets con estilo).
import tkinter as tk                          # widget base: Text, Label
from tkinter import ttk                       # widgets con estilo moderno

# Importamos las tres fases del compilador.
from analizador_lexico import analizar_lexico                                     # fase léxica
from analizador_sintactico import analizar_sintactico, formatear_arbol_a_texto    # fase sintáctica + formateo
from analizador_semantico import analizar_semantico, formatear_tabla_simbolos_a_texto  # fase semántica

# Colores para los estados de las fases.
COLOR_VERDE = "#1a7f37"                       # análisis correcto
COLOR_ROJO = "#cf222e"                        # errores encontrados
COLOR_GRIS = "#57606a"                        # no ejecutada o pendiente

# Variables globales del módulo (el "estado" de la ventana).
ventana_principal = None                      # raíz Tk()
editor_codigo = None                          # widget Text del editor
etiqueta_estado_lexico = None                 # Label del estado léxico
etiqueta_estado_sintactico = None             # Label del estado sintáctico
etiqueta_estado_semantico = None              # Label del estado semántico
area_tokens = None                            # Text para tokens
area_ast = None                               # Text para el árbol
area_tabla_simbolos = None                    # Text para tabla de símbolos
area_errores = None                           # Text para errores
area_informe_final = None                     # Text para el informe

# ------------------ Diagrama: crear_area_de_texto --------------------
#   [padre] -> crear Frame con scroll V y H -> devolver el Text interior
# ---------------------------------------------------------------------
def crear_area_de_texto(padre):
    marco = ttk.Frame(padre)                                                          # marco contenedor
    marco.pack(fill="both", expand=True)                                              # ocupa todo el espacio
    barra_vertical = ttk.Scrollbar(marco, orient="vertical")                          # scroll vertical
    barra_vertical.pack(side="right", fill="y")                                       # a la derecha
    barra_horizontal = ttk.Scrollbar(marco, orient="horizontal")                      # scroll horizontal
    barra_horizontal.pack(side="bottom", fill="x")                                    # abajo
    area = tk.Text(marco, wrap="none", font=("Consolas", 10),                          # Text monoespaciado
                   yscrollcommand=barra_vertical.set,                                  # conectado al scroll V
                   xscrollcommand=barra_horizontal.set)                                # conectado al scroll H
    area.pack(side="left", fill="both", expand=True)                                  # ocupa el resto
    barra_vertical.config(command=area.yview)                                         # scroll controla al Text
    barra_horizontal.config(command=area.xview)                                       # scroll controla al Text
    return area                                                                       # devolvemos el Text

# ------------------ Diagrama: crear_seccion_editor -------------------
#   [raiz] -> LabelFrame con Text y botones (Analizar, Limpiar, 5 ejemplos)
# ---------------------------------------------------------------------
def crear_seccion_editor(raiz):
    global editor_codigo                                                              # modificamos la global
    marco_editor = ttk.LabelFrame(raiz, text="Codigo fuente")                         # sección con título
    marco_editor.pack(fill="both", expand=False, padx=10, pady=5)                     # ubicación
    editor_codigo = tk.Text(marco_editor, height=10, font=("Consolas", 11), undo=True)  # editor real
    editor_codigo.pack(fill="both", expand=True, padx=5, pady=5)                      # ubicación interna
    marco_botones = ttk.Frame(marco_editor)                                           # fila de botones
    marco_botones.pack(fill="x", padx=5, pady=(0, 5))                                 # ubicación interna
    ttk.Button(marco_botones, text="Analizar", command=analizar_codigo).pack(side="left", padx=2)                  # dispara el compilador
    ttk.Button(marco_botones, text="Limpiar", command=limpiar_editor).pack(side="left", padx=2)                    # vacía editor
    ttk.Button(marco_botones, text="Ejemplo valido", command=cargar_ejemplo_valido).pack(side="left", padx=2)      # ejemplo OK
    ttk.Button(marco_botones, text="Error lexico", command=cargar_ejemplo_error_lexico).pack(side="left", padx=2)  # ejemplo error léxico
    ttk.Button(marco_botones, text="Error sintactico", command=cargar_ejemplo_error_sintactico).pack(side="left", padx=2)  # ejemplo sintáctico
    ttk.Button(marco_botones, text="Error semantico", command=cargar_ejemplo_error_semantico).pack(side="left", padx=2)    # ejemplo semántico
    ttk.Button(marco_botones, text="Precedencia", command=cargar_ejemplo_precedencia).pack(side="left", padx=2)            # ejemplo paréntesis

# ------------------ Diagrama: crear_seccion_estado_fases -------------
#   [raiz] -> LabelFrame con tres etiquetas (léxica, sintáctica, semántica)
# ---------------------------------------------------------------------
def crear_seccion_estado_fases(raiz):
    global etiqueta_estado_lexico, etiqueta_estado_sintactico, etiqueta_estado_semantico  # modificamos globales
    marco_fases = ttk.LabelFrame(raiz, text="Estado de las fases")                    # sección con título
    marco_fases.pack(fill="x", padx=10, pady=5)                                        # ubicación
    etiqueta_estado_lexico = tk.Label(marco_fases, text="Lexica: pendiente", fg=COLOR_GRIS, font=("Segoe UI", 11, "bold"))
    etiqueta_estado_lexico.pack(side="left", padx=15, pady=5)                          # a la izquierda
    etiqueta_estado_sintactico = tk.Label(marco_fases, text="Sintactica: pendiente", fg=COLOR_GRIS, font=("Segoe UI", 11, "bold"))
    etiqueta_estado_sintactico.pack(side="left", padx=15, pady=5)                      # en el medio
    etiqueta_estado_semantico = tk.Label(marco_fases, text="Semantica: pendiente", fg=COLOR_GRIS, font=("Segoe UI", 11, "bold"))
    etiqueta_estado_semantico.pack(side="left", padx=15, pady=5)                       # a la derecha

# ------------------ Diagrama: crear_seccion_pestanas -----------------
#   [raiz] -> Notebook con 5 pestañas, cada una con su Text
# ---------------------------------------------------------------------
def crear_seccion_pestanas(raiz):
    global area_tokens, area_ast, area_tabla_simbolos, area_errores, area_informe_final  # globales
    cuaderno = ttk.Notebook(raiz)                                                      # contenedor de pestañas
    cuaderno.pack(fill="both", expand=True, padx=10, pady=5)                           # ubicación
    pestana_tokens = ttk.Frame(cuaderno); cuaderno.add(pestana_tokens, text="Tokens")  # pestaña tokens
    area_tokens = crear_area_de_texto(pestana_tokens)                                  # Text de tokens
    pestana_ast = ttk.Frame(cuaderno); cuaderno.add(pestana_ast, text="Arbol sintactico")  # pestaña AST
    area_ast = crear_area_de_texto(pestana_ast)                                        # Text del AST
    pestana_simbolos = ttk.Frame(cuaderno); cuaderno.add(pestana_simbolos, text="Tabla de simbolos")  # pestaña símbolos
    area_tabla_simbolos = crear_area_de_texto(pestana_simbolos)                        # Text de la tabla
    pestana_errores = ttk.Frame(cuaderno); cuaderno.add(pestana_errores, text="Errores")  # pestaña errores
    area_errores = crear_area_de_texto(pestana_errores)                                # Text de errores
    pestana_informe = ttk.Frame(cuaderno); cuaderno.add(pestana_informe, text="Informe final")  # pestaña informe
    area_informe_final = crear_area_de_texto(pestana_informe)                          # Text del informe

# ------------------ Diagrama: limpiar_editor -------------------------
#   [] -> vaciar el editor y reiniciar los paneles y estados
# ---------------------------------------------------------------------
def limpiar_editor():
    editor_codigo.delete("1.0", "end")                     # borrar todo el texto del editor
    limpiar_todos_los_paneles()                            # vaciar todas las pestañas
    marcar_las_tres_fases_pendientes()                     # volver a "pendiente"

# ------------------ Diagrama: colocar_codigo_en_editor ---------------
#   [texto] -> reemplazar contenido y limpiar paneles/estados
# ---------------------------------------------------------------------
def colocar_codigo_en_editor(texto_del_ejemplo):
    editor_codigo.delete("1.0", "end")                     # vaciar el editor primero
    editor_codigo.insert("1.0", texto_del_ejemplo)         # pegar el ejemplo
    limpiar_todos_los_paneles()                            # paneles a cero
    marcar_las_tres_fases_pendientes()                     # fases a "pendiente"

# ------------------ Diagrama: cargar_ejemplo_valido ------------------
#   [] -> colocar un programa sin errores
# ---------------------------------------------------------------------
def cargar_ejemplo_valido():
    colocar_codigo_en_editor('var edad : entero = 2 + 3 * 4;\nmostrar edad;\n')

# ------------------ Diagrama: cargar_ejemplo_error_lexico ------------
#   [] -> colocar programa con '@' (carácter no permitido)
# ---------------------------------------------------------------------
def cargar_ejemplo_error_lexico():
    colocar_codigo_en_editor('var x : entero = 5 @ 3;\n')

# ------------------ Diagrama: cargar_ejemplo_error_sintactico --------
#   [] -> colocar programa con expresión incompleta
# ---------------------------------------------------------------------
def cargar_ejemplo_error_sintactico():
    colocar_codigo_en_editor('var x : entero = 2 + ;\n')

# ------------------ Diagrama: cargar_ejemplo_error_semantico ---------
#   [] -> colocar programa con tipos incompatibles
# ---------------------------------------------------------------------
def cargar_ejemplo_error_semantico():
    colocar_codigo_en_editor('var y : entero = "hola";\n')

# ------------------ Diagrama: cargar_ejemplo_precedencia -------------
#   [] -> colocar programa con paréntesis para demostrar precedencia
# ---------------------------------------------------------------------
def cargar_ejemplo_precedencia():
    colocar_codigo_en_editor('var resultado : entero = (2 + 3) * 4;\nmostrar resultado;\n')

# ------------------ Diagrama: marcar_fase ----------------------------
#   [etiqueta, texto, color] -> actualizar texto y color de una fase
# ---------------------------------------------------------------------
def marcar_fase(etiqueta, texto, color):
    etiqueta.config(text=texto, fg=color)                  # cambio de texto y color

# ------------------ Diagrama: marcar_las_tres_fases_pendientes -------
#   [] -> poner las tres etiquetas en "pendiente" y color gris
# ---------------------------------------------------------------------
def marcar_las_tres_fases_pendientes():
    marcar_fase(etiqueta_estado_lexico, "Lexica: pendiente", COLOR_GRIS)         # léxica
    marcar_fase(etiqueta_estado_sintactico, "Sintactica: pendiente", COLOR_GRIS) # sintáctica
    marcar_fase(etiqueta_estado_semantico, "Semantica: pendiente", COLOR_GRIS)   # semántica

# ------------------ Diagrama: limpiar_todos_los_paneles --------------
#   [] -> borrar el contenido de cada pestaña de texto
# ---------------------------------------------------------------------
def limpiar_todos_los_paneles():
    area_tokens.delete("1.0", "end")                       # tokens
    area_ast.delete("1.0", "end")                          # árbol
    area_tabla_simbolos.delete("1.0", "end")               # tabla de símbolos
    area_errores.delete("1.0", "end")                      # errores
    area_informe_final.delete("1.0", "end")                # informe

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

# ------------------ Diagrama: mostrar_tokens_en_panel ----------------
#   [tokens] -> escribir el texto tabular en area_tokens
# ---------------------------------------------------------------------
def mostrar_tokens_en_panel(tokens):
    area_tokens.insert("end", formatear_tokens_a_texto(tokens))                          # delegar formateo

# ------------------ Diagrama: mostrar_ast_en_panel -------------------
#   [arbol] -> escribir el árbol indentado en area_ast
# ---------------------------------------------------------------------
def mostrar_ast_en_panel(arbol):
    area_ast.insert("end", formatear_arbol_a_texto(arbol, 0))                            # delegar formateo

# ------------------ Diagrama: mostrar_tabla_en_panel -----------------
#   [tabla] -> escribir la tabla de símbolos formateada en area_tabla_simbolos
# ---------------------------------------------------------------------
def mostrar_tabla_en_panel(tabla):
    area_tabla_simbolos.insert("end", formatear_tabla_simbolos_a_texto(tabla))           # delegar formateo

# ------------------ Diagrama: mostrar_errores_en_panel ---------------
#   [errores] -> escribir una línea por error; no borrar los ya mostrados
# ---------------------------------------------------------------------
def mostrar_errores_en_panel(errores):
    for error in errores:                                                                # recorrer errores
        texto = "[" + error[0] + "] " + error[1]                                         # prefijo con tipo
        texto += " (linea " + str(error[2]) + ", columna " + str(error[3]) + ")\n"       # agregar posición
        area_errores.insert("end", texto)                                                # insertar al final

# ------------------ Diagrama: ejecutar_fase_lexica -------------------
#   [codigo] -> analizar_lexico -> mostrar tokens -> marcar estado
#   devuelve (tokens, errores_lexicos)
# ---------------------------------------------------------------------
def ejecutar_fase_lexica(codigo):
    tokens, errores = analizar_lexico(codigo)                                            # llamar al lexer
    mostrar_tokens_en_panel(tokens)                                                      # pestaña Tokens
    mostrar_errores_en_panel(errores)                                                    # pestaña Errores
    if len(errores) > 0:                                                                 # ¿hubo error léxico?
        marcar_fase(etiqueta_estado_lexico, "Lexica: con errores", COLOR_ROJO)           # rojo en léxica
        marcar_fase(etiqueta_estado_sintactico, "Sintactica: no ejecutada", COLOR_GRIS)  # sintáctica gris
        marcar_fase(etiqueta_estado_semantico, "Semantica: no ejecutada", COLOR_GRIS)    # semántica gris
    else:                                                                                # sin errores
        marcar_fase(etiqueta_estado_lexico, "Lexica: correcta", COLOR_VERDE)             # verde en léxica
    return tokens, errores                                                               # devolver al orquestador

# ------------------ Diagrama: ejecutar_fase_sintactica ---------------
#   [tokens] -> analizar_sintactico -> mostrar AST -> marcar estado
#   devuelve (arbol, errores_sintacticos)
# ---------------------------------------------------------------------
def ejecutar_fase_sintactica(tokens):
    arbol, errores = analizar_sintactico(tokens)                                         # llamar al parser
    mostrar_ast_en_panel(arbol)                                                          # pestaña Árbol
    mostrar_errores_en_panel(errores)                                                    # pestaña Errores
    if len(errores) > 0:                                                                 # ¿hubo error?
        marcar_fase(etiqueta_estado_sintactico, "Sintactica: con errores", COLOR_ROJO)   # rojo en sintáctica
        marcar_fase(etiqueta_estado_semantico, "Semantica: no ejecutada", COLOR_GRIS)    # semántica gris
    else:                                                                                # sin errores
        marcar_fase(etiqueta_estado_sintactico, "Sintactica: correcta", COLOR_VERDE)     # verde en sintáctica
    return arbol, errores                                                                # devolver al orquestador

# ------------------ Diagrama: ejecutar_fase_semantica ----------------
#   [arbol] -> analizar_semantico -> mostrar tabla -> marcar estado
#   devuelve (tabla, errores_semanticos)
# ---------------------------------------------------------------------
def ejecutar_fase_semantica(arbol):
    tabla, errores = analizar_semantico(arbol)                                           # llamar al semántico
    mostrar_tabla_en_panel(tabla)                                                        # pestaña Tabla
    mostrar_errores_en_panel(errores)                                                    # pestaña Errores
    if len(errores) > 0:                                                                 # ¿hubo error?
        marcar_fase(etiqueta_estado_semantico, "Semantica: con errores", COLOR_ROJO)     # rojo en semántica
    else:                                                                                # sin errores
        marcar_fase(etiqueta_estado_semantico, "Semantica: correcta", COLOR_VERDE)       # verde en semántica
    return tabla, errores                                                                # devolver al orquestador

# ------------------ Diagrama: mostrar_informe_final ------------------
#   [estado, ...] -> informe según en qué fase terminó
# ---------------------------------------------------------------------
def mostrar_informe_final(estado, tokens, errores_lexicos, arbol, errores_sintacticos, tabla, errores_semanticos):
    area_informe_final.insert("end", "=== INFORME FINAL ===\n\n")                         # encabezado
    if estado == "lexico":                                                               # se detuvo en léxico
        area_informe_final.insert("end", "Estado: DETENIDO EN ANALISIS LEXICO\n")        # mensaje claro
        area_informe_final.insert("end", "Se encontraron " + str(len(errores_lexicos)) + " errores lexicos.\n")
        area_informe_final.insert("end", "No se ejecutaron las fases sintactica ni semantica.\n")
        return                                                                           # fin del informe
    if estado == "sintactico":                                                           # se detuvo en sintáctico
        area_informe_final.insert("end", "Estado: DETENIDO EN ANALISIS SINTACTICO\n")    # mensaje
        area_informe_final.insert("end", "Analisis lexico: correcto\n")                  # lo que sí pasó
        area_informe_final.insert("end", "Se encontraron " + str(len(errores_sintacticos)) + " errores sintacticos.\n")
        area_informe_final.insert("end", "No se ejecuto el analisis semantico.\n")
        return                                                                           # fin del informe
    area_informe_final.insert("end", "Estado: ANALISIS COMPLETO\n")                      # llegó al final
    area_informe_final.insert("end", "Analisis lexico: correcto (" + str(len(tokens)) + " tokens)\n")
    area_informe_final.insert("end", "Analisis sintactico: correcto\n")                  # árbol construido
    if len(errores_semanticos) > 0:                                                      # con errores semánticos
        area_informe_final.insert("end", "Analisis semantico: " + str(len(errores_semanticos)) + " errores encontrados.\n")
    else:                                                                                # sin errores
        area_informe_final.insert("end", "Analisis semantico: correcto (" + str(len(tabla)) + " variables declaradas)\n")

# ------------------ Diagrama: analizar_codigo ------------------------
#   [] -> leer editor -> ejecutar fases en orden -> informe final
#   Si una fase falla, no se ejecutan las siguientes.
# ---------------------------------------------------------------------
def analizar_codigo():
    limpiar_todos_los_paneles()                                                          # paneles en blanco
    codigo = editor_codigo.get("1.0", "end-1c")                                          # leer editor
    if codigo.strip() == "":                                                             # editor vacío
        marcar_las_tres_fases_pendientes()                                               # todo en pendiente
        area_informe_final.insert("end", "El editor esta vacio.\n")                      # aviso claro
        return                                                                           # no seguir
    tokens, errores_lexicos = ejecutar_fase_lexica(codigo)                               # fase 1
    if len(errores_lexicos) > 0:                                                         # si hubo error léxico
        mostrar_informe_final("lexico", tokens, errores_lexicos, None, None, None, None) # informe y parar
        return                                                                           # no continuar
    arbol, errores_sintacticos = ejecutar_fase_sintactica(tokens)                        # fase 2
    if len(errores_sintacticos) > 0:                                                     # si hubo error sintáctico
        mostrar_informe_final("sintactico", tokens, errores_lexicos, arbol, errores_sintacticos, None, None)
        return                                                                           # no continuar
    tabla, errores_semanticos = ejecutar_fase_semantica(arbol)                           # fase 3
    mostrar_informe_final("completo", tokens, errores_lexicos, arbol, errores_sintacticos, tabla, errores_semanticos)

# ------------------ Diagrama: crear_ventana_principal ----------------
#   [] -> Tk() con título, tamaño y las tres secciones
# ---------------------------------------------------------------------
def crear_ventana_principal():
    global ventana_principal                                                             # modificamos global
    ventana_principal = tk.Tk()                                                          # ventana raíz
    ventana_principal.title("Compilador Educativo - LenguajeEducativo")                  # título
    ventana_principal.geometry("1200x800")                                               # tamaño inicial
    crear_seccion_editor(ventana_principal)                                              # editor + botones
    crear_seccion_estado_fases(ventana_principal)                                        # etiquetas de fase
    crear_seccion_pestanas(ventana_principal)                                            # 5 pestañas

# ------------------ Diagrama: iniciar_aplicacion ---------------------
#   [] -> crear la ventana y entrar en el bucle de eventos
# ---------------------------------------------------------------------
def iniciar_aplicacion():
    crear_ventana_principal()                                                            # construir UI
    ventana_principal.mainloop()                                                         # bucle Tkinter

# ------------------ Bloque de comprobación directa --------------------
if __name__ == "__main__":
    iniciar_aplicacion()                                                                 # permite probar sin principal.py