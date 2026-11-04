# ventana.py
# =====================================================================
# Ventana principal del compilador educativo (Tkinter).
# Todo procedural: no usamos clases, el estado va en variables globales
# del módulo y cada botón ejecuta una función de nivel superior.
# =====================================================================
import tkinter as tk
from tkinter import ttk

from compilador.analizador_lexico import analizar_lexico
from compilador.analizador_sintactico import analizar_sintactico, formatear_arbol_a_texto
from compilador.analizador_semantico import analizar_semantico, formatear_tabla_simbolos_a_texto

from . import tema
from . import ejemplos
from . import editor
from .formato import formatear_tokens_a_texto, formatear_error

COLOR_VERDE = tema.COLOR_VERDE
COLOR_ROJO = tema.COLOR_ROJO
COLOR_GRIS = tema.COLOR_GRIS

ventana_principal = None
editor_codigo = None
etiqueta_estado_lexico = None
etiqueta_estado_sintactico = None
etiqueta_estado_semantico = None
area_tokens = None
area_ast = None
area_tabla_simbolos = None
area_errores = None
area_informe_final = None
cuaderno = None
pestanas = {}
puntos_de_fase = {}
etiqueta_resumen = None
etiqueta_mensaje = None
etiqueta_cursor = None
errores_acumulados = []

AYUDAS = {
    "tokens": "Aquí verás la lista de tokens.\nEscribe código y pulsa «Analizar» (Ctrl+Enter).\n",
    "ast": "Aquí verás el árbol sintáctico.\n",
    "simbolos": "Aquí verás la tabla de símbolos.\n",
    "errores": "Aquí verás los errores léxicos, sintácticos y semánticos.\n",
    "informe": "Aquí verás el informe final del análisis.\n",
}

# ------------------ Diagrama: escribir -------------------------------
#   [area, texto, etiqueta] -> habilitar, insertar, volver a solo lectura
# ---------------------------------------------------------------------
def escribir(area, texto, etiqueta=None):
    area.config(state="normal")
    if etiqueta is None:
        area.insert("end", texto)
    else:
        area.insert("end", texto, etiqueta)
    area.config(state="disabled")

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
    marco = tk.Frame(padre, bg=tema.EDITOR_FONDO)
    marco.pack(fill="both", expand=True, padx=8, pady=(0, 8))
    barra_vertical = ttk.Scrollbar(marco, orient="vertical")
    barra_vertical.pack(side="right", fill="y")
    barra_horizontal = ttk.Scrollbar(marco, orient="horizontal")
    if not ajustar_lineas:
        barra_horizontal.pack(side="bottom", fill="x")
    area = tk.Text(marco, wrap="word" if ajustar_lineas else "none", font=tema.fuente_codigo(11),
                   bg=tema.EDITOR_FONDO, fg=tema.TEXTO, relief="flat", bd=0,
                   highlightthickness=0, padx=12, pady=10, spacing1=2, spacing3=2,
                   selectbackground="#264f78", selectforeground="#ffffff",
                   yscrollcommand=barra_vertical.set, xscrollcommand=barra_horizontal.set)
    area.pack(side="left", fill="both", expand=True)
    barra_vertical.config(command=area.yview)
    barra_horizontal.config(command=area.xview)
    configurar_etiquetas_resultado(area)
    area.tag_raise("sel")
    area.bind("<Button-1>", lambda evento: area.focus_set())
    area.config(state="disabled")
    return area

def crear_tarjeta(padre, titulo):
    tarjeta = tk.Frame(padre, bg=tema.PANEL, highlightbackground=tema.BORDE, highlightthickness=1)
    cabecera = tk.Frame(tarjeta, bg=tema.PANEL)
    cabecera.pack(fill="x", padx=14, pady=(12, 8))
    tk.Label(cabecera, text=titulo, bg=tema.PANEL, fg=tema.TEXTO,
             font=tema.fuente_ui(12, "bold")).pack(side="left")
    return tarjeta, cabecera

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

# ------------------ Diagrama: crear_tarjeta_fase ---------------------
#   [marco_fases, posicion, numero, titulo] -> tarjeta con indicador
# ---------------------------------------------------------------------
def crear_tarjeta_fase(marco_fases, posicion, numero, titulo):
    tarjeta = tk.Frame(marco_fases, bg=tema.PANEL, highlightbackground=tema.BORDE, highlightthickness=1)
    tarjeta.grid(row=0, column=posicion * 2, sticky="ew")
    punto = tk.Canvas(tarjeta, width=14, height=14, bg=tema.PANEL, highlightthickness=0, bd=0)
    circulo = punto.create_oval(1, 1, 13, 13, fill=tema.COLOR_GRIS, outline="")
    punto.pack(side="left", padx=(16, 10), pady=10)
    textos = tk.Frame(tarjeta, bg=tema.PANEL)
    textos.pack(side="left", pady=8)
    tk.Label(textos, text=numero + " · " + titulo, bg=tema.PANEL, fg=tema.TEXTO,
             font=tema.fuente_ui(10, "bold")).pack(anchor="w")
    estado = tk.Label(textos, text="Pendiente", bg=tema.PANEL, fg=tema.COLOR_GRIS, font=tema.fuente_ui(10))
    estado.pack(anchor="w")
    puntos_de_fase[estado] = (punto, circulo)
    return estado

def crear_flecha(marco_fases, posicion):
    flecha = tk.Canvas(marco_fases, width=34, height=16, bg=tema.FONDO, highlightthickness=0, bd=0)
    flecha.create_line(6, 8, 26, 8, fill=tema.TEXTO_SUAVE, width=2)
    flecha.create_line(20, 2, 27, 8, 20, 14, fill=tema.TEXTO_SUAVE, width=2)
    flecha.grid(row=0, column=posicion * 2 + 1, padx=6)

# ------------------ Diagrama: crear_seccion_estado_fases -------------
#   [raiz] -> tres tarjetas (léxica → sintáctica → semántica)
# ---------------------------------------------------------------------
def crear_seccion_estado_fases(raiz):
    global etiqueta_estado_lexico, etiqueta_estado_sintactico, etiqueta_estado_semantico
    marco_fases = tk.Frame(raiz, bg=tema.FONDO)
    marco_fases.pack(fill="x", padx=20, pady=(8, 10))
    for columna in (0, 2, 4):
        marco_fases.columnconfigure(columna, weight=1, uniform="fase")
    fases = [("1", "Análisis léxico"), ("2", "Análisis sintáctico"), ("3", "Análisis semántico")]
    etiquetas = []
    for posicion, (numero, titulo) in enumerate(fases):
        etiquetas.append(crear_tarjeta_fase(marco_fases, posicion, numero, titulo))
        if posicion < 2:
            crear_flecha(marco_fases, posicion)
    etiqueta_estado_lexico, etiqueta_estado_sintactico, etiqueta_estado_semantico = etiquetas

# ------------------ Diagrama: crear_seccion_editor -------------------
#   [contenedor] -> tarjeta con editor y botones de ejemplos
# ---------------------------------------------------------------------
def crear_seccion_editor(contenedor):
    global editor_codigo
    tarjeta, cabecera = crear_tarjeta(contenedor, "Código fuente")
    ttk.Button(cabecera, text="Limpiar", style="Secondary.TButton",
               command=limpiar_editor).pack(side="right", padx=(8, 0))
    ttk.Button(cabecera, text="Analizar", style="Accent.TButton",
               command=analizar_codigo).pack(side="right")
    
    # 1. EL PIE CON LOS BOTONES VA PRIMERO Y ANCLADO AL FONDO (bottom)
    pie = tk.Frame(tarjeta, bg=tema.PANEL)
    pie.pack(side="bottom", fill="x", padx=14, pady=(10, 14))
    tk.Label(pie, text="Ejemplos", bg=tema.PANEL, fg=tema.TEXTO_SUAVE,
             font=tema.fuente_ui(9, "bold")).pack(anchor="w", pady=(0, 4))
             
    fila1 = tk.Frame(pie, bg=tema.PANEL)
    fila1.pack(fill="x", pady=2)
    botones_fila1 = [("Válido", cargar_ejemplo_valido), ("Error léxico", cargar_ejemplo_error_lexico), 
                     ("Error sintáctico", cargar_ejemplo_error_sintactico), ("Error semántico", cargar_ejemplo_error_semantico)]
    for texto, accion in botones_fila1:
        ttk.Button(fila1, text=texto, style="Chip.TButton", command=accion).pack(side="left", padx=(0, 6))
        
    fila2 = tk.Frame(pie, bg=tema.PANEL)
    fila2.pack(fill="x", pady=2)
    botones_fila2 = [("Precedencia", cargar_ejemplo_precedencia), ("Relacionales", cargar_ejemplo_relacionales), 
                     ("No declarada", cargar_ejemplo_no_declarada), ("Duplicada", cargar_ejemplo_duplicada)]
    for texto, accion in botones_fila2:
        ttk.Button(fila2, text=texto, style="Chip.TButton", command=accion).pack(side="left", padx=(0, 6))

    # 2. EL EDITOR VA DESPUÉS Y OCUPA EL RESTO DEL ESPACIO
    marco_editor = tk.Frame(tarjeta, bg=tema.EDITOR_FONDO, highlightbackground=tema.BORDE, highlightthickness=1)
    marco_editor.pack(fill="both", expand=True, padx=14, pady=(0, 10))
    editor_codigo = editor.crear_editor(marco_editor, actualizar_posicion_cursor)

    editor_codigo.bind("<Control-Return>", lambda evento: (analizar_codigo(), "break")[1])
    return tarjeta

# ------------------ Diagrama: crear_seccion_pestanas -----------------
#   [contenedor] -> tarjeta con Notebook de 5 pestañas, cada una con su Text
# ---------------------------------------------------------------------
def crear_seccion_pestanas(contenedor):
    global area_tokens, area_ast, area_tabla_simbolos, area_errores, area_informe_final
    global cuaderno, etiqueta_resumen
    tarjeta, cabecera = crear_tarjeta(contenedor, "Resultados")
    etiqueta_resumen = tk.Label(cabecera, text="", bg=tema.PANEL, fg=tema.TEXTO_SUAVE, font=tema.fuente_ui(10))
    etiqueta_resumen.pack(side="right")
    cuaderno = ttk.Notebook(tarjeta)
    cuaderno.pack(fill="both", expand=True, padx=6, pady=(0, 6))
    areas = {}
    for clave, titulo in [("tokens", "Tokens"), ("ast", "Árbol sintáctico"),
                          ("simbolos", "Tabla de símbolos"), ("errores", "Errores"),
                          ("informe", "Informe final")]:
        marco = tk.Frame(cuaderno, bg=tema.EDITOR_FONDO)
        cuaderno.add(marco, text=titulo)
        pestanas[clave] = (marco, titulo)
        areas[clave] = crear_area_de_texto(marco, clave in ("errores", "informe"))
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
    etiqueta_cursor = tk.Label(barra, text="Ln 1, Col 1", bg=tema.PANEL, fg=tema.TEXTO_SUAVE, font=tema.fuente_ui(9))
    etiqueta_cursor.pack(side="right", padx=14)

def actualizar_posicion_cursor(linea, columna):
    etiqueta_cursor.config(text="Ln " + str(linea) + ", Col " + str(columna))

def mostrar_mensaje(texto, color=None):
    etiqueta_mensaje.config(text=texto, fg=color or tema.TEXTO_SUAVE)

# ------------------ Diagrama: limpiar_editor -------------------------
#   [] -> vaciar el editor y reiniciar los paneles y estados
# ---------------------------------------------------------------------
def limpiar_editor():
    editor_codigo.delete("1.0", "end")
    editor.quitar_marcas_de_error()
    reiniciar_resultados()
    editor_codigo.focus_set()

# ------------------ Diagrama: colocar_codigo_en_editor ---------------
#   [texto] -> reemplazar contenido y limpiar paneles/estados
# ---------------------------------------------------------------------
def colocar_codigo_en_editor(texto_del_ejemplo):
    editor_codigo.delete("1.0", "end")
    editor_codigo.insert("1.0", texto_del_ejemplo)
    editor.quitar_marcas_de_error()
    reiniciar_resultados()
    editor_codigo.focus_set()

def reiniciar_resultados():
    limpiar_todos_los_paneles()
    mostrar_ayudas_iniciales()
    marcar_las_tres_fases_pendientes()
    actualizar_titulos_de_pestanas({})
    etiqueta_resumen.config(text="")
    mostrar_mensaje("Listo  ·  Ctrl+Enter para analizar")

def mostrar_ayudas_iniciales():
    for clave, area in [("tokens", area_tokens), ("ast", area_ast), ("simbolos", area_tabla_simbolos),
                        ("errores", area_errores), ("informe", area_informe_final)]:
        escribir(area, AYUDAS[clave], "suave")

# ------------------ Diagrama: cargar_ejemplo_valido ------------------
#   [] -> colocar un programa sin errores
# ---------------------------------------------------------------------
def cargar_ejemplo_valido(): colocar_codigo_en_editor(ejemplos.EJEMPLO_VALIDO)
def cargar_ejemplo_error_lexico(): colocar_codigo_en_editor(ejemplos.EJEMPLO_ERROR_LEXICO)
def cargar_ejemplo_error_sintactico(): colocar_codigo_en_editor(ejemplos.EJEMPLO_ERROR_SINTACTICO)
def cargar_ejemplo_error_semantico(): colocar_codigo_en_editor(ejemplos.EJEMPLO_ERROR_SEMANTICO)
def cargar_ejemplo_precedencia(): colocar_codigo_en_editor(ejemplos.EJEMPLO_PRECEDENCIA)
def cargar_ejemplo_relacionales(): colocar_codigo_en_editor(ejemplos.EJEMPLO_RELACIONAL)
def cargar_ejemplo_no_declarada(): colocar_codigo_en_editor(ejemplos.EJEMPLO_NO_DECLARADA)
def cargar_ejemplo_duplicada(): colocar_codigo_en_editor(ejemplos.EJEMPLO_DUPLICADA)

# ------------------ Diagrama: marcar_fase ----------------------------
#   [etiqueta, texto, color] -> actualizar texto y color de una fase
# ---------------------------------------------------------------------
def marcar_fase(etiqueta, texto, color):
    etiqueta.config(text=texto, fg=color)
    punto, circulo = puntos_de_fase[etiqueta]
    punto.itemconfig(circulo, fill=color)

def marcar_las_tres_fases_pendientes():
    marcar_fase(etiqueta_estado_lexico, "Pendiente", COLOR_GRIS)
    marcar_fase(etiqueta_estado_sintactico, "Pendiente", COLOR_GRIS)
    marcar_fase(etiqueta_estado_semantico, "Pendiente", COLOR_GRIS)

def limpiar_todos_los_paneles():
    for area in (area_tokens, area_ast, area_tabla_simbolos, area_errores, area_informe_final):
        borrar(area)

def actualizar_titulos_de_pestanas(conteos):
    for clave, (marco, titulo) in pestanas.items():
        if clave in conteos:
            cuaderno.tab(marco, text=titulo + "  (" + str(conteos[clave]) + ")")
        else:
            cuaderno.tab(marco, text=titulo)

# ------------------ Diagrama: etiqueta_de_token ----------------------
#   [tipo] -> nombre de la etiqueta de color según la categoría
# ---------------------------------------------------------------------
def etiqueta_de_token(tipo):
    if tipo in ("PALABRA_RESERVADA", "OPERADOR_Y", "OPERADOR_O", "OPERADOR_NO"): return "t_palabra"
    if tipo == "TIPO_DATO": return "t_tipo"
    if tipo == "BOOLEANO_LITERAL": return "t_bool"
    if tipo in ("ENTERO", "DECIMAL"): return "t_numero"
    if tipo == "CADENA": return "t_cadena"
    if tipo == "IDENTIFICADOR": return None
    if tipo == "FIN": return "suave"
    return "t_oper"

def mostrar_tokens_en_panel(tokens):
    lineas = formatear_tokens_a_texto(tokens).splitlines(keepends=True)
    escribir(area_tokens, lineas[0], "encabezado")
    escribir(area_tokens, lineas[1], "separador")
    for token, linea in zip(tokens, lineas[2:]):
        escribir(area_tokens, linea[:18], "suave")
        escribir(area_tokens, linea[18:42], etiqueta_de_token(token[0]))
        escribir(area_tokens, linea[42:])

def mostrar_ast_en_panel(arbol):
    for linea in formatear_arbol_a_texto(arbol, 0).splitlines(keepends=True):
        palabra = linea.strip().split(" ")[0]
        if palabra == "Programa": etiqueta = "a_programa"
        elif palabra in ("Declaracion", "Asignacion", "Mostrar"): etiqueta = "a_instruccion"
        elif palabra in ("Binaria:", "Unaria:"): etiqueta = "a_operacion"
        elif palabra in ("entero:", "decimal:"): etiqueta = "t_numero"
        elif palabra == "cadena:": etiqueta = "t_cadena"
        elif palabra == "booleano:": etiqueta = "t_bool"
        else: etiqueta = None
        escribir(area_ast, linea, etiqueta)

def mostrar_tabla_en_panel(tabla):
    lineas = formatear_tabla_simbolos_a_texto(tabla).splitlines(keepends=True)
    for numero, linea in enumerate(lineas):
        if len(tabla) == 0: etiqueta = "suave"
        elif numero == 0: etiqueta = "encabezado"
        else: etiqueta = None
        escribir(area_tabla_simbolos, linea, etiqueta)

def mostrar_errores_en_panel(errores):
    for error in errores:
        errores_acumulados.append(error)
        texto = formatear_error(error)
        prefijo = "[" + error[0] + "]"
        escribir(area_errores, prefijo, error[0].lower())
        escribir(area_errores, texto[len(prefijo):])

# ------------------ Diagrama: ejecutar_fase_lexica -------------------
#   [codigo] -> analizar_lexico -> mostrar tokens -> marcar estado
# ---------------------------------------------------------------------
def ejecutar_fase_lexica(codigo):
    tokens, errores = analizar_lexico(codigo)
    mostrar_tokens_en_panel(tokens)
    mostrar_errores_en_panel(errores)
    if len(errores) > 0:
        marcar_fase(etiqueta_estado_lexico, "Con errores", COLOR_ROJO)
        marcar_fase(etiqueta_estado_sintactico, "No ejecutada", COLOR_GRIS)
        marcar_fase(etiqueta_estado_semantico, "No ejecutada", COLOR_GRIS)
    else:
        marcar_fase(etiqueta_estado_lexico, "Correcta", COLOR_VERDE)
    return tokens, errores

def ejecutar_fase_sintactica(tokens):
    arbol, errores = analizar_sintactico(tokens)
    mostrar_ast_en_panel(arbol)
    mostrar_errores_en_panel(errores)
    if len(errores) > 0:
        marcar_fase(etiqueta_estado_sintactico, "Con errores", COLOR_ROJO)
        marcar_fase(etiqueta_estado_semantico, "No ejecutada", COLOR_GRIS)
    else:
        marcar_fase(etiqueta_estado_sintactico, "Correcta", COLOR_VERDE)
    return arbol, errores

def ejecutar_fase_semantica(arbol):
    tabla, errores = analizar_semantico(arbol)
    mostrar_tabla_en_panel(tabla)
    mostrar_errores_en_panel(errores)
    if len(errores) > 0:
        marcar_fase(etiqueta_estado_semantico, "Con errores", COLOR_ROJO)
    else:
        marcar_fase(etiqueta_estado_semantico, "Correcta", COLOR_VERDE)
    return tabla, errores

# ------------------ Diagrama: escribir_informe_lexico ----------------
#   [informe, errores] -> escribir mensaje de detención léxica
# ---------------------------------------------------------------------
def escribir_informe_lexico(informe, errores):
    escribir(informe, "Estado: DETENIDO EN ANALISIS LEXICO\n", "error")
    escribir(informe, "Se encontraron " + str(len(errores)) + " errores lexicos.\n")
    escribir(informe, "No se ejecutaron las fases sintactica ni semantica.\n", "suave")

def escribir_informe_sintactico(informe, errores):
    escribir(informe, "Estado: DETENIDO EN ANALISIS SINTACTICO\n", "error")
    escribir(informe, "Analisis lexico: correcto\n", "ok")
    escribir(informe, "Se encontraron " + str(len(errores)) + " errores sintacticos.\n")
    escribir(informe, "No se ejecuto el analisis semantico.\n", "suave")

def escribir_informe_completo(informe, tokens, tabla, errores_semanticos):
    if len(errores_semanticos) > 0:
        escribir(informe, "Estado: ANALISIS COMPLETO CON ERRORES SEMANTICOS\n", "aviso")
    else:
        escribir(informe, "Estado: ANALISIS COMPLETO SIN ERRORES\n", "ok")
    escribir(informe, "Analisis lexico: correcto (" + str(len(tokens)) + " tokens)\n", "ok")
    escribir(informe, "Analisis sintactico: correcto\n", "ok")
    if len(errores_semanticos) > 0:
        escribir(informe, "Analisis semantico: " + str(len(errores_semanticos)) + " errores encontrados.\n", "error")
        escribir(informe, "\nObservacion: el codigo es lexica y sintacticamente valido, pero tiene errores de significado. Por eso existen tres fases separadas.\n", "suave")
    else:
        escribir(informe, "Analisis semantico: correcto (" + str(len(tabla)) + " variables declaradas)\n", "ok")

def mostrar_informe_final(estado, tokens, errores_lexicos, arbol, errores_sintacticos, tabla, errores_semanticos):
    informe = area_informe_final
    escribir(informe, "=== INFORME FINAL ===\n\n", "titulo")
    if estado == "lexico":
        escribir_informe_lexico(informe, errores_lexicos)
        return
    if estado == "sintactico":
        escribir_informe_sintactico(informe, errores_sintacticos)
        return
    escribir_informe_completo(informe, tokens, tabla, errores_semanticos)

def mostrar_mensaje_final(estado, total_errores):
    if estado == "lexico":
        mostrar_mensaje("Detenido en el análisis léxico  ·  " + str(total_errores) + " error(es)", tema.COLOR_ROJO)
    elif estado == "sintactico":
        mostrar_mensaje("Detenido en el análisis sintáctico  ·  " + str(total_errores) + " error(es)", tema.COLOR_ROJO)
    elif total_errores > 0:
        mostrar_mensaje("Análisis completo con errores semánticos  ·  " + str(total_errores) + " error(es)", tema.COLOR_ROJO)
    else:
        mostrar_mensaje("Análisis completo sin errores", tema.COLOR_VERDE)

def terminar_analisis(estado, tokens, tabla):
    total_errores = len(errores_acumulados)
    if total_errores == 0:
        escribir(area_errores, "No se encontraron errores.\n", "ok")
    for area in (area_ast, area_tabla_simbolos):
        if esta_vacia(area):
            escribir(area, "Esta fase no se ejecutó porque una fase anterior tuvo errores.\n", "suave")
    editor.marcar_errores_en_editor(errores_acumulados)
    
    conteos = {"tokens": len(tokens)}
    if tabla is not None: conteos["simbolos"] = len(tabla)
    if total_errores > 0: conteos["errores"] = total_errores
    actualizar_titulos_de_pestanas(conteos)
    
    etiqueta_resumen.config(text=str(len(tokens)) + " tokens  ·  " + str(total_errores) + (" error" if total_errores == 1 else " errores"))
    mostrar_mensaje_final(estado, total_errores)
    if total_errores > 0:
        cuaderno.select(pestanas["errores"][0])

# ------------------ Diagrama: analizar_codigo ------------------------
#   [] -> leer editor -> ejecutar fases en orden -> informe final
# ---------------------------------------------------------------------
def analizar_codigo():
    limpiar_todos_los_paneles()
    errores_acumulados.clear()
    editor.quitar_marcas_de_error()
    codigo = editor_codigo.get("1.0", "end-1c")
    if codigo.strip() == "":
        marcar_las_tres_fases_pendientes()
        escribir(area_informe_final, "El editor esta vacio.\n", "aviso")
        actualizar_titulos_de_pestanas({})
        etiqueta_resumen.config(text="")
        mostrar_mensaje("El editor está vacío", tema.COLOR_SINTACTICO)
        cuaderno.select(pestanas["informe"][0])
        return
        
    estado = "completo"
    tokens, errores_lexicos = ejecutar_fase_lexica(codigo)
    arbol = tabla = errores_sintacticos = errores_semanticos = None
    if len(errores_lexicos) > 0:
        estado = "lexico"
    else:
        arbol, errores_sintacticos = ejecutar_fase_sintactica(tokens)
        if len(errores_sintacticos) > 0:
            estado = "sintactico"
        else:
            tabla, errores_semanticos = ejecutar_fase_semantica(arbol)
            
    mostrar_informe_final(estado, tokens, errores_lexicos, arbol, errores_sintacticos, tabla, errores_semanticos)
    terminar_analisis(estado, tokens, tabla)

# ------------------ Diagrama: crear_ventana_principal ----------------
#   [] -> Tk() con título, tamaño y todas las secciones
# ---------------------------------------------------------------------
def crear_ventana_principal():
    global ventana_principal
    tema.habilitar_nitidez_en_windows()
    ventana_principal = tk.Tk()
    ventana_principal.title("Compilador Educativo - LenguajeEducativo")
    tema.aplicar_estilos(ventana_principal)
    ancho = min(1320, ventana_principal.winfo_screenwidth() - 80)
    alto = min(820, ventana_principal.winfo_screenheight() - 100)
    x = (ventana_principal.winfo_screenwidth() - ancho) // 2
    y = max((ventana_principal.winfo_screenheight() - alto) // 3, 0)
    ventana_principal.geometry(str(ancho) + "x" + str(alto) + "+" + str(x) + "+" + str(y))
    ventana_principal.minsize(980, 620)
    
    crear_encabezado(ventana_principal)
    crear_seccion_estado_fases(ventana_principal)
    crear_barra_estado(ventana_principal)
    
    cuerpo = tk.PanedWindow(ventana_principal, orient="horizontal", sashwidth=10,
                            bg=tema.FONDO, bd=0, sashrelief="flat", opaqueresize=True)
    cuerpo.pack(fill="both", expand=True, padx=20, pady=(0, 14))
    cuerpo.add(crear_seccion_editor(cuerpo), minsize=380, stretch="always", width=int(ancho * 0.44))
    cuerpo.add(crear_seccion_pestanas(cuerpo), minsize=420, stretch="always")
    
    ventana_principal.bind("<F5>", lambda evento: analizar_codigo())
    reiniciar_resultados()
    colocar_codigo_en_editor(ejemplos.EJEMPLO_VALIDO)
    editor_codigo.focus_set()

def iniciar_aplicacion():
    crear_ventana_principal()
    ventana_principal.mainloop()

if __name__ == "__main__":
    iniciar_aplicacion()