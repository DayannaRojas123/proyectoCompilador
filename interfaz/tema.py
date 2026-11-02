# tema.py
# =====================================================================
# Apariencia de la interfaz: paleta de colores, tipografías y estilos ttk.
# Cambiar un color aquí lo cambia en toda la aplicación.
# =====================================================================

import sys
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont

# ------------------ Paleta (tema oscuro) -----------------------------
FONDO = "#0d1117"            # fondo de la ventana
PANEL = "#161b22"            # tarjetas y paneles
PANEL_ALT = "#1c2330"        # pestañas activas, superficies elevadas
EDITOR_FONDO = "#0b0f14"     # fondo del editor y de los resultados
BORDE = "#2b3342"            # líneas y bordes
TEXTO = "#e6edf3"            # texto principal
TEXTO_SUAVE = "#8b98a9"      # texto secundario
ACENTO = "#6366f1"           # botón principal (índigo)
ACENTO_HOVER = "#7a7df7"
ACENTO_PRESIONADO = "#4f52d9"
BOTON = "#222b3a"            # botones secundarios
BOTON_HOVER = "#2d3748"

# Estados de las fases del compilador.
COLOR_VERDE = "#3fb950"      # análisis correcto
COLOR_ROJO = "#f85149"       # errores encontrados
COLOR_GRIS = "#6e7a8a"       # no ejecutada o pendiente
FONDO_ERROR = "#3a1a20"      # línea del editor con error
LINEA_ACTUAL = "#131a24"     # línea donde está el cursor

# Colores por tipo de error y de elemento (resultados y resaltado).
COLOR_LEXICO = "#ff7b72"
COLOR_SINTACTICO = "#ffa657"
COLOR_SEMANTICO = "#d2a8ff"
COLOR_PALABRA = "#ff7b72"    # var, mostrar, y, o, no
COLOR_TIPO = "#79c0ff"       # entero, decimal, cadena, booleano
COLOR_BOOLEANO = "#d2a8ff"   # verdadero, falso
COLOR_CADENA = "#7ee787"
COLOR_NUMERO = "#f2cc60"
COLOR_COMENTARIO = "#6e7a8a"

# ------------------ Tipografías --------------------------------------
# Se usa la primera fuente instalada de cada lista de candidatas.
FUENTES_UI = ["Segoe UI", "Inter", "SF Pro Text", "Helvetica Neue", "Ubuntu", "DejaVu Sans", "Arial"]
FUENTES_CODIGO = ["Cascadia Code", "JetBrains Mono", "Consolas", "SF Mono", "Menlo", "DejaVu Sans Mono", "Courier New"]

FUENTE_UI = "TkDefaultFont"       # se reemplazan en preparar_fuentes()
FUENTE_CODIGO = "TkFixedFont"


# ------------------ Diagrama: elegir_fuente --------------------------
#   [candidatas, defecto] -> primera fuente instalada, o la de respaldo
# ---------------------------------------------------------------------
def elegir_fuente(candidatas, defecto):
    instaladas = set(tkfont.families())                    # fuentes del sistema
    for nombre in candidatas:                              # en orden de preferencia
        if nombre in instaladas:                           # ¿está instalada?
            return nombre                                  # usarla
    return defecto                                         # respaldo de Tk


def preparar_fuentes():
    global FUENTE_UI, FUENTE_CODIGO
    FUENTE_UI = elegir_fuente(FUENTES_UI, "TkDefaultFont")
    FUENTE_CODIGO = elegir_fuente(FUENTES_CODIGO, "TkFixedFont")


def fuente_ui(tamano=10, estilo=""):
    return (FUENTE_UI, tamano, estilo) if estilo else (FUENTE_UI, tamano)


def fuente_codigo(tamano=11, estilo=""):
    return (FUENTE_CODIGO, tamano, estilo) if estilo else (FUENTE_CODIGO, tamano)


# ------------------ Diagrama: habilitar_nitidez_en_windows -----------
#   [] -> en Windows pide nitidez en pantallas de alta densidad (DPI)
# ---------------------------------------------------------------------
def habilitar_nitidez_en_windows():
    if sys.platform != "win32":                            # solo aplica a Windows
        return
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)     # texto sin borrosidad
    except Exception:
        pass                                               # si falla, se sigue sin ello


# ------------------ Diagrama: aplicar_estilos ------------------------
#   [raiz] -> tema base 'clam' + estilos para botones, pestañas y barras
# ---------------------------------------------------------------------
def aplicar_estilos(raiz):
    preparar_fuentes()
    raiz.configure(bg=FONDO)
    estilo = ttk.Style(raiz)
    estilo.theme_use("clam")                               # base que sí permite colorear
    estilo.configure(".", background=FONDO, foreground=TEXTO, font=fuente_ui(10),
                     borderwidth=0, focuscolor=FONDO)

    # Botones: principal (acento), secundario y "chip" de ejemplos.
    plano = dict(borderwidth=0, relief="flat", focusthickness=0,
                 lightcolor=PANEL, darkcolor=PANEL, bordercolor=PANEL)
    estilo.configure("Accent.TButton", background=ACENTO, foreground="#ffffff",
                     padding=(20, 9), font=fuente_ui(10, "bold"), **plano)
    estilo.map("Accent.TButton",
               background=[("pressed", ACENTO_PRESIONADO), ("active", ACENTO_HOVER)],
               lightcolor=[("pressed", ACENTO_PRESIONADO), ("active", ACENTO_HOVER)],
               darkcolor=[("pressed", ACENTO_PRESIONADO), ("active", ACENTO_HOVER)],
               bordercolor=[("pressed", ACENTO_PRESIONADO), ("active", ACENTO_HOVER)])
    estilo.configure("Secondary.TButton", background=BOTON, foreground=TEXTO,
                     padding=(16, 9), font=fuente_ui(10), **plano)
    estilo.configure("Chip.TButton", background=BOTON, foreground=TEXTO_SUAVE,
                     padding=(11, 5), font=fuente_ui(9), **plano)
    for nombre in ("Secondary.TButton", "Chip.TButton"):
        estilo.map(nombre,
                   background=[("pressed", BORDE), ("active", BOTON_HOVER)],
                   foreground=[("active", TEXTO)],
                   lightcolor=[("pressed", BORDE), ("active", BOTON_HOVER)],
                   darkcolor=[("pressed", BORDE), ("active", BOTON_HOVER)],
                   bordercolor=[("pressed", BORDE), ("active", BOTON_HOVER)])

    # Pestañas de resultados.
    estilo.configure("TNotebook", background=PANEL, borderwidth=0, tabmargins=(8, 8, 8, 0),
                     bordercolor=PANEL, lightcolor=PANEL, darkcolor=PANEL)
    estilo.configure("TNotebook.Tab", background=PANEL, foreground=TEXTO_SUAVE,
                     padding=(14, 8), borderwidth=0, font=fuente_ui(10),
                     lightcolor=PANEL, bordercolor=PANEL)
    estilo.map("TNotebook.Tab",
               background=[("selected", PANEL_ALT), ("active", PANEL_ALT)],
               foreground=[("selected", TEXTO), ("active", TEXTO)],
               lightcolor=[("selected", ACENTO)], bordercolor=[("selected", PANEL_ALT)])
    estilo.layout("TNotebook.Tab", [("Notebook.tab", {"sticky": "nswe", "children": [
        ("Notebook.padding", {"side": "top", "sticky": "nswe", "children": [
            ("Notebook.label", {"side": "top", "sticky": ""})]})]})])

    # Barras de desplazamiento discretas.
    for orientacion in ("Vertical", "Horizontal"):
        estilo.configure(orientacion + ".TScrollbar", background=BORDE, troughcolor=EDITOR_FONDO,
                         bordercolor=EDITOR_FONDO, lightcolor=BORDE, darkcolor=BORDE,
                         arrowcolor=TEXTO_SUAVE, relief="flat", arrowsize=12, gripcount=0)
        estilo.map(orientacion + ".TScrollbar", background=[("active", "#425068"), ("pressed", "#52617c")])
