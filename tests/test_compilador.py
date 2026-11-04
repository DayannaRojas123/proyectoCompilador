# test_compilador.py
# =====================================================================
# Pruebas automáticas del compilador y de la interfaz.
# Ejecutar desde la carpeta del proyecto: python -m unittest -v
# =====================================================================
import unittest
from compilador.analizador_lexico import analizar_lexico
from compilador.analizador_sintactico import analizar_sintactico, formatear_arbol_a_texto
from compilador.analizador_semantico import analizar_semantico, formatear_tabla_simbolos_a_texto
from interfaz import ejemplos
from interfaz.formato import formatear_tokens_a_texto, formatear_error

def compilar(codigo):
    tokens, errores = analizar_lexico(codigo)
    if errores: return "lexico", errores
    arbol, errores = analizar_sintactico(tokens)
    if errores: return "sintactico", errores
    tabla, errores = analizar_semantico(arbol)
    return ("semantico" if errores else "ok"), errores

def test_tokens_del_ejemplo_valido():
    tokens, errores = analizar_lexico(ejemplos.EJEMPLO_VALIDO)
    assert errores == []
    assert len(tokens) == 15
    assert tokens[0][:2] == ["PALABRA_RESERVADA", "var"]
    assert tokens[-1][0] == "FIN"

def test_caracter_no_permitido():
    _, errores = analizar_lexico("var x : entero = 5 @ 3;")
    assert errores[0][:2] == ["LEXICO", "Caracter no permitido: @"]

def test_precedencia_multiplicacion_sobre_suma():
    tokens, _ = analizar_lexico("var x : entero = 2 + 3 * 4;")
    arbol, errores = analizar_sintactico(tokens)
    assert errores == []
    texto = formatear_arbol_a_texto(arbol, 0)
    assert texto.index("Binaria: +") < texto.index("Binaria: *")

def test_falta_punto_y_coma():
    tokens, _ = analizar_lexico("var x : entero = 5")
    _, errores = analizar_sintactico(tokens)
    assert len(errores) > 0

def test_tabla_de_simbolos():
    tokens, _ = analizar_lexico(ejemplos.EJEMPLO_VALIDO)
    arbol, _ = analizar_sintactico(tokens)
    tabla, errores = analizar_semantico(arbol)
    assert errores == []
    assert tabla == [["edad", "entero", 1, 5]]
    assert "edad" in formatear_tabla_simbolos_a_texto(tabla)

def test_cada_ejemplo_falla_en_su_fase():
    esperado = {
        ejemplos.EJEMPLO_VALIDO: "ok",
        ejemplos.EJEMPLO_ERROR_LEXICO: "lexico",
        ejemplos.EJEMPLO_ERROR_SINTACTICO: "sintactico",
        ejemplos.EJEMPLO_ERROR_SEMANTICO: "semantico",
        ejemplos.EJEMPLO_PRECEDENCIA: "ok",
        ejemplos.EJEMPLO_RELACIONAL: "sintactico",
        ejemplos.EJEMPLO_NO_DECLARADA: "semantico",
        ejemplos.EJEMPLO_DUPLICADA: "semantico",
    }
    for codigo, fase in esperado.items():
        assert compilar(codigo)[0] == fase

def test_formato_de_tokens_y_errores():
    tokens, _ = analizar_lexico("var x : entero = 1;")
    assert formatear_tokens_a_texto(tokens).count("\n") == len(tokens) + 2
    assert formatear_error(["LEXICO", "msg", 2, 3]) == "[LEXICO] msg (linea 2, columna 3)\n"

def hay_pantalla():
    try:
        import tkinter
        raiz = tkinter.Tk()
        raiz.destroy()
        return True
    except Exception:
        return False

def buscar_boton(texto, raiz):
    for hijo in raiz.winfo_children():
        if hijo.winfo_class() == "TButton" and hijo.cget("text") == texto:
            return hijo
        encontrado = buscar_boton(texto, hijo)
        if encontrado: return encontrado
    return None

def test_botones_ejecutan_las_fases_reales():
    if not hay_pantalla(): return
    from interfaz import ventana
    ventana.crear_ventana_principal()
    ventana.ventana_principal.update()
    v = ventana

    def fases():
        return [e.cget("text") for e in (v.etiqueta_estado_lexico, v.etiqueta_estado_sintactico, v.etiqueta_estado_semantico)]

    casos = [
        ("Válido", ["Correcta"] * 3),
        ("Error léxico", ["Con errores", "No ejecutada", "No ejecutada"]),
        ("Error sintáctico", ["Correcta", "Con errores", "No ejecutada"]),
        ("Error semántico", ["Correcta", "Correcta", "Con errores"]),
        ("Precedencia", ["Correcta"] * 3),
        ("Relacionales", ["Correcta", "Con errores", "No ejecutada"]),
        ("No declarada", ["Correcta", "Correcta", "Con errores"]),
        ("Duplicada", ["Correcta", "Correcta", "Con errores"]),
    ]
    for texto, fases_esperadas in casos:
        boton = buscar_boton(texto, v.ventana_principal)
        if boton:
            boton.invoke()
            assert fases() == ["Pendiente"] * 3
            buscar_boton("Analizar", v.ventana_principal).invoke()
            assert fases() == fases_esperadas
    v.ventana_principal.destroy()

def test_limpiar_y_editor_vacio():
    if not hay_pantalla(): return
    from interfaz import ventana
    ventana.crear_ventana_principal()
    ventana.ventana_principal.update()
    v = ventana
    buscar_boton("Limpiar", v.ventana_principal).invoke()
    assert v.editor_codigo.get("1.0", "end-1c") == ""
    buscar_boton("Analizar", v.ventana_principal).invoke()
    assert "vacio" in v.area_informe_final.get("1.0", "end")
    v.ventana_principal.destroy()

def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    suite.addTest(unittest.FunctionTestCase(test_tokens_del_ejemplo_valido))
    suite.addTest(unittest.FunctionTestCase(test_caracter_no_permitido))
    suite.addTest(unittest.FunctionTestCase(test_precedencia_multiplicacion_sobre_suma))
    suite.addTest(unittest.FunctionTestCase(test_falta_punto_y_coma))
    suite.addTest(unittest.FunctionTestCase(test_tabla_de_simbolos))
    suite.addTest(unittest.FunctionTestCase(test_cada_ejemplo_falla_en_su_fase))
    suite.addTest(unittest.FunctionTestCase(test_formato_de_tokens_y_errores))
    suite.addTest(unittest.FunctionTestCase(test_botones_ejecutan_las_fases_reales))
    suite.addTest(unittest.FunctionTestCase(test_limpiar_y_editor_vacio))
    return suite

if __name__ == "__main__":
    unittest.main()