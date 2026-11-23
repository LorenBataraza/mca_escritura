# Configuracion de latexmk para esta tesis.
#
# Uso:
#   latexmk template          -> compila a PDF, corriendo biber y repitiendo
#                                pdflatex las veces que haga falta
#   latexmk -pvc template     -> queda escuchando cambios y recompila solo
#   latexmk -C template       -> borra PDF y todos los auxiliares
#   latexmk -c template       -> borra auxiliares pero deja el PDF

$pdf_mode = 1;        # pdflatex
$bibtex_use = 2;      # correr biber/bibtex siempre, y borrar .bbl en -C

# latexmk >= 4.5x detecta biblatex por el archivo .bcf y llama a biber solo.
# Lo dejamos explicito para que no dependa de la version.
$biber = 'biber --validate-datamodel %O %S';

# Cortar los reruns si no converge (evita loops infinitos por un label roto)
$max_repeat = 7;

# Auxiliares que genera biblatex/biber y que latexmk no limpia por default
push @generated_exts, 'bcf', 'run.xml', 'bbl';
$clean_ext .= ' %R-blx.bib synctex.gz';
