# test_compilador.py
# =====================================================================
# Pruebas automáticas del compilador y de la interfaz.
# Ejecutar desde la carpeta del proyecto:   python -m unittest -v
# =====================================================================

import unittest

from compilador.analizador_lexico import analizar_lexico
from compilador.analizador_sintactico import analizar_sintactico, formatear_arbol_a_texto
from compilador.analizador_semantico import analizar_semantico, formatear_tabla_simbolos_a_texto
from interfaz import ejemplos
from interfaz.formato import formatear_tokens_a_texto, formatear_error


def compilar(codigo):
    """Ejecuta las tres fases y devuelve en qué fase falló (o 'ok')."""
    tokens, errores = analizar_lexico(codigo)
    if errores:
        return "lexico", errores
    arbol, errores = analizar_sintactico(tokens)
    if errores:
        return "sintactico", errores
    tabla, errores = analizar_semantico(arbol)
    return ("semantico" if errores else "ok"), errores


class PruebasLexico(unittest.TestCase):
    def test_tokens_del_ejemplo_valido(self):
        tokens, errores = analizar_lexico(ejemplos.EJEMPLO_VALIDO)
        self.assertEqual(errores, [])
        self.assertEqual(len(tokens), 15)
        self.assertEqual(tokens[0][:2], ["PALABRA_RESERVADA", "var"])
        self.assertEqual(tokens[-1][0], "FIN")

    def test_caracter_no_permitido(self):
        _, errores = analizar_lexico("var x : entero = 5 @ 3;")
        self.assertEqual(errores[0][:2], ["LEXICO", "Caracter no permitido: @"])


class PruebasSintactico(unittest.TestCase):
    def test_precedencia_multiplicacion_sobre_suma(self):
        tokens, _ = analizar_lexico("var x : entero = 2 + 3 * 4;")
        arbol, errores = analizar_sintactico(tokens)
        self.assertEqual(errores, [])
        texto = formatear_arbol_a_texto(arbol, 0)
        self.assertLess(texto.index("Binaria: +"), texto.index("Binaria: *"))

    def test_falta_punto_y_coma(self):
        tokens, _ = analizar_lexico("var x : entero = 5")
        _, errores = analizar_sintactico(tokens)
        self.assertTrue(errores)


class PruebasSemantico(unittest.TestCase):
    def test_tabla_de_simbolos(self):
        tokens, _ = analizar_lexico(ejemplos.EJEMPLO_VALIDO)
        arbol, _ = analizar_sintactico(tokens)
        tabla, errores = analizar_semantico(arbol)
        self.assertEqual(errores, [])
        self.assertEqual(tabla, [["edad", "entero", 1, 5]])
        self.assertIn("edad", formatear_tabla_simbolos_a_texto(tabla))


class PruebasEjemplos(unittest.TestCase):
    """Cada botón de ejemplo debe demostrar justo lo que dice su nombre."""

    def test_cada_ejemplo_falla_en_su_fase(self):
        esperado = {
            ejemplos.EJEMPLO_VALIDO: "ok",
            ejemplos.EJEMPLO_ERROR_LEXICO: "lexico",
            ejemplos.EJEMPLO_ERROR_SINTACTICO: "sintactico",
            ejemplos.EJEMPLO_ERROR_SEMANTICO: "semantico",
            ejemplos.EJEMPLO_PRECEDENCIA: "ok",
        }
        for codigo, fase in esperado.items():
            with self.subTest(codigo=codigo):
                self.assertEqual(compilar(codigo)[0], fase)


class PruebasFormato(unittest.TestCase):
    def test_formato_de_tokens_y_errores(self):
        tokens, _ = analizar_lexico("var x : entero = 1;")
        self.assertEqual(formatear_tokens_a_texto(tokens).count("\n"), len(tokens) + 2)
        self.assertEqual(formatear_error(["LEXICO", "msg", 2, 3]), "[LEXICO] msg (linea 2, columna 3)\n")


def _hay_pantalla():
    try:
        import tkinter
        raiz = tkinter.Tk()
        raiz.destroy()
        return True
    except Exception:
        return False


@unittest.skipUnless(_hay_pantalla(), "No hay Tkinter o pantalla disponible")
class PruebasInterfaz(unittest.TestCase):
    """Pulsa los botones reales de la ventana y revisa los resultados."""

    @classmethod
    def setUpClass(cls):
        from interfaz import ventana
        cls.v = ventana
        ventana.crear_ventana_principal()
        ventana.ventana_principal.update()

    @classmethod
    def tearDownClass(cls):
        cls.v.ventana_principal.destroy()

    def boton(self, texto, raiz=None):
        raiz = raiz or self.v.ventana_principal
        for hijo in raiz.winfo_children():
            if hijo.winfo_class() == "TButton" and hijo.cget("text") == texto:
                return hijo
            encontrado = self.boton(texto, hijo)
            if encontrado:
                return encontrado

    def fases(self):
        v = self.v
        return [e.cget("text") for e in (v.etiqueta_estado_lexico, v.etiqueta_estado_sintactico, v.etiqueta_estado_semantico)]

    def test_botones_ejecutan_las_fases_reales(self):
        casos = [("Válido", ["Correcta"] * 3),
                 ("Error léxico", ["Con errores", "No ejecutada", "No ejecutada"]),
                 ("Error sintáctico", ["Correcta", "Con errores", "No ejecutada"]),
                 ("Error semántico", ["Correcta", "Correcta", "Con errores"]),
                 ("Precedencia", ["Correcta"] * 3)]
        for texto, fases in casos:
            with self.subTest(boton=texto):
                self.boton(texto).invoke()
                self.assertEqual(self.fases(), ["Pendiente"] * 3)          # cargar ejemplo reinicia
                self.boton("Analizar").invoke()
                self.assertEqual(self.fases(), fases)

    def test_limpiar_y_editor_vacio(self):
        self.boton("Limpiar").invoke()
        self.assertEqual(self.v.editor_codigo.get("1.0", "end-1c"), "")
        self.boton("Analizar").invoke()
        self.assertIn("vacio", self.v.area_informe_final.get("1.0", "end"))


if __name__ == "__main__":
    unittest.main()
