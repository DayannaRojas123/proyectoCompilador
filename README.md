# Compilador Educativo — LenguajeEducativo

Compilador didáctico escrito en Python con interfaz gráfica Tkinter. Analiza un
programa en tres fases (**léxica → sintáctica → semántica**) y muestra los
tokens, el árbol sintáctico, la tabla de símbolos, los errores y un informe final.

## Cómo ejecutarlo

Requisitos: **Python 3.8 o superior** (Tkinter ya viene incluido en Windows y macOS;
en Linux: `sudo apt install python3-tk`). No hay que instalar nada más.

```bash
cd proyectoCompilador
python principal.py          # en algunos sistemas: python3 principal.py
```

Uso: escribe código en el editor (o pulsa un botón de **Ejemplos**) y pulsa
**Analizar** (atajos: `Ctrl+Enter` o `F5`).

Pruebas automáticas:

```bash
python -m unittest -v
```

## Estructura del proyecto

```
proyectoCompilador/
├── principal.py              Punto de entrada (abre la ventana)
├── compilador/               Lógica del compilador (sin interfaz)
│   ├── lenguaje.py             Constantes y palabras reservadas del lenguaje
│   ├── analizador_lexico.py    Fase 1: texto  -> tokens
│   ├── analizador_sintactico.py Fase 2: tokens -> árbol sintáctico
│   └── analizador_semantico.py Fase 3: árbol  -> tabla de símbolos y tipos
├── interfaz/                 Interfaz gráfica (Tkinter)
│   ├── ventana.py              Distribución de la ventana y acciones de los botones
│   ├── editor.py               Editor: números de línea, colores, líneas con error
│   ├── tema.py                 Paleta de colores, fuentes y estilos
│   ├── ejemplos.py             Programas de ejemplo de los botones
│   └── formato.py              Conversión de resultados a texto
├── tests/                    Pruebas automáticas
└── docs/                     explicaciones.md, guia_sustentacion.md
```

Regla de dependencias: `principal.py` → `interfaz` → `compilador`. El paquete
`compilador` no importa nada de la interfaz, así que se puede usar o probar solo:

```bash
python -m compilador.analizador_lexico      # demo de cada módulo
python -m compilador.analizador_sintactico
python -m compilador.analizador_semantico
```

## Personalizar la apariencia

Colores y tipografías: `interfaz/tema.py`. Ejemplos de los botones: `interfaz/ejemplos.py`.

## Lenguaje de ejemplo

```
var edad : entero = 2 + 3 * 4;
mostrar edad;
```

Tipos: `entero`, `decimal`, `cadena`, `booleano`. Palabras reservadas: `var`, `mostrar`,
`verdadero`, `falso`, `y`, `o`, `no` (por eso `y` no se puede usar como nombre de variable).
