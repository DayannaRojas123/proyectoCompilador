Propósito: preparar la sustentación oral. Contiene respuestas a preguntas típicas, guion de demostración y mapa de "qué tocar en cada fase" si el profesor pide una modificación en vivo.

markdown
# Guía de sustentación

## 1. Explicación oral breve (30 segundos)

"Construimos un compilador educativo que procesa un lenguaje de
programación pequeño que definimos nosotras. El compilador tiene tres
fases: análisis léxico, que convierte el texto en tokens; análisis
sintáctico, que convierte los tokens en un árbol sintáctico; y análisis
semántico, que recorre ese árbol y verifica reglas de significado
usando una tabla de símbolos. La interfaz gráfica muestra todo el
proceso en vivo: cada cambio en el editor produce resultados distintos."

## 2. Descripción del funcionamiento general

El flujo es: código fuente → tokens → AST → tabla de símbolos → informe.
Cada fase recibe el resultado real de la anterior y nunca lee
directamente el texto fuente de otra fase. La interfaz solo orquesta:
lee el editor, llama las tres fases en orden, y muestra los paneles.
Si una fase falla, las siguientes no se ejecutan.

## 3. Explicación de cada fase

**Léxica** (`analizador_lexico.py`): recorre el texto carácter por
carácter. Reconoce palabras reservadas, identificadores, números,
cadenas, operadores, comentarios `//`, espacios y saltos de línea. Cada
token guarda `[tipo, lexema, línea, columna, valor]`. Los errores
léxicos son caracteres no permitidos, cadenas sin cerrar y números mal
formados.

**Sintáctica** (`analizador_sintactico.py`): recibe los tokens y
construye un AST con descenso recursivo. Cada nivel de precedencia es
una función distinta: `expresion_logica` → `y` → `no` → `relacional`
→ `aritmetica` → `termino` → `factor` → `primario`. La precedencia se
logra por el orden de las funciones, la asociatividad por `while`, y el
menos unario por una rama especial en `analizar_factor`.

**Semántica** (`analizador_semantico.py`): recorre el AST, construye
la tabla de símbolos y verifica reglas: variables declaradas antes de
usarse, prohibición de redeclarar, tipos compatibles en asignaciones y
operadores. La inferencia de tipos es recursiva: cada nodo del AST
devuelve su tipo.

## 4. Demostración sugerida (5 minutos)

1. Abrir `python principal.py`.
2. Pulsar **Ejemplo valido** → **Analizar**. Mostrar que las tres
   etiquetas están en verde y las pestañas se llenan.
3. Abrir la pestaña **Arbol sintactico** y señalar cómo el `*` cuelga
   del `+` en `2 + 3 * 4`.
4. Pulsar **Error lexico** → **Analizar**. Solo la etiqueta léxica en
   rojo; las otras dos dicen "no ejecutada". Explicar por qué.
5. Pulsar **Error semantico** → **Analizar**. Léxica y sintáctica en
   verde, semántica en rojo. **Este es el caso estrella**: el código
   compila pero no tiene significado.
6. Pulsar **Precedencia** → **Analizar**. Árbol con `+` colgando de
   `*` por culpa de los paréntesis.
7. Editar el código a mano con algo nuevo (por ejemplo
   `var a : decimal = 1.5 * 2.0;`) y pulsar Analizar. Los resultados
   cambian en vivo.

## 5. Preguntas típicas y respuestas modelo

**P: ¿Por qué tres analizadores y no uno?**
R: Porque detectan clases distintas de errores. Un código puede ser
léxicamente correcto (todos los caracteres válidos), sintácticamente
correcto (respeta la gramática) y aun así semánticamente incorrecto
(tipos incompatibles). Si tuviéramos un solo analizador, no podríamos
reportar con precisión cuál es el error.

**P: ¿Qué es un token?**
R: La unidad mínima significativa del lenguaje. Cada palabra reservada,
identificador, número, operador o signo de puntuación es un token.
El lexer los agrupa y les asigna una categoría.

**P: ¿Qué es un AST y en qué se diferencia del árbol sintáctico
concreto?**
R: El AST representa solo la estructura semántica, sin detalles
sintácticos. Los paréntesis, por ejemplo, no aparecen en el AST: solo
afectan la forma del árbol. `(2 + 3) * 4` y `2 + 3 * 4` producen ASTs
distintos porque la estructura es distinta.

**P: ¿Cómo garantizan la precedencia?**
R: Por el orden de las funciones del parser. `analizar_expresion_aritmetica`
llama a `analizar_termino` como primer operando, y `analizar_termino`
solo acepta `*` y `/`. Como `analizar_termino` termina antes de devolver
a `analizar_expresion_aritmetica`, cualquier `*` se consume antes que
cualquier `+`.

**P: ¿Dónde está la tabla de símbolos y qué contiene?**
R: En `analizador_semantico.py`, variable global `tabla_simbolos`.
Contiene una lista de listas `[nombre, tipo, línea, columna]`, una por
variable declarada. Se construye durante el recorrido del AST.

**P: ¿Qué pasa si hay un error?**
R: El lexer acumula errores léxicos. Si hay alguno, la interfaz no
ejecuta el parser. Si el parser falla, no ejecuta el semántico. Si el
semántico falla, sí se ejecutó el árbol completo pero la tabla muestra
los errores. La interfaz dice explícitamente qué fases se ejecutaron.

**P: ¿Cómo manejan errores dentro de una instrucción?**
R: El parser, cuando falla una instrucción, salta tokens hasta el `;`
y continúa con la siguiente. Eso permite recuperar programas parcialmente
válidos y reportar varios errores en una sola pasada.

**P: ¿Por qué el lenguaje no tiene condicionales ni ciclos?**
R: Porque el objetivo era demostrar las tres fases con el menor código
posible. Condicionales y ciclos agregan mucha complejidad al parser y al
analizador semántico (ámbitos, ramas, retornos) sin aportar nada nuevo
a las tres fases exigidas.

**P: ¿Qué limitaciones tiene el lenguaje?**
R: No admite escapes en cadenas, no tiene ámbitos, los operadores
relacionales no se pueden encadenar, y la división entre enteros produce
decimal (no entera). Cada una de esas limitaciones está documentada en
el README.

**P: ¿Cómo probaron que funciona?**
R: `pruebas.py` corre 12 pruebas automatizadas con `unittest`, una por
cada caso mínimo del enunciado. Si todas pasan, el compilador funciona.

**P: ¿Qué pasa si el usuario introduce un comentario?**
R: `saltar_espacios_y_comentarios` en el lexer consume desde `//` hasta
el salto de línea. No genera tokens. La línea siguiente arranca con
columna 1.

**P: ¿Cómo se conectan las fases?**
R: `principal.py` → `interfaz_grafica.py` → `analizar_codigo` llama
`analizar_lexico`, cuyo resultado pasa a `analizar_sintactico`, cuyo
resultado pasa a `analizar_semantico`. Los paneles muestran los
resultados de cada fase.

## 6. Modificaciones que puede pedir el profesor

### 6.1 Añadir una palabra reservada nueva (`si`)

- `lenguaje.py`: agregar `"si"` a `PALABRAS_RESERVADAS_SIMPLES`.
- `analizador_sintactico.py`: agregar rama en `analizar_instruccion`
  y nueva función `analizar_si`.
- `analizador_semantico.py`: agregar caso `"si"` en
  `procesar_instruccion`.
- `interfaz_grafica.py`: no requiere cambio.
- `pruebas.py`: agregar una prueba nueva.

### 6.2 Añadir un operador nuevo (`%`)

- `lenguaje.py`: agregar `TIPO_MODULO = "MODULO"`.
- `analizador_lexico.py`: agregar `if caracter == '%':` en
  `analizar_operador`.
- `analizador_sintactico.py`: incluir `TIPO_MODULO` en el `while` de
  `analizar_termino`.
- `analizador_semantico.py`: agregar `"%"` a la lista de operadores
  aritméticos en `inferir_tipo_binaria` y definir sus reglas de tipo
  en `tipo_aritmetico`.

### 6.3 Añadir un tipo de dato nuevo (`longitud`)

- `lenguaje.py`: agregar `"longitud"` a `TIPOS_DATOS`.
- `analizador_semantico.py`: decidir qué operaciones admite y agregarlo
  en `tipo_aritmetico` y `tipo_relacional`.
- `analizador_lexico.py`: sin cambios (ya reconoce `TIPO_DATO` para
  cualquier palabra de `TIPOS_DATOS`).

### 6.4 Cambiar la división de enteros para que sea entera

- `analizador_semantico.py`: en `tipo_aritmetico`, quitar la rama que
  convierte `/` en `decimal` y devolver `entero` cuando ambos operandos
  son enteros.

### 6.5 Permitir relacionales encadenados (`2 < 3 < 4`)

- `analizador_sintactico.py`: cambiar el `if` de
  `analizar_expresion_relacional` por un `while`, y quitar el error
  explícito que agregamos con el parche.
- `analizador_semantico.py`: definir la regla de tipos para el
  encadenamiento (por ejemplo, exigir que el resultado del primero sea
  booleano).

### 6.6 Añadir cadenas con escapes (`\"`)

- `analizador_lexico.py`: en `analizar_cadena`, antes de comparar con
  `"`, detectar `\\` y consumir dos caracteres de golpe.

## 7. Mapa mental "qué tocar dónde"

| Cambio | Léxico | Sintáctico | Semántico | Interfaz |
|---|---|---|---|---|
| Palabra reservada nueva | X | X | X | — |
| Operador nuevo | X | X | X | — |
| Tipo de dato nuevo | — | — | X | — |
| Regla de tipos nueva | — | — | X | — |
| Instrucción nueva | — | X | X | — |
| Cambio de mensaje de error | X | X | X | — |
| Nueva pestaña o botón | — | — | — | X |

## 8. Frases para defender decisiones

- **Sobre no usar librerías de parsing:** "El profesor podría haber
  aceptado Lark o ANTLR, pero la asignatura exige demostrar la
  construcción manual del parser. Escribir el descenso recursivo nos
  obligó a comprender la precedencia y la asociatividad desde dentro."
- **Sobre no usar clases:** "Toda la lógica del compilador está en
  funciones de nivel superior con variables globales controladas. Es
  más fácil de leer, explicar y modificar durante la sustentación.
  Tkinter y unittest los usamos sin clases porque también lo permiten."
- **Sobre el alcance pequeño del lenguaje:** "Elegimos el lenguaje más
  pequeño que demuestra las tres fases. Añadir condicionales o ciclos
  no habría añadido nada nuevo a la comprensión del compilador, solo
  más código."
- **Sobre la división entre enteros que da decimal:** "Es una decisión
  del lenguaje para evitar perder información. Está documentada en el
  README y es modificable en una línea si el profesor lo pide."

## 9. Verificación final antes de entrar

- [ ] `python pruebas.py` → `Ran 12 tests ... OK`.
- [ ] `python principal.py` → ventana abierta.
- [ ] Los cinco botones de ejemplo funcionan.
- [ ] La pestaña **Arbol sintactico** muestra el `*` bajo el `+` en
      el ejemplo de precedencia.
- [ ] El informe final cambia según la fase donde falla.