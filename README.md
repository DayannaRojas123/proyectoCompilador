# Compilador Educativo — LenguajeEducativo

Proyecto académico de Ingeniería de Sistemas. Compilador educativo que
procesa un lenguaje de programación propio y pequeño, implementando las
tres fases fundamentales: análisis léxico, análisis sintáctico y análisis
semántico, con interfaz gráfica interactiva en español.

No ejecuta el programa ni genera código máquina. El objetivo es demostrar
correctamente las tres fases del compilador.

---

## 1. Qué es

El usuario escribe código fuente en un editor gráfico. Al pulsar el botón
**Analizar**, el compilador procesa ese código y muestra:

- La lista de **tokens** generados (fase léxica).
- El **árbol sintáctico** construido (fase sintáctica).
- La **tabla de símbolos** y los errores semánticos (fase semántica).
- Un **informe final** con el estado global de la compilación.

Cada fase usa los resultados reales de la fase anterior. No hay
resultados fijos ni simulaciones: si el usuario cambia el código, cambian
todos los resultados.

---

## 2. Requisitos

- **Python 3.10 o superior** (probado con 3.12).
- **Tkinter** (viene incluido con Python en Windows y macOS).
- Editor de texto: cualquiera sirve (VS Code, Notepad++, IDLE).

**No se necesitan dependencias externas.** Nada de `pip install`. Todo
usa la biblioteca estándar de Python.

### Verificar la instalación
python --version
Debe mostrar 3.10 o superior. En Mac/Linux puede ser `python3`.

python -c "import tkinter; print('tkinter OK')"
Debe imprimir `tkinter OK`.

---

## 3. Cómo ejecutar

### 3.1 Abrir la interfaz gráfica

Desde la carpeta `proyecto_compilador`:
python principal.py

text

Se abre una ventana con el editor, el estado de las fases, las pestañas
de resultados y los botones. Cerrar con la X de la esquina.

En Mac/Linux usar `python3 principal.py`.

### 3.2 Ejecutar las pruebas automatizadas
python pruebas.py

text

Salida esperada:
............

Ran 12 tests in 0.045s

OK

text

### 3.3 Probar cada fase por separado (opcional)

Cada archivo tiene un bloque de comprobación al final:
python analizador_lexico.py
python analizador_sintactico.py
python analizador_semantico.py

text

Cada uno imprime un ejemplo propio de su fase.

---

## 4. Estructura del proyecto

Todos los archivos están al mismo nivel (sin subcarpetas):
proyecto_compilador/
├── lenguaje.py Definiciones del lenguaje (tipos de token, palabras)
├── analizador_lexico.py Fase 1: texto → tokens
├── analizador_sintactico.py Fase 2: tokens → AST
├── analizador_semantico.py Fase 3: AST → tabla de símbolos y errores
├── interfaz_grafica.py Ventana Tkinter
├── principal.py Punto de entrada
├── pruebas.py 12 pruebas con unittest
├── README.md Este documento
├── GUIA_GITHUB.md Guía para trabajo en equipo
├── GUIA_SUSTENTACION.md Guía para defender el proyecto
└── .gitignore Archivos que Git no debe subir

text

---

## 5. El lenguaje — LenguajeEducativo

### 5.1 Instrucciones

- **Declaración con inicialización:** `var nombre : tipo = expresion;`
- **Asignación:** `nombre = expresion;`
- **Mostrar:** `mostrar expresion;`
- **Comentarios:** `// hasta fin de línea`

### 5.2 Tipos de dato

- `entero`
- `decimal`
- `cadena`
- `booleano`

### 5.3 Literales

- Enteros: `42`, `0`, `100`
- Decimales: `3.14`, `0.5`, `7.0`
- Cadenas: `"hola"`, `"mundo"` (sin escapes)
- Booleanos: `verdadero`, `falso`

### 5.4 Operadores y precedencia

De mayor a menor precedencia:

| Nivel | Operadores | Asociatividad |
|-------|------------|---------------|
| 1 | `( )` | — |
| 2 | `-` unario | derecha |
| 3 | `*`, `/` | izquierda |
| 4 | `+`, `-` | izquierda |
| 5 | `==`, `!=`, `<`, `>`, `<=`, `>=` | no encadenables |
| 6 | `no` | derecha |
| 7 | `y` | izquierda |
| 8 | `o` | izquierda |

### 5.5 Gramática en EBNF

```ebnf
programa              = { instruccion } ;

instruccion           = declaracion | asignacion | mostrar ;

declaracion           = "var" identificador ":" tipo "=" expresion ";" ;
asignacion            = identificador "=" expresion ";" ;
mostrar               = "mostrar" expresion ";" ;

tipo                  = "entero" | "decimal" | "cadena" | "booleano" ;

expresion             = expresion_logica ;
expresion_logica      = expresion_y { "o" expresion_y } ;
expresion_y           = expresion_no { "y" expresion_no } ;
expresion_no          = [ "no" ] expresion_relacional ;
expresion_relacional  = expresion_aritmetica
                        [ operador_relacional expresion_aritmetica ] ;
expresion_aritmetica  = termino { ( "+" | "-" ) termino } ;
termino               = factor { ( "*" | "/" ) factor } ;
factor                = [ "-" ] primario ;

primario              = entero | decimal | cadena
                      | "verdadero" | "falso"
                      | identificador
                      | "(" expresion ")" ;

operador_relacional   = "==" | "!=" | "<" | ">" | "<=" | ">=" ;