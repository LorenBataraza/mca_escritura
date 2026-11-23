# Template de tesis IB — notas de uso

## Compilar

```bash
latexmk template          # compila a PDF (corre biber solo)
latexmk -pvc template     # recompila al guardar
latexmk -c template       # borra auxiliares, deja el PDF
latexmk -C template       # borra todo, incluido el PDF
```

La configuración está en `latexmkrc`. No hace falta pasar `-pdf`.

## Capítulos

Los archivos `capN.tex` se numeran por orden de creación; el orden y el número
de capítulo en la tesis los da el orden de los `\include` en `template.tex`.

| Archivo | Cap. | Contenido | Nota de origen (`Secciones/`) |
|---|---|---|---|
| `cap6.tex` | 1 | Tipos de usuario y aplicación | `PI - Tipos de Usuario y APP.md` |
| `cap1.tex` | 2 | Analizador multicanal | `PI - Analizador Multicanal.md` |
| `cap2.tex` | 3 | Hardware empleado | `PI - Hardware empleado.md` |
| `cap5.tex` | 4 | Conceptos de diseño de hardware | `PI - Conceptos de diseno en HW.md` |
| `cap3.tex` | 5 | Implementación del multitrigger | `PI - Implementacion Multitrigger.md` |
| `cap7.tex` | 6 | Implementación del MCA (**señuelo**) | `PI - Implementacion MCA.md` |
| `cap9.tex` | 7 | Resultados de mérito | `PI - Resultados de Merito.md` (la parte de Monte-Carlo está en `PI - Resultados Monte - Carlo.md`, sin convertir) |
| `cap8.tex` | 8 | Implementación del OSC | `PI - Implementacion OSC.md` |
| `cap12.tex` | 9 | Implementación del TOP (integración) | `PI - Implementacion TOP (Integracion).md` |
| `cap10.tex` | 10 | Software | `PI - Software.md` |
| `cap4.tex` | 11 | Verificación de normativa nacional e internacional | `PI - Verificación de normativa nacional e internacional.md` |
| `cap11.tex` | 12 | Conclusiones y futuros pasos | `PI - Conclusiones y Futuros Pasos.md` |
| `apend4.tex` | A | Capturas de la aplicación | "Apéndice" de `PI - Tipos de Usuario y APP.md` |
| `apend1.tex` | B | Complementos del analizador multicanal | "Apéndice" de `PI - Analizador Multicanal.md` |
| `apend2.tex` | C | Complementos del hardware empleado | "Apéndice" de `PI - Hardware empleado.md` |
| `apend3.tex` | D | Detalles del multitrigger | "Apéndice", "Mapa de Memoria" y "Verificación" de `PI - Implementacion Multitrigger.md` |
| `apend6.tex` | E | Detalles del osciloscopio | "Apendice" de `PI - Implementacion OSC.md` (lo que está entre `%%` no se transcribe) |
| `apend5.tex` | F | Complementos del software | "Apéndice" de `PI - Software.md` |

Los **señuelos** reservan el lugar en el índice y el label del capítulo
(queda `C:implmca`), con un aviso
en rojo (`\capitulopendiente`). Al convertir la nota se reemplaza el archivo
entero, conservando ese `\label`.

Los capítulos empiezan en la página siguiente al anterior, sin hoja en blanco
(opción `openany` en `\documentclass`).

Los capítulos de ejemplo de la template original quedaron en `ejemplos/`
(no se compilan). Sirven de referencia para citas, localizadores y figuras.

### Referencias a capítulos que todavía no existen

Las notas enlazan secciones de otras notas que aún no se pasaron a LaTeX. Para
esas se usa `\refpend{label}{texto}` (definido en `ibextra.sty`): si el label
existe imprime el número como `\ref`; si no, el texto en rojo. Cuando se pase
el capítulo destino, alcanza con ponerle ese mismo `\label` y se resuelve solo.

```bash
grep -o 'refpend{[^}]*}' cap*.tex apend*.tex | sort | uniq -c   # pendientes
```

Prefijos de labels: `C:` capítulo, `S:` sección, `f:` figura, `t:` tabla,
`e:` ecuación. Las secciones de otras notas usan el nombre de la nota:
`S:implmca-…` (Implementación MCA), `S:sw-…` (Software), `S:res-…`
(Resultados), `S:intro-hw-…` (Conceptos de diseño de hardware), `S:top-…`
(Implementación TOP), `S:osc-…` (Implementación OSC). `\incompleto` marca en rojo una frase que quedó sin
terminar en la nota.

## Formato (todo en `ibextra.sty`)

- **Márgenes**: 20 mm a los costados, 22 mm arriba, 18 mm abajo. Pisa el
  `geometry` de la clase.
- **Listas**: sin espacio extra entre `\item` (`enumitem`).
- **Epígrafes**: rótulo y texto en gris (`epigrafe`), en figuras y tablas.
- **Referencias**: las entradas de cada bibliografía van en `\small`, con
  interlineado simple y poco aire entre una y otra (`\bibfont`, `\bibitemsep`).
- **Figuras**: dentro de un `figure` ocupan el ancho del texto (el borde de la
  figura coincide con el del párrafo; `\desbordefig` = 0 mm, subirlo las mete en
  los márgenes), con altura libre y tope en `\alturafig` (`0.62\textheight`).
  Basta con `\includegraphics{nombre}`.
- **Figuras y tablas en su lugar**: todas van con `[H]`, escritas justo después
  del párrafo que las comenta (si el párrafo sigue con una lista, después de la
  lista). Si no entran, pasan a la página siguiente y la anterior queda corta
  (`\raggedbottom` global). No usar `\floatplacement` (rompe `figuraapaisada`).
  Una tabla más alta que una página va como `longtable` (apéndices C y E).
  El log avisa de páginas sólo con floats: `grep -a PAGINA-SOLO-FLOATS
  template.log` (con `-a`, el log tiene bytes Latin-1). Las apaisadas salen como
  "apaisada, esperado".
- **Figuras apaisadas**: para las muy anchas (waveforms), entorno
  `figuraapaisada` en lugar de `figure`. Va en una página propia, girada (lo de
  arriba de la figura hacia el lomo), y el PDF la muestra rotada en pantalla.
  Admite varias imágenes, cada una con su `\caption` y `\label`:

  ```latex
  \begin{figuraapaisada}
  \includegraphics[height=0.4\textwidth]{cap5_bus_escritura}
  \caption{...}\label{f:...}
  \end{figuraapaisada}
  ```
  `\figurapend{figs/capN/nombre}{Dibujo}` deja un recuadro rojo mientras no
  exista el PDF (dibujos de Excalidraw sin SVG exportado).
- **Tablas**: grilla gris (`|` entre columnas, `\hline` entre filas) y fila de
  encabezado con `\encabezado` al principio:

  ```latex
  \begin{tabularx}{\textwidth}{|l|X|}
  \hline \encabezado \textbf{Columna} & \textbf{Otra} \\ \hline
  dato & dato \\ \hline
  \end{tabularx}
  ```
- **Código**: nada de `\texttt` ni `\verb` sueltos; cada cosa con su macro,
  así el estilo se cambia en un solo lugar:

  | Macro | Para | Aspecto |
  |---|---|---|
  | `\codigo{trig\_arm}` | señales, registros, módulos, parámetros, valores | monoespaciada azul oscuro; va en epígrafes y tablas |
  | `\cmd\|make app\|` | comando de terminal dentro del texto | fondo gris; texto tal cual, como `\verb` (no en `\caption`) |
  | `\ruta{prj/MCA}` | archivos y carpetas | azul oscuro; se corta en las `/` |
  | `\begin{comando}` … `\end{comando}` | líneas de terminal en su renglón | caja gris con `$` delante; las largas se cortan solas |

  En los títulos de sección queda `\texttt` (sin color en el índice).
- **Cita destacada** (`> …` en la nota): entorno `destacado`, caja gris con
  barra a la izquierda.

## Exportar PDFs

```bash
python3 tools/exportar_pdfs.py      # compila y deja todo en pdf/
python3 tools/exportar_pdfs.py -n   # sin compilar, usa el template.pdf actual
```

Deja `pdf/tesis_completa.pdf` y un PDF por capítulo y por apéndice
(`cap1_analizador_multicanal.pdf`, `apA_…`). El número del nombre es el del
capítulo en la tesis, no el del archivo `.tex`. Si al reordenar capítulos queda
un `capN_…`/`apX_…` que ya no corresponde, el script lo borra y lo avisa. Los sueltos se cortan de la tesis
completa, así que conservan la numeración de páginas, figuras y referencias
cruzadas, y cada uno lleva su bibliografía.

## Bibliografía

Motor: **biblatex + biber**. Reemplaza al `natbib` + `ibtesis.bst` originales.
La configuración está en `ibextra.sty`; `ibtesis.bst` quedó en el repo pero no
se usa (cómo volver atrás está comentado en ese mismo archivo).

### Una bibliografía por capítulo

Lo hace la opción `refsection=chapter`. Cada `\chapter` abre una *refsection*
nueva, y al final de cada archivo de capítulo va:

```latex
\bibliografiacapitulo              % título "Referencias"
\bibliografiacapitulo[Otro título] % título a medida
```

Entra al índice como sección del capítulo. Los apéndices también son
`\chapter`, así que también tienen la suya.

Una misma clave citada en varios capítulos aparece en cada bibliografía, con
numeración independiente (cada capítulo numera desde 1). En el `.bib` la
entrada existe una sola vez. No hay nada que hacer para que funcione.

**Bibliografía global al final**: desactivada por default. El bloque está
comentado al final de `template.tex`. Ojo: biblatex no sabe unir refsections,
así que la única forma es `\nocite{*}`, que lista *todas* las entradas de los
`.bib`, citadas o no.

**Cuidado**: lo que se cite antes del capítulo 1 (resumen, abstract) cae en la
refsection 0, que nunca se imprime. Si necesitás citar ahí, hay que agregar un
`\printbibliography[section=0]` explícito.

### Citar una página / capítulo / sección

El argumento opcional de `\cite` es el localizador:

| Qué querés | Cómo | Sale |
|---|---|---|
| Página | `\cite[45]{clave}` | `[4, pág. 45]` |
| Rango | `\cite[45-48]{clave}` | `[4, págs. 45-48]` |
| Capítulo | `\citecap{clave}{5}` | `[4, cap. 5]` |
| Sección | `\citesec{clave}{5.3}` | `[4, sec. 5.3]` |
| Ecuación | `\citeec{clave}{2.17}` | `[4, ec. 2.17]` |
| Figura | `\citefig{clave}{3}` | `[4, fig. 3]` |
| A mano | `\cite[tomo II, ap. B]{clave}` | `[6, tomo II, ap. B]` |

Un número pelado lleva prefijo automático, y biblatex pluraliza solo si detecta
un rango. Los atajos `\citecap` y compañía están definidos en `ibextra.sty`.

También quedan disponibles `\textcite` (autor en el texto) y, por la opción
`natbib=true`, los viejos `\citep` / `\citet` / `\citeauthor` / `\citeyear`.

### Capítulo de libro: dos casos distintos

- **Cito el libro y señalo dónde mirar** → entrada `@book`, el capítulo va en
  la cita: `\citecap{Sakurai2011}{5}`.
- **El capítulo es la referencia en sí** (tiene autor propio) → entrada
  `@incollection` (autor distinto del editor del libro) o `@inbook` (mismo
  autor que el libro). Se cita normal, sin localizador.

Hay ejemplos comentados de los dos al principio de `mibib.bib`.

Para obras en varios tomos: entrada `@mvbook` y cita `\volcite{2}[45]{clave}`.

## Figuras

```
figs/
├── comunes/     compartidas entre capítulos (logos, esquemas recurrentes)
├── cap1/
├── cap2/
└── apendices/
```

Cada archivo de capítulo arranca declarando sus carpetas:

```latex
\graphicspath{{figs/cap2/}{figs/comunes/}}
```

Después, en el `\includegraphics` va **solo el nombre del archivo**, sin
carpeta: `\includegraphics[width=\imsize]{cap2_espectro}`.

**`\graphicspath` es global, no local al archivo.** Si un capítulo nuevo no
declara el suyo, hereda el del capítulo anterior y las figuras "desaparecen".
Regla: archivo de capítulo nuevo → primera línea después del `\chapter`, su
`\graphicspath`.

La alternativa de poner un solo `\graphicspath` con todas las subcarpetas está
comentada en `template.tex`. Tiene el problema de que dos archivos homónimos en
distintas carpetas se resuelven por orden de la lista, en silencio.

Anchos predefinidos por la clase: `\imsizeS` (0.5), `\imsize` (0.7),
`\imsizeL` (0.9 del `\textwidth`).

### Dibujos de Excalidraw

Los dibujos se hacen en Obsidian con el auto-export a SVG activado, que los deja
en `~/Dropbox/DropsyncFiles/Obsidian/Lorenzo/Excalidraw/`. pdflatex no come SVG,
así que hay un paso de conversión a PDF vectorial:

```bash
python3 tools/svg2pdf.py        # convierte lo que cambió
python3 tools/svg2pdf.py -l     # lista el mapeo y su estado
python3 tools/svg2pdf.py -f     # reconvierte todo
```

Qué dibujo entra en la tesis y con qué nombre se decide en `tools/figuras.conf`,
una línea por figura: `<archivo.svg>` TAB `<capítulo>/<nombre>`. No descubre
dibujos solo, a propósito: en el vault hay bocetos que no son figuras.

El conversor es Chrome headless. Excalidraw es una app web y su SVG está pensado
para Blink, así que el PDF sale igual a lo que ves en Obsidian; la fuente
(Excalifont) viaja embebida como TTF dentro del SVG y queda embebida en el PDF,
por eso el texto no se desborda de las cajas. El resultado es vectorial salvo
las imágenes que hayas pegado dentro del dibujo, que siguen siendo mapas de bits.

El mismo script sincroniza también las figuras que **no** son SVG (PNG de
matplotlib, PDF de TikZ del repo MCA): si el origen no termina en `.svg` lo
copia tal cual, con su extensión. El origen puede ser una ruta absoluta o
relativa a `Excalidraw/` (por ejemplo `../Images/dibujo.excalidraw.svg`). Así
`figuras.conf` es el único lugar donde se decide qué figura entra.

**No está enganchado a `latexmk`**, y es a propósito: con `-pvc` abriría Chrome
en cada guardado. Corré `svg2pdf.py` cuando cambies un dibujo.

**Ojo con los dibujos altos.** Varios salen más altos que anchos (el de
multitrigger es 21 × 54 pulgadas). Con `width=\imsize` el alto escalado se va de
la página sin que LaTeX avise. Para esos conviene limitar por altura:

```latex
\includegraphics[width=\imsize,height=0.8\textheight,keepaspectratio]{cap2_multitrigger}
```

O, mejor, partir el dibujo en varias figuras: una de 1:2.5 en una tesis a doble
faz queda ilegible.

## Otros cambios respecto de la template original

- Se quitó `pagebackref` de las opciones de `\documentclass`: choca con
  biblatex. Los back-references ahora los hace biblatex (`backref=true`), y se
  ven como `(vid. pág. N)` al final de cada entrada.
- Se activó `\usepackage[T1]{fontenc}` + `lmodern` en `ibextra.sty`. Sin T1 las
  palabras con acento no se dividen en sílabas correctamente.
- Se agregó `cap2.tex`, que `template.tex` ya incluía pero no existía.
- Se quitó la sección "Publicaciones asociadas" del final (`postliminary`).
- Las figuras de ejemplo son placeholders generados con PGFPlots; reemplazalas.
