# principal.py
# =====================================================================
# Punto de entrada del compilador educativo.
# Solo importa la función que crea y mantiene la ventana, y la invoca.
#
# ---------------------------------------------------------------------
# EJEMPLO TRAZADO
# ---------------------------------------------------------------------
# Entrada (terminal): python principal.py
# Salida: se abre la ventana "Compilador Educativo - LenguajeEducativo"
# Cerrar: botón X de la ventana o Ctrl+C en la terminal
# ---------------------------------------------------------------------

from interfaz_grafica import iniciar_aplicacion     # única dependencia: la interfaz

if __name__ == "__main__":
    iniciar_aplicacion()                            # arranca el bucle de eventos