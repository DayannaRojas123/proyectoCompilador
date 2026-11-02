# compilador/__init__.py
# =====================================================================
# Paquete con las tres fases del compilador y las definiciones del lenguaje.
# No depende de la interfaz gráfica: se puede usar por separado.
#
#     from compilador.analizador_lexico import analizar_lexico
#     from compilador.analizador_sintactico import analizar_sintactico
#     from compilador.analizador_semantico import analizar_semantico
#
# Cada módulo también se puede ejecutar solo para ver una demostración:
#     python -m compilador.lenguaje
#     python -m compilador.analizador_lexico
#     python -m compilador.analizador_sintactico
#     python -m compilador.analizador_semantico
# =====================================================================
