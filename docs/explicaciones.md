Propósito: explicar los conceptos del compilador desde cero, con un ejemplo de principio a fin. Es el documento de estudio para entender cada parte antes de la sustentación.

markdown
# Explicaciones desde cero

## 1. Qué es un compilador

Un compilador es un programa que traduce código fuente escrito en un
lenguaje a otro lenguaje o a una representación ejecutable. En este
proyecto el objetivo no es generar código máquina: el compilador llega
hasta el análisis semántico y se detiene ahí, mostrando lo que encontró
en cada fase.

## 2. Las tres fases

### 2.1 Análisis léxico

Convierte el texto fuente en **tokens**. Un token es la unidad mínima
significativa del lenguaje: una palabra reservada, un identificador, un
número, una cadena, un operador, un signo de puntuación. El lexer
también detecta errores de bajo nivel: caracteres no permitidos, cadenas
sin cerrar, números mal formados.

Ejemplo:

    var edad : entero = 2 + 3;

se convierte en tokens:
`[var]` `[edad]` `[:]` `[entero]` `[=]` `[2]` `[+]` `[3]` `[;]`

Cada token guarda `[tipo, lexema, línea, columna, valor]`.

### 2.2 Análisis sintáctico

Convierte los tokens en un **Árbol de Sintaxis Abstracta (AST)**. El
árbol representa la estructura del programa, no los detalles textuales.
Si la secuencia de tokens respeta la gramática, el árbol se construye.
Si no, se reportan errores sintácticos.

Ejemplo: `var x : entero = 2 + 3 * 4;` produce
declaracion
nombre: x
tipo: entero
expresion: binaria +
izquierda: entero 2
derecha: binaria *
izquierda: entero 3
derecha: entero 4

text

El `*` está más abajo que el `+`, lo que significa que se agrupa primero.
Eso es la precedencia.

### 2.3 Análisis semántico

Recorre el AST y verifica reglas de significado. Construye una **tabla
de símbolos** que asocia cada nombre de variable con su tipo. Detecta
errores que la fase sintáctica no puede ver: variables no declaradas,
tipos incompatibles, redeclaraciones.

Ejemplo: `var y : entero = "hola";` es léxicamente correcto (todos los
caracteres son válidos) y sintácticamente correcto (respeta la
gramática), pero semánticamente incorrecto (está asignando una cadena a
un entero). **Por eso existen tres fases separadas.**

## 3. Conceptos clave

### 3.1 Token

Unidad mínima significativa. Ejemplo: `var`, `x`, `:`, `entero`, `=`,
`5`, `;` son 7 tokens. Cada uno tiene una categoría (`PALABRA_RESERVADA`,
`IDENTIFICADOR`, `DOS_PUNTOS`, `TIPO_DATO`, `ASIGNACION`, `ENTERO`,
`PUNTO_COMA`).

### 3.2 Gramática

Conjunto de reglas que dicen qué secuencias de tokens son válidas. La
gramática del lenguaje está documentada en EBNF en el README. Por
ejemplo, una declaración es:

    "var" identificador ":" tipo "=" expresion ";"

Si el usuario escribe `var : entero = 5;` (falta el nombre), la gramática
no se cumple y el parser reporta un error.

### 3.3 AST (Árbol de Sintaxis Abstracta)

Estructura jerárquica que representa el programa. Los nodos internos son
operaciones o instrucciones; las hojas son literales o identificadores.
El AST no contiene paréntesis, espacios, comentarios ni signos de
puntuación: solo la estructura semántica.

### 3.4 Tabla de símbolos

Estructura que asocia cada nombre de variable con su tipo y posición.
En este proyecto es una lista de listas:

    [["edad", "entero", 1, 5]]

Cada fila significa: "la variable `edad` es de tipo `entero` y se declaró
en línea 1, columna 5". Se construye durante el análisis semántico y se
consulta cada vez que se usa una variable.

### 3.5 Regla semántica

Una restricción que no se puede expresar solo con la gramática. Por
ejemplo: "no se puede declarar dos veces la misma variable", "no se
puede asignar una cadena a un entero", "no se puede dividir por cero
si el lenguaje lo prohíbe". Las reglas semánticas se implementan
recorriendo el AST y consultando la tabla de símbolos.

## 4. Cómo se conectan las tres fases
Código fuente
→ [analizar_lexico] → tokens + errores léxicos
→ [analizar_sintactico] → AST + errores sintácticos
→ [analizar_semantico] → tabla + errores semánticos
→ interfaz

text

Cada fase recibe **solo** lo que produce la anterior. El parser no lee
el texto, solo los tokens. El semántico no lee tokens, solo el AST. Eso
permite detectar exactamente qué fase falló y reportar errores claros.

## 5. Ejemplo de principio a fin

### 5.1 Programa que se analiza
var x : entero = 2 + 3 * 4;
mostrar x;

text

### 5.2 Fase léxica (tokens)

15 tokens: `var x : entero = 2 + 3 * 4 ; mostrar x ; FIN`.
Sin errores léxicos.

### 5.3 Fase sintáctica (AST)
Programa
Declaracion x : entero
Binaria: +
entero: 2
Binaria: *
entero: 3
entero: 4
Mostrar
identificador: x

text

Sin errores sintácticos. El `*` está más abajo que el `+`.

### 5.4 Fase semántica (tabla + reglas)

Tabla: `[["x", "entero", 1, 5]]`. Se verifica que `2 + 3 * 4` es
`entero` (la multiplicación de enteros es entero, la suma de enteros es
entero) y coincide con el tipo declarado. `mostrar x` consulta la tabla
y encuentra `x`. Sin errores semánticos.

### 5.5 Qué aparece en la interfaz

Las tres etiquetas en verde, los tres paneles con contenido, e informe
final con "ANALISIS COMPLETO SIN ERRORES".

### 5.6 Modificación a error léxico

Cambiar a `var x : entero = 5 @ 3;`. El lexer detecta `@` en columna
20 y reporta error. La interfaz no ejecuta las siguientes fases.

### 5.7 Modificación a error sintáctico

Cambiar a `var x : entero = 2 + ;`. El lexer no falla. El parser
detecta que falta un operando y reporta error en `;`. La semántica no
se ejecuta.

### 5.8 Modificación a error semántico

Cambiar a `var x : entero = "hola";`. Las fases léxica y sintáctica
terminan sin error. La semántica infiere el tipo `cadena` en la
expresión, lo compara con `entero` declarado, y reporta error de tipo.
**Este caso es el más importante para la sustentación**: demuestra por
qué existen tres fases.

## 6. Glosario rápido

- **Compilador:** programa que traduce código fuente.
- **Lexer / analizador léxico:** convierte texto en tokens.
- **Parser / analizador sintáctico:** convierte tokens en AST.
- **Analizador semántico:** recorre el AST y verifica reglas.
- **Token:** unidad mínima significativa.
- **Lexema:** texto original del token (`var`, `edad`, `2`, etc.).
- **Tipo:** categoría de un valor (`entero`, `decimal`, `cadena`, `booleano`).
- **Precedencia:** orden en que se agrupan los operadores (`*` antes que `+`).
- **Asociatividad:** orden cuando hay varios del mismo nivel (`10 - 3 - 2` es `(10 - 3) - 2`).
- **AST:** árbol que representa la estructura semántica del programa.
- **Tabla de símbolos:** asociación nombre ↔ tipo de cada variable.
- **Recursión:** una función que se llama a sí misma. El parser es recursivo porque las expresiones contienen expresiones.