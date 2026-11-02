# editor.py
# =====================================================================
# Editor de código fuente: Text con números de línea, resaltado de
# sintaxis, línea actual destacada y marcas de error.
# Solo se ocupa del aspecto del editor; no ejecuta el compilador.
# =====================================================================

import re
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont

from compilador.lenguaje import (
    PALABRAS_RESERVADAS_SIMPLES, TIPOS_DATOS, LITERALES_BOOLEANOS, OPERADORES_DE_PALABRA
)
from . import tema

# Estado del editor (un solo editor por ventana).
texto_editor = None            # widget Text
lienzo_numeros = None          # Canvas con los números de línea
lineas_con_error = set()       # líneas marcadas en rojo
_refresco_pendiente = None     # id de after() para agrupar refrescos
_al_mover_cursor = None        # función opcional: se llama con (linea, columna)

# Un solo patrón: comentarios y cadenas primero para que ganen a lo demás.
PATRON_SINTAXIS = re.compile(
    r'(?P<comentario>//[^\n]*)'
    r'|(?P<cadena>"[^"\n]*"?)'
    r'|(?P<numero>\b\d+(?:\.\d+)?\b)'
    r'|(?P<palabra>[A-Za-z_]\w*)'
)


# ------------------ Diagrama: crear_editor ---------------------------
#   [padre] -> Frame con [números | Text | scroll] y devuelve el Text
# ---------------------------------------------------------------------
def crear_editor(padre, al_mover_cursor=None):
    global texto_editor, lienzo_numeros, _al_mover_cursor
    _al_mover_cursor = al_mover_cursor
    marco = tk.Frame(padre, bg=tema.EDITOR_FONDO)                                       # contenedor
    marco.pack(fill="both", expand=True)
    barra_v = ttk.Scrollbar(marco, orient="vertical")                                   # scroll vertical
    barra_h = ttk.Scrollbar(marco, orient="horizontal")                                 # scroll horizontal
    barra_v.pack(side="right", fill="y")
    barra_h.pack(side="bottom", fill="x")
    lienzo_numeros = tk.Canvas(marco, width=48, bg=tema.EDITOR_FONDO,                   # columna de números
                               highlightthickness=0, bd=0)
    lienzo_numeros.pack(side="left", fill="y")
    texto_editor = tk.Text(marco, wrap="none", undo=True, font=tema.fuente_codigo(12),  # editor real
                           bg=tema.EDITOR_FONDO, fg=tema.TEXTO, insertbackground=tema.TEXTO,
                           selectbackground="#264f78", selectforeground="#ffffff",
                           relief="flat", bd=0, highlightthickness=0,
                           padx=10, pady=8, spacing1=2, spacing3=2, tabs=("1c",),
                           yscrollcommand=lambda a, b: _al_desplazar(barra_v, a, b),
                           xscrollcommand=barra_h.set)
    texto_editor.pack(side="left", fill="both", expand=True)
    barra_v.config(command=texto_editor.yview)
    barra_h.config(command=texto_editor.xview)
    _crear_etiquetas()
    texto_editor.bind("<<Modified>>", _al_modificar)                                    # cualquier cambio
    texto_editor.bind("<KeyRelease>", lambda e: _actualizar_cursor())                   # mover con teclado
    texto_editor.bind("<ButtonRelease-1>", lambda e: _actualizar_cursor())              # mover con ratón
    texto_editor.bind("<Configure>", lambda e: _programar_refresco())                   # cambio de tamaño
    lienzo_numeros.bind("<MouseWheel>", lambda e: texto_editor.event_generate("<MouseWheel>", delta=e.delta))
    refrescar_editor()
    return texto_editor


def _crear_etiquetas():
    t = texto_editor
    t.tag_configure("linea_actual", background=tema.LINEA_ACTUAL)
    t.tag_configure("error_linea", background=tema.FONDO_ERROR)
    t.tag_configure("comentario", foreground=tema.COLOR_COMENTARIO, font=tema.fuente_codigo(12, "italic"))
    t.tag_configure("cadena", foreground=tema.COLOR_CADENA)
    t.tag_configure("numero", foreground=tema.COLOR_NUMERO)
    t.tag_configure("palabra_clave", foreground=tema.COLOR_PALABRA)
    t.tag_configure("tipo", foreground=tema.COLOR_TIPO)
    t.tag_configure("booleano", foreground=tema.COLOR_BOOLEANO)
    t.tag_raise("sel")                                                                  # la selección siempre se ve


# ------------------ Diagrama: resaltar_sintaxis ----------------------
#   [] -> recorrer el texto con PATRON_SINTAXIS y etiquetar cada pieza
# ---------------------------------------------------------------------
def resaltar_sintaxis():
    t = texto_editor
    for etiqueta in ("comentario", "cadena", "numero", "palabra_clave", "tipo", "booleano"):
        t.tag_remove(etiqueta, "1.0", "end")                                            # limpiar lo anterior
    codigo = t.get("1.0", "end-1c")
    for coincidencia in PATRON_SINTAXIS.finditer(codigo):
        grupo = coincidencia.lastgroup
        if grupo == "palabra":                                                          # clasificar la palabra
            palabra = coincidencia.group()
            if palabra in PALABRAS_RESERVADAS_SIMPLES or palabra in OPERADORES_DE_PALABRA:
                grupo = "palabra_clave"
            elif palabra in TIPOS_DATOS:
                grupo = "tipo"
            elif palabra in LITERALES_BOOLEANOS:
                grupo = "booleano"
            else:
                continue                                                                # identificador normal
        inicio = "1.0+%dc" % coincidencia.start()
        fin = "1.0+%dc" % coincidencia.end()
        t.tag_add(grupo, inicio, fin)


# ------------------ Diagrama: marcar_errores_en_editor ---------------
#   [errores] -> pintar de rojo las líneas con error (y su número)
# ---------------------------------------------------------------------
def marcar_errores_en_editor(errores):
    quitar_marcas_de_error()
    for error in errores:
        linea = int(error[2])
        lineas_con_error.add(linea)
        texto_editor.tag_add("error_linea", "%d.0" % linea, "%d.0 lineend+1c" % linea)
    _dibujar_numeros()


def quitar_marcas_de_error():
    lineas_con_error.clear()
    texto_editor.tag_remove("error_linea", "1.0", "end")
    _dibujar_numeros()


# ------------------ Refresco (números, resaltado, línea actual) ------
def refrescar_editor():
    resaltar_sintaxis()
    _actualizar_cursor()
    _dibujar_numeros()


def _programar_refresco():
    global _refresco_pendiente
    if _refresco_pendiente is None:                                                     # agrupa varios eventos en uno
        _refresco_pendiente = texto_editor.after_idle(_ejecutar_refresco)


def _ejecutar_refresco():
    global _refresco_pendiente
    _refresco_pendiente = None
    refrescar_editor()


def _al_modificar(evento):
    if texto_editor.edit_modified():
        texto_editor.edit_modified(False)                                               # rearmar el aviso
        _programar_refresco()


def _al_desplazar(barra, primero, ultimo):
    barra.set(primero, ultimo)                                                          # mover la barra
    _dibujar_numeros()                                                                  # y los números


def _actualizar_cursor():
    t = texto_editor
    t.tag_remove("linea_actual", "1.0", "end")
    linea, columna = t.index("insert").split(".")
    t.tag_add("linea_actual", "%s.0" % linea, "%s.0 lineend+1c" % linea)
    if _al_mover_cursor is not None:
        _al_mover_cursor(int(linea), int(columna) + 1)                                  # columnas desde 1 (como el compilador)


def _dibujar_numeros():
    lienzo = lienzo_numeros
    t = texto_editor
    if lienzo is None or t is None:
        return
    lienzo.delete("all")
    total = int(t.index("end-1c").split(".")[0])
    fuente = tkfont.Font(font=tema.fuente_codigo(11))
    ancho = fuente.measure("0") * max(3, len(str(total))) + 22                          # crece con los dígitos
    lienzo.config(width=ancho)
    indice = t.index("@0,0")
    for _ in range(500):                                                                # tope de seguridad
        info = t.dlineinfo(indice)
        if info is None:
            break
        numero = int(indice.split(".")[0])
        if numero in lineas_con_error:
            color, fuente_numero = tema.COLOR_ROJO, tema.fuente_codigo(11, "bold")
        else:
            color, fuente_numero = tema.TEXTO_SUAVE, tema.fuente_codigo(11)
        lienzo.create_text(ancho - 10, info[1] + info[3] / 2, anchor="e", text=str(numero),
                           font=fuente_numero, fill=color)
        siguiente = t.index("%s+1line" % indice)
        if siguiente == indice or int(siguiente.split(".")[0]) > total:
            break
        indice = siguiente
