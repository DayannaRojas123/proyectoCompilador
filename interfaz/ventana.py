# ventana.py
# =====================================================================
# Ventana principal del compilador educativo (Tkinter).
# Todo procedural: no usamos clases, el estado va en variables globales
# del módulo y cada botón ejecuta una función de nivel superior.
# Las tres fases del compilador se invocan realmente al pulsar "Analizar".
#
# Distribución:
#   ┌ Encabezado ───────────────────────────────────────────────┐
#   ├ Fases:  [Léxica] → [Sintáctica] → [Semántica] ────────────┤
#   ├ Código fuente (editor)      │ Resultados (5 pestañas) ────┤
#   └ Barra de estado ──────────────────────────────────────────┘
#
# ---------------------------------------------------------------------
# EJEMPLO TRAZADO
# ---------------------------------------------------------------------
# Entrada: 'var edad : entero = 2 + 3 * 4;' + 'mostrar edad;' + [Analizar]
# Salida:
#   - Pestaña Tokens: 15 filas (una por token)
#   - Pestaña Árbol: jerarquía con 'Binaria: *' colgando de 'Binaria: +'
#   - Pestaña Tabla de símbolos: 1 fila con 'edad entero 1 5'
#   - Pestaña Errores: "No se encontraron errores"
#   - Pestaña Informe: 'Estado: ANALISIS COMPLETO'
#   - Tarjetas de fase: las tres en verde 'Correcta'
# ---------------------------------------------------------------------

import tkinter as tk
from tkinter import ttk

# Las tres fases del compilador (paquete compilador).
from compilador.analizador_lexico import analizar_lexico
from compilador.analizador_sintactico import analizar_sintactico, formatear_arbol_a_texto
from compilador.analizador_semantico import analizar_semantico, formatear_tabla_simbolos_a_texto

# Piezas de la interfaz (paquete interfaz).
from . import tema
from . import ejemplos
from . import editor
from .formato import formatear_tokens_a_texto, formatear_error

# Compatibilidad con el nombre de colores que usaba la versión anterior.
COLOR_VERDE = tema.COLOR_VERDE                # análisis correcto
COLOR_ROJO = tema.COLOR_ROJO                  # errores encontrados
COLOR_GRIS = tema.COLOR_GRIS                  # no ejecutada o pendiente

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
cuaderno = None                               # Notebook con las pestañas
pestanas = {}                                 # clave -> (frame, título base)
puntos_de_fase = {}                           # etiqueta de estado -> punto de color
etiqueta_resumen = None                       # resumen en el encabezado de resultados
etiqueta_mensaje = None                       # mensaje en la barra de estado
etiqueta_cursor = None                        # "Ln 1, Col 1"
errores_acumulados = []                       # errores del análisis en curso

# Ayudas que se muestran en cada panel antes de analizar.
AYUDAS = {
    "tokens": "Aquí verás la lista de tokens.\nEscribe código y pulsa «Analizar» (Ctrl+Enter).\n",
    "ast": "Aquí verás el árbol sintáctico.\n",
    "simbolos": "Aquí verás la tabla de símbolos.\n",
    "errores": "Aquí verás los errores léxicos, sintácticos y semánticos.\n",
    "informe": "Aquí verás el informe final del análisis.\n",
}


# =====================================================================
# Utilidades para escribir en los paneles de resultados (solo lectura)
# =====================================================================

# ------------------ Diagrama: escribir / borrar ----------------------
#   [area, texto, etiqueta] -> habilitar, insertar, volver a solo lectura
# ---------------------------------------------------------------------
def escribir(area, texto, etiqueta=None):
    area.config(state="normal")                            # permitir escribir
    if etiqueta is None:
        area.insert("end", texto)                          # texto sin formato
    else:
        area.insert("end", texto, etiqueta)                # texto con color/estilo
    area.config(state="disabled")                          # bloquear de nuevo


def borrar(area):
    area.config(state="normal")
    area.delete("1.0", "end")
    area.config(state="disabled")


def esta_vacia(area):
    return area.get("1.0", "end-1c") == ""


# ------------------ Diagrama: configurar_etiquetas_resultado ---------
#   [area] -> define los estilos (colores/negritas) que usan los paneles
# ---------------------------------------------------------------------
def configurar_etiquetas_resultado(area):
    negrita = tema.fuente_codigo(11, "bold")
    area.tag_configure("titulo", foreground=tema.TEXTO, font=tema.fuente_codigo(12, "bold"))
    area.tag_configure("encabezado", foreground=tema.TEXTO_SUAVE, font=negrita)
    area.tag_configure("separador", foreground=tema.BORDE)
    area.tag_configure("suave", foreground=tema.TEXTO_SUAVE)
    area.tag_configure("ok", foreground=tema.COLOR_VERDE, font=negrita)
    area.tag_configure("error", foreground=tema.COLOR_ROJO, font=negrita)
    area.tag_configure("aviso", foreground=tema.COLOR_SINTACTICO, font=negrita)
    area.tag_configure("lexico", foreground=tema.COLOR_LEXICO, font=negrita)
    area.tag_configure("sintactico", foreground=tema.COLOR_SINTACTICO, font=negrita)
    area.tag_configure("semantico", foreground=tema.COLOR_SEMANTICO, font=negrita)
    area.tag_configure("t_palabra", foreground=tema.COLOR_PALABRA)
    area.tag_configure("t_tipo", foreground=tema.COLOR_TIPO)
    area.tag_configure("t_bool", foreground=tema.COLOR_BOOLEANO)
    area.tag_configure("t_numero", foreground=tema.COLOR_NUMERO)
    area.tag_configure("t_cadena", foreground=tema.COLOR_CADENA)
    area.tag_configure("t_oper", foreground="#a5b4c8")
    area.tag_configure("a_programa", foreground=tema.TEXTO, font=negrita)
    area.tag_configure("a_instruccion", foreground=tema.COLOR_TIPO, font=negrita)
    area.tag_configure("a_operacion", foreground=tema.COLOR_SINTACTICO, font=negrita)


# ------------------ Diagrama: crear_area_de_texto --------------------
#   [padre] -> Frame con scroll V y H -> devolver el Text interior
# ---------------------------------------------------------------------
def crear_area_de_texto(padre, ajustar_lineas=False):
    marco = tk.Frame(padre, bg=tema.EDITOR_FONDO)                                     # marco contenedor
    marco.pack(fill="both", expand=True, padx=8, pady=(0, 8))                         # ocupa todo el espacio
    barra_vertical = ttk.Scrollbar(marco, orient="vertical")                          # scroll vertical
    barra_vertical.pack(side="right", fill="y")                                       # a la derecha
    barra_horizontal = ttk.Scrollbar(marco, orient="horizontal")                      # scroll horizontal
    if not ajustar_lineas:
        barra_horizontal.pack(side="bottom", fill="x")                                # abajo
    area = tk.Text(marco, wrap="word" if ajustar_lineas else "none", font=tema.fuente_codigo(11),                   # Text monoespaciado
                   bg=tema.EDITOR_FONDO, fg=tema.TEXTO, relief="flat", bd=0,
                   highlightthickness=0, padx=12, pady=10, spacing1=2, spacing3=2,
                   selectbackground="#264f78", selectforeground="#ffffff",
                   yscrollcommand=barra_vertical.set,                                 # conectado al scroll V
                   xscrollcommand=barra_horizontal.set)                               # conectado al scroll H
    area.pack(side="left", fill="both", expand=True)                                  # ocupa el resto
    barra_vertical.config(command=area.yview)                                         # scroll controla al Text
    barra_horizontal.config(command=area.xview)                                       # scroll controla al Text
    configurar_etiquetas_resultado(area)                                              # colores del panel
    area.tag_raise("sel")
    area.bind("<Button-1>", lambda evento: area.focus_set())                          # permite seleccionar y copiar
    area.config(state="disabled")                                                     # solo lectura
    return area                                                                       # devolvemos el Text


def crear_tarjeta(padre, titulo):
    """Panel con borde fino y una fila de cabecera; devuelve (tarjeta, cabecera)."""
    tarjeta = tk.Frame(padre, bg=tema.PANEL, highlightbackground=tema.BORDE, highlightthickness=1)
    cabecera = tk.Frame(tarjeta, bg=tema.PANEL)
    cabecera.pack(fill="x", padx=14, pady=(12, 8))
    tk.Label(cabecera, text=titulo, bg=tema.PANEL, fg=tema.TEXTO,
             font=tema.fuente_ui(12, "bold")).pack(side="left")
    return tarjeta, cabecera


# =====================================================================
# Construcción de la ventana
# =====================================================================

# ------------------ Diagrama: crear_encabezado -----------------------
#   [raiz] -> logotipo + título + subtítulo
# ---------------------------------------------------------------------
def crear_encabezado(raiz):
    marco = tk.Frame(raiz, bg=tema.FONDO)
    marco.pack(fill="x", padx=20, pady=(16, 6))
    logo = tk.Label(marco, text="{ }", bg=tema.ACENTO, fg="#ffffff",
                    font=tema.fuente_codigo(13, "bold"), width=3, pady=4)
    logo.pack(side="left")
    textos = tk.Frame(marco, bg=tema.FONDO)
    textos.pack(side="left", padx=12)
    tk.Label(textos, text="Compilador Educativo", bg=tema.FONDO, fg=tema.TEXTO,
             font=tema.fuente_ui(17, "bold")).pack(anchor="w")
    tk.Label(textos, text="LenguajeEducativo  ·  análisis léxico, sintáctico y semántico",
             bg=tema.FONDO, fg=tema.TEXTO_SUAVE, font=tema.fuente_ui(10)).pack(anchor="w")


# ------------------ Diagrama: crear_seccion_estado_fases -------------
#   [raiz] -> tres tarjetas (léxica → sintáctica → semántica)
# ---------------------------------------------------------------------
def crear_seccion_estado_fases(raiz):
    global etiqueta_estado_lexico, etiqueta_estado_sintactico, etiqueta_estado_semantico  # modificamos globales
    marco_fases = tk.Frame(raiz, bg=tema.FONDO)                                       # fila de fases
    marco_fases.pack(fill="x", padx=20, pady=(8, 10))
    for columna in (0, 2, 4):
        marco_fases.columnconfigure(columna, weight=1, uniform="fase")                # tres tarjetas iguales
    etiquetas = []
    for posicion, (numero, titulo) in enumerate([("1", "Análisis léxico"),
                                                  ("2", "Análisis sintáctico"),
                                                  ("3", "Análisis semántico")]):
        tarjeta = tk.Frame(marco_fases, bg=tema.PANEL, highlightbackground=tema.BORDE, highlightthickness=1)
        tarjeta.grid(row=0, column=posicion * 2, sticky="ew")
        punto = tk.Canvas(tarjeta, width=14, height=14, bg=tema.PANEL, highlightthickness=0, bd=0)
        circulo = punto.create_oval(1, 1, 13, 13, fill=tema.COLOR_GRIS, outline="")   # indicador de color
        punto.pack(side="left", padx=(16, 10), pady=10)
        textos = tk.Frame(tarjeta, bg=tema.PANEL)
        textos.pack(side="left", pady=8)
        tk.Label(textos, text=numero + " · " + titulo, bg=tema.PANEL, fg=tema.TEXTO,
                 font=tema.fuente_ui(10, "bold")).pack(anchor="w")
        estado = tk.Label(textos, text="Pendiente", bg=tema.PANEL, fg=tema.COLOR_GRIS, font=tema.fuente_ui(10))
        estado.pack(anchor="w")
        puntos_de_fase[estado] = (punto, circulo)
        etiquetas.append(estado)
        if posicion < 2:                                                              # flecha entre tarjetas
            flecha = tk.Canvas(marco_fases, width=34, height=16, bg=tema.FONDO, highlightthickness=0, bd=0)
            flecha.create_line(6, 8, 26, 8, fill=tema.TEXTO_SUAVE, width=2)
            flecha.create_line(20, 2, 27, 8, 20, 14, fill=tema.TEXTO_SUAVE, width=2)
            flecha.grid(row=0, column=posicion * 2 + 1, padx=6)
    etiqueta_estado_lexico, etiqueta_estado_sintactico, etiqueta_estado_semantico = etiquetas


# ------------------ Diagrama: crear_seccion_editor -------------------
#   [contenedor] -> tarjeta con editor, botones (Analizar, Limpiar) y ejemplos
# ---------------------------------------------------------------------
def crear_seccion_editor(contenedor):
    global editor_codigo
    tarjeta, cabecera = crear_tarjeta(contenedor, "Código fuente")                    # tarjeta con título
    ttk.Button(cabecera, text="Limpiar", style="Secondary.TButton",
               command=limpiar_editor).pack(side="right", padx=(8, 0))                # vacía editor
    ttk.Button(cabecera, text="Analizar", style="Accent.TButton",
               command=analizar_codigo).pack(side="right")                            # dispara el compilador
    marco_editor = tk.Frame(tarjeta, bg=tema.EDITOR_FONDO, highlightbackground=tema.BORDE,
                            highlightthickness=1)                                     # borde del editor
    marco_editor.pack(fill="both", expand=True, padx=14)
    editor_codigo = editor.crear_editor(marco_editor, actualizar_posicion_cursor)     # editor real
    pie = tk.Frame(tarjeta, bg=tema.PANEL)                                            # fila de ejemplos
    pie.pack(fill="x", padx=14, pady=(10, 14))
    tk.Label(pie, text="Ejemplos", bg=tema.PANEL, fg=tema.TEXTO_SUAVE,
             font=tema.fuente_ui(9, "bold")).pack(side="left", padx=(0, 8))
    for texto, accion in [("Válido", cargar_ejemplo_valido),                          # ejemplo OK
                          ("Error léxico", cargar_ejemplo_error_lexico),              # ejemplo error léxico
                          ("Error sintáctico", cargar_ejemplo_error_sintactico),      # ejemplo sintáctico
                          ("Error semántico", cargar_ejemplo_error_semantico),        # ejemplo semántico
                          ("Precedencia", cargar_ejemplo_precedencia)]:               # ejemplo paréntesis
        ttk.Button(pie, text=texto, style="Chip.TButton", command=accion).pack(side="left", padx=(0, 6))
    editor_codigo.bind("<Control-Return>", lambda evento: (analizar_codigo(), "break")[1])  # atajo
    return tarjeta


# ------------------ Diagrama: crear_seccion_pestanas -----------------
#   [contenedor] -> tarjeta con Notebook de 5 pestañas, cada una con su Text
# ---------------------------------------------------------------------
def crear_seccion_pestanas(contenedor):
    global area_tokens, area_ast, area_tabla_simbolos, area_errores, area_informe_final  # globales
    global cuaderno, etiqueta_resumen
    tarjeta, cabecera = crear_tarjeta(contenedor, "Resultados")
    etiqueta_resumen = tk.Label(cabecera, text="", bg=tema.PANEL, fg=tema.TEXTO_SUAVE, font=tema.fuente_ui(10))
    etiqueta_resumen.pack(side="right")
    cuaderno = ttk.Notebook(tarjeta)                                                  # contenedor de pestañas
    cuaderno.pack(fill="both", expand=True, padx=6, pady=(0, 6))
    areas = {}
    for clave, titulo in [("tokens", "Tokens"), ("ast", "Árbol sintáctico"),
                          ("simbolos", "Tabla de símbolos"), ("errores", "Errores"),
                          ("informe", "Informe final")]:
        marco = tk.Frame(cuaderno, bg=tema.EDITOR_FONDO)                              # una pestaña
        cuaderno.add(marco, text=titulo)
        pestanas[clave] = (marco, titulo)
        areas[clave] = crear_area_de_texto(marco, clave in ("errores", "informe"))  # Text de la pestaña
    area_tokens, area_ast, area_tabla_simbolos = areas["tokens"], areas["ast"], areas["simbolos"]
    area_errores, area_informe_final = areas["errores"], areas["informe"]
    return tarjeta


# ------------------ Diagrama: crear_barra_estado ---------------------
#   [raiz] -> franja inferior con mensaje y posición del cursor
# ---------------------------------------------------------------------
def crear_barra_estado(raiz):
    global etiqueta_mensaje, etiqueta_cursor
    barra = tk.Frame(raiz, bg=tema.PANEL, highlightbackground=tema.BORDE, highlightthickness=1)
    barra.pack(side="bottom", fill="x")
    etiqueta_mensaje = tk.Label(barra, text="Listo  ·  Ctrl+Enter para analizar", bg=tema.PANEL,
                                fg=tema.TEXTO_SUAVE, font=tema.fuente_ui(9), anchor="w")
    etiqueta_mensaje.pack(side="left", padx=14, pady=5)
    etiqueta_cursor = tk.Label(barra, text="Ln 1, Col 1", bg=tema.PANEL, fg=tema.TEXTO_SUAVE,
                               font=tema.fuente_ui(9))
    etiqueta_cursor.pack(side="right", padx=14)


def actualizar_posicion_cursor(linea, columna):
    etiqueta_cursor.config(text="Ln " + str(linea) + ", Col " + str(columna))


def mostrar_mensaje(texto, color=None):
    etiqueta_mensaje.config(text=texto, fg=color or tema.TEXTO_SUAVE)


# =====================================================================
# Acciones de los botones
# =====================================================================

# ------------------ Diagrama: limpiar_editor -------------------------
#   [] -> vaciar el editor y reiniciar los paneles y estados
# ---------------------------------------------------------------------
def limpiar_editor():
    editor_codigo.delete("1.0", "end")                     # borrar todo el texto del editor
    editor.quitar_marcas_de_error()                        # sin líneas en rojo
    reiniciar_resultados()                                 # paneles, fases y resumen a cero
    editor_codigo.focus_set()                              # listo para escribir


# ------------------ Diagrama: colocar_codigo_en_editor ---------------
#   [texto] -> reemplazar contenido y limpiar paneles/estados
# ---------------------------------------------------------------------
def colocar_codigo_en_editor(texto_del_ejemplo):
    editor_codigo.delete("1.0", "end")                     # vaciar el editor primero
    editor_codigo.insert("1.0", texto_del_ejemplo)         # pegar el ejemplo
    editor.quitar_marcas_de_error()                        # sin líneas en rojo
    reiniciar_resultados()                                 # paneles y fases a cero
    editor_codigo.focus_set()


def reiniciar_resultados():
    limpiar_todos_los_paneles()                            # vaciar todas las pestañas
    mostrar_ayudas_iniciales()                             # mensajes guía
    marcar_las_tres_fases_pendientes()                     # volver a "pendiente"
    actualizar_titulos_de_pestanas({})                     # sin contadores
    etiqueta_resumen.config(text="")
    mostrar_mensaje("Listo  ·  Ctrl+Enter para analizar")


def mostrar_ayudas_iniciales():
    for clave, area in [("tokens", area_tokens), ("ast", area_ast), ("simbolos", area_tabla_simbolos),
                        ("errores", area_errores), ("informe", area_informe_final)]:
        escribir(area, AYUDAS[clave], "suave")


# ------------------ Ejemplos (cada botón llama a una de estas) -------
def cargar_ejemplo_valido():
    colocar_codigo_en_editor(ejemplos.EJEMPLO_VALIDO)

def cargar_ejemplo_error_lexico():
    colocar_codigo_en_editor(ejemplos.EJEMPLO_ERROR_LEXICO)

def cargar_ejemplo_error_sintactico():
    colocar_codigo_en_editor(ejemplos.EJEMPLO_ERROR_SINTACTICO)

def cargar_ejemplo_error_semantico():
    colocar_codigo_en_editor(ejemplos.EJEMPLO_ERROR_SEMANTICO)

def cargar_ejemplo_precedencia():
    colocar_codigo_en_editor(ejemplos.EJEMPLO_PRECEDENCIA)


# ------------------ Diagrama: marcar_fase ----------------------------
#   [etiqueta, texto, color] -> actualizar texto y color de una fase
# ---------------------------------------------------------------------
def marcar_fase(etiqueta, texto, color):
    etiqueta.config(text=texto, fg=color)                  # cambio de texto y color
    punto, circulo = puntos_de_fase[etiqueta]
    punto.itemconfig(circulo, fill=color)                  # el punto toma el mismo color


# ------------------ Diagrama: marcar_las_tres_fases_pendientes -------
#   [] -> poner las tres etiquetas en "pendiente" y color gris
# ---------------------------------------------------------------------
def marcar_las_tres_fases_pendientes():
    marcar_fase(etiqueta_estado_lexico, "Pendiente", COLOR_GRIS)         # léxica
    marcar_fase(etiqueta_estado_sintactico, "Pendiente", COLOR_GRIS)     # sintáctica
    marcar_fase(etiqueta_estado_semantico, "Pendiente", COLOR_GRIS)      # semántica


# ------------------ Diagrama: limpiar_todos_los_paneles --------------
#   [] -> borrar el contenido de cada pestaña de texto
# ---------------------------------------------------------------------
def limpiar_todos_los_paneles():
    borrar(area_tokens)                                    # tokens
    borrar(area_ast)                                       # árbol
    borrar(area_tabla_simbolos)                            # tabla de símbolos
    borrar(area_errores)                                   # errores
    borrar(area_informe_final)                             # informe


def actualizar_titulos_de_pestanas(conteos):
    """Pone contadores en los títulos: 'Tokens (15)', 'Errores (2)'."""
    for clave, (marco, titulo) in pestanas.items():
        if clave in conteos:
            cuaderno.tab(marco, text=titulo + "  (" + str(conteos[clave]) + ")")
        else:
            cuaderno.tab(marco, text=titulo)


# =====================================================================
# Mostrar resultados de cada fase
# =====================================================================

def etiqueta_de_token(tipo):
    """Estilo de color según la categoría del token."""
    if tipo in ("PALABRA_RESERVADA", "OPERADOR_Y", "OPERADOR_O", "OPERADOR_NO"):
        return "t_palabra"
    if tipo == "TIPO_DATO":
        return "t_tipo"
    if tipo == "BOOLEANO_LITERAL":
        return "t_bool"
    if tipo in ("ENTERO", "DECIMAL"):
        return "t_numero"
    if tipo == "CADENA":
        return "t_cadena"
    if tipo == "IDENTIFICADOR":
        return None
    if tipo == "FIN":
        return "suave"
    return "t_oper"                                        # operadores y puntuación


# ------------------ Diagrama: mostrar_tokens_en_panel ----------------
#   [tokens] -> escribir el texto tabular en area_tokens (con color)
# ---------------------------------------------------------------------
def mostrar_tokens_en_panel(tokens):
    lineas = formatear_tokens_a_texto(tokens).splitlines(keepends=True)                 # delegar formateo
    escribir(area_tokens, lineas[0], "encabezado")                                       # encabezado
    escribir(area_tokens, lineas[1], "separador")                                        # línea separadora
    for token, linea in zip(tokens, lineas[2:]):                                         # una fila por token
        escribir(area_tokens, linea[:18], "suave")                                       # línea y columna
        escribir(area_tokens, linea[18:42], etiqueta_de_token(token[0]))                 # tipo con su color
        escribir(area_tokens, linea[42:])                                                # lexema y valor


# ------------------ Diagrama: mostrar_ast_en_panel -------------------
#   [arbol] -> escribir el árbol indentado en area_ast (con color)
# ---------------------------------------------------------------------
def mostrar_ast_en_panel(arbol):
    for linea in formatear_arbol_a_texto(arbol, 0).splitlines(keepends=True):           # delegar formateo
        palabra = linea.strip().split(" ")[0]
        if palabra == "Programa":
            etiqueta = "a_programa"
        elif palabra in ("Declaracion", "Asignacion", "Mostrar"):
            etiqueta = "a_instruccion"
        elif palabra in ("Binaria:", "Unaria:"):
            etiqueta = "a_operacion"
        elif palabra in ("entero:", "decimal:"):
            etiqueta = "t_numero"
        elif palabra == "cadena:":
            etiqueta = "t_cadena"
        elif palabra == "booleano:":
            etiqueta = "t_bool"
        else:
            etiqueta = None
        escribir(area_ast, linea, etiqueta)


# ------------------ Diagrama: mostrar_tabla_en_panel -----------------
#   [tabla] -> escribir la tabla de símbolos formateada en area_tabla_simbolos
# ---------------------------------------------------------------------
def mostrar_tabla_en_panel(tabla):
    lineas = formatear_tabla_simbolos_a_texto(tabla).splitlines(keepends=True)          # delegar formateo
    for numero, linea in enumerate(lineas):
        if len(tabla) == 0:
            etiqueta = "suave"                                                           # tabla vacía
        elif numero == 0:
            etiqueta = "encabezado"                                                      # encabezado
        else:
            etiqueta = None
        escribir(area_tabla_simbolos, linea, etiqueta)


# ------------------ Diagrama: mostrar_errores_en_panel ---------------
#   [errores] -> escribir una línea por error; no borrar los ya mostrados
# ---------------------------------------------------------------------
def mostrar_errores_en_panel(errores):
    for error in errores:                                                                # recorrer errores
        errores_acumulados.append(error)                                                 # para marcar el editor
        texto = formatear_error(error)                                                   # "[TIPO] mensaje (...)"
        prefijo = "[" + error[0] + "]"
        escribir(area_errores, prefijo, error[0].lower())                                # tipo con color
        escribir(area_errores, texto[len(prefijo):])                                     # resto del mensaje


# ------------------ Diagrama: ejecutar_fase_lexica -------------------
#   [codigo] -> analizar_lexico -> mostrar tokens -> marcar estado
#   devuelve (tokens, errores_lexicos)
# ---------------------------------------------------------------------
def ejecutar_fase_lexica(codigo):
    tokens, errores = analizar_lexico(codigo)                                            # llamar al lexer
    mostrar_tokens_en_panel(tokens)                                                      # pestaña Tokens
    mostrar_errores_en_panel(errores)                                                    # pestaña Errores
    if len(errores) > 0:                                                                 # ¿hubo error léxico?
        marcar_fase(etiqueta_estado_lexico, "Con errores", COLOR_ROJO)                   # rojo en léxica
        marcar_fase(etiqueta_estado_sintactico, "No ejecutada", COLOR_GRIS)              # sintáctica gris
        marcar_fase(etiqueta_estado_semantico, "No ejecutada", COLOR_GRIS)               # semántica gris
    else:                                                                                # sin errores
        marcar_fase(etiqueta_estado_lexico, "Correcta", COLOR_VERDE)                     # verde en léxica
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
        marcar_fase(etiqueta_estado_sintactico, "Con errores", COLOR_ROJO)               # rojo en sintáctica
        marcar_fase(etiqueta_estado_semantico, "No ejecutada", COLOR_GRIS)               # semántica gris
    else:                                                                                # sin errores
        marcar_fase(etiqueta_estado_sintactico, "Correcta", COLOR_VERDE)                 # verde en sintáctica
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
        marcar_fase(etiqueta_estado_semantico, "Con errores", COLOR_ROJO)                # rojo en semántica
    else:                                                                                # sin errores
        marcar_fase(etiqueta_estado_semantico, "Correcta", COLOR_VERDE)                  # verde en semántica
    return tabla, errores                                                                # devolver al orquestador


# ------------------ Diagrama: mostrar_informe_final ------------------
#   [estado, ...] -> informe según en qué fase terminó
# ---------------------------------------------------------------------
def mostrar_informe_final(estado, tokens, errores_lexicos, arbol, errores_sintacticos, tabla, errores_semanticos):
    informe = area_informe_final
    escribir(informe, "=== INFORME FINAL ===\n\n", "titulo")                              # encabezado
    if estado == "lexico":                                                               # se detuvo en léxico
        escribir(informe, "Estado: DETENIDO EN ANALISIS LEXICO\n", "error")              # mensaje claro
        escribir(informe, "Se encontraron " + str(len(errores_lexicos)) + " errores lexicos.\n")
        escribir(informe, "No se ejecutaron las fases sintactica ni semantica.\n", "suave")
        return                                                                           # fin del informe
    if estado == "sintactico":                                                           # se detuvo en sintáctico
        escribir(informe, "Estado: DETENIDO EN ANALISIS SINTACTICO\n", "error")          # mensaje
        escribir(informe, "Analisis lexico: correcto\n", "ok")                           # lo que sí pasó
        escribir(informe, "Se encontraron " + str(len(errores_sintacticos)) + " errores sintacticos.\n")
        escribir(informe, "No se ejecuto el analisis semantico.\n", "suave")
        return                                                                           # fin del informe
    if len(errores_semanticos) > 0:                                                      # con errores semánticos
        escribir(informe, "Estado: ANALISIS COMPLETO\n", "aviso")                        # llegó al final
    else:
        escribir(informe, "Estado: ANALISIS COMPLETO\n", "ok")
    escribir(informe, "Analisis lexico: correcto (" + str(len(tokens)) + " tokens)\n", "ok")
    escribir(informe, "Analisis sintactico: correcto\n", "ok")                           # árbol construido
    if len(errores_semanticos) > 0:                                                      # con errores semánticos
        escribir(informe, "Analisis semantico: " + str(len(errores_semanticos)) + " errores encontrados.\n", "error")
    else:                                                                                # sin errores
        escribir(informe, "Analisis semantico: correcto (" + str(len(tabla)) + " variables declaradas)\n", "ok")


# ------------------ Diagrama: analizar_codigo ------------------------
#   [] -> leer editor -> ejecutar fases en orden -> informe final
#   Si una fase falla, no se ejecutan las siguientes.
# ---------------------------------------------------------------------
def analizar_codigo():
    limpiar_todos_los_paneles()                                                          # paneles en blanco
    errores_acumulados.clear()                                                           # sin errores previos
    editor.quitar_marcas_de_error()                                                      # editor sin marcas
    codigo = editor_codigo.get("1.0", "end-1c")                                          # leer editor
    if codigo.strip() == "":                                                             # editor vacío
        marcar_las_tres_fases_pendientes()                                               # todo en pendiente
        escribir(area_informe_final, "El editor esta vacio.\n", "aviso")                 # aviso claro
        actualizar_titulos_de_pestanas({})
        etiqueta_resumen.config(text="")
        mostrar_mensaje("El editor está vacío", tema.COLOR_SINTACTICO)
        cuaderno.select(pestanas["informe"][0])                                          # mostrar el aviso
        return                                                                           # no seguir
    estado = "completo"
    tokens, errores_lexicos = ejecutar_fase_lexica(codigo)                               # fase 1
    arbol = tabla = errores_sintacticos = errores_semanticos = None
    if len(errores_lexicos) > 0:                                                         # si hubo error léxico
        estado = "lexico"
    else:
        arbol, errores_sintacticos = ejecutar_fase_sintactica(tokens)                    # fase 2
        if len(errores_sintacticos) > 0:                                                 # si hubo error sintáctico
            estado = "sintactico"
        else:
            tabla, errores_semanticos = ejecutar_fase_semantica(arbol)                   # fase 3
    mostrar_informe_final(estado, tokens, errores_lexicos, arbol, errores_sintacticos, tabla, errores_semanticos)
    terminar_analisis(estado, tokens, tabla)


# ------------------ Diagrama: terminar_analisis ----------------------
#   [estado, tokens, tabla] -> rellenar vacíos, contadores, marcas y mensaje
# ---------------------------------------------------------------------
def terminar_analisis(estado, tokens, tabla):
    total_errores = len(errores_acumulados)
    if total_errores == 0:
        escribir(area_errores, "No se encontraron errores.\n", "ok")
    for area in (area_ast, area_tabla_simbolos):                                         # fases no ejecutadas
        if esta_vacia(area):
            escribir(area, "Esta fase no se ejecutó porque una fase anterior tuvo errores.\n", "suave")
    editor.marcar_errores_en_editor(errores_acumulados)                                  # líneas en rojo
    conteos = {"tokens": len(tokens)}
    if tabla is not None:
        conteos["simbolos"] = len(tabla)
    if total_errores > 0:
        conteos["errores"] = total_errores
    actualizar_titulos_de_pestanas(conteos)
    etiqueta_resumen.config(text=str(len(tokens)) + " tokens  ·  " + str(total_errores) +
                            (" error" if total_errores == 1 else " errores"))
    if estado == "lexico":
        mostrar_mensaje("Detenido en el análisis léxico  ·  " + str(total_errores) + " error(es)", tema.COLOR_ROJO)
    elif estado == "sintactico":
        mostrar_mensaje("Detenido en el análisis sintáctico  ·  " + str(total_errores) + " error(es)", tema.COLOR_ROJO)
    elif total_errores > 0:
        mostrar_mensaje("Análisis completo con errores semánticos  ·  " + str(total_errores) + " error(es)", tema.COLOR_ROJO)
    else:
        mostrar_mensaje("Análisis completo sin errores", tema.COLOR_VERDE)
    if total_errores > 0:
        cuaderno.select(pestanas["errores"][0])                                          # llevar al usuario a los errores


# ------------------ Diagrama: crear_ventana_principal ----------------
#   [] -> Tk() con título, tamaño y todas las secciones
# ---------------------------------------------------------------------
def crear_ventana_principal():
    global ventana_principal                                                             # modificamos global
    tema.habilitar_nitidez_en_windows()                                                  # texto nítido en Windows
    ventana_principal = tk.Tk()                                                          # ventana raíz
    ventana_principal.title("Compilador Educativo - LenguajeEducativo")                  # título
    tema.aplicar_estilos(ventana_principal)                                              # colores y estilos ttk
    ancho = min(1320, ventana_principal.winfo_screenwidth() - 80)                        # tamaño inicial
    alto = min(820, ventana_principal.winfo_screenheight() - 100)
    x = (ventana_principal.winfo_screenwidth() - ancho) // 2                             # centrada
    y = max((ventana_principal.winfo_screenheight() - alto) // 3, 0)
    ventana_principal.geometry(str(ancho) + "x" + str(alto) + "+" + str(x) + "+" + str(y))
    ventana_principal.minsize(980, 620)

    crear_encabezado(ventana_principal)                                                  # título de la app
    crear_seccion_estado_fases(ventana_principal)                                        # tarjetas de fase
    crear_barra_estado(ventana_principal)                                                # franja inferior
    cuerpo = tk.PanedWindow(ventana_principal, orient="horizontal", sashwidth=10,        # editor | resultados
                            bg=tema.FONDO, bd=0, sashrelief="flat", opaqueresize=True)
    cuerpo.pack(fill="both", expand=True, padx=20, pady=(0, 14))
    cuerpo.add(crear_seccion_editor(cuerpo), minsize=380, stretch="always", width=int(ancho * 0.44))
    cuerpo.add(crear_seccion_pestanas(cuerpo), minsize=420, stretch="always")

    ventana_principal.bind("<F5>", lambda evento: analizar_codigo())                     # atajo alternativo
    reiniciar_resultados()                                                               # estado inicial
    colocar_codigo_en_editor(ejemplos.EJEMPLO_VALIDO)                                    # arranca con un ejemplo
    editor_codigo.focus_set()


# ------------------ Diagrama: iniciar_aplicacion ---------------------
#   [] -> crear la ventana y entrar en el bucle de eventos
# ---------------------------------------------------------------------
def iniciar_aplicacion():
    crear_ventana_principal()                                                            # construir UI
    ventana_principal.mainloop()                                                         # bucle Tkinter


# ------------------ Bloque de comprobación directa --------------------
if __name__ == "__main__":
    iniciar_aplicacion()                                                                 # python -m interfaz.ventana
