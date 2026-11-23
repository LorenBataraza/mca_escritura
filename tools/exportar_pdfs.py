#!/usr/bin/env python3
"""Exporta la tesis completa y un PDF por capitulo (y por apendice) a pdf/.

Compila con latexmk y despues corta template.pdf por capitulo, asi cada PDF
suelto tiene la misma numeracion de paginas, figuras y referencias cruzadas
que la tesis completa, y su propia bibliografia (va al final de cada capitulo).

Donde empieza cada capitulo sale de template.toc (titulo y destino PDF de cada
\\chapter) y de `pdfinfo -dests` (pagina fisica de cada destino). Un capitulo
termina donde empieza la siguiente entrada de nivel capitulo del indice. Las
paginas en blanco que deja la doble faz al final de un capitulo se descartan.

Uso:
    python3 tools/exportar_pdfs.py              # compila y exporta
    python3 tools/exportar_pdfs.py -n           # exporta sin compilar
"""
import argparse
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata

RAIZ = pathlib.Path(__file__).resolve().parent.parent
MAESTRO = "template"
SALIDA = RAIZ / "pdf"


def correr(*cmd, **kw):
    # La salida de latexmk mezcla UTF-8 con Latin-1: no fallar por eso.
    return subprocess.run(cmd, capture_output=True, encoding="utf-8",
                          errors="replace", cwd=RAIZ, **kw)


def entradas_toc():
    """[(numero, titulo, destino)] de las entradas de nivel capitulo del .toc."""
    toc = (RAIZ / f"{MAESTRO}.toc").read_text(encoding="utf-8")
    patron = re.compile(r"\\contentsline \{chapter\}\{(.*)\}\{(.*?)\}\{(.*?)\}%")
    entradas = []
    for linea in toc.splitlines():
        m = patron.match(linea)
        if not m:
            continue
        texto, _, destino = m.groups()
        num = re.match(r"\\numberline \{(.*?)\}(.*)", texto)
        numero, titulo = (num.group(1), num.group(2)) if num else (None, texto)
        entradas.append((numero, titulo, destino))
    return entradas


def paginas_destinos(pdf):
    """{destino: pagina fisica} segun pdfinfo -dests."""
    r = correr("pdfinfo", "-dests", str(pdf))
    destinos = {}
    for linea in r.stdout.splitlines():
        m = re.match(r'\s*(\d+)\s+\[.*\]\s+"(.*)"', linea)
        if m:
            destinos[m.group(2)] = int(m.group(1))
    return destinos


def en_blanco(pdf, pagina):
    texto = correr("pdftotext", "-f", str(pagina), "-l", str(pagina),
                   str(pdf), "-").stdout
    return not re.sub(r"[\sivxlcdm\d]", "", texto, flags=re.I)


def nombre_archivo(numero, titulo):
    titulo = re.sub(r"\\[a-zA-Z]+|[{}\\']", "", titulo)
    plano = unicodedata.normalize("NFKD", titulo).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "_", plano.lower()).strip("_")
    prefijo = f"cap{numero}" if numero.isdigit() else f"ap{numero}"
    return f"{prefijo}_{slug}.pdf"


def extraer(pdf, desde, hasta, destino):
    with tempfile.TemporaryDirectory() as td:
        patron = pathlib.Path(td) / "p%04d.pdf"
        correr("pdfseparate", "-f", str(desde), "-l", str(hasta),
               str(pdf), str(patron))
        hojas = sorted(pathlib.Path(td).glob("p*.pdf"))
        r = correr("pdfunite", *map(str, hojas), str(destino))
        if r.returncode:
            sys.exit(f"fallo pdfunite: {r.stderr}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-n", "--sin-compilar", action="store_true",
                    help="usar el template.pdf que ya existe")
    args = ap.parse_args()

    if not args.sin_compilar:
        r = correr("latexmk", "-interaction=nonstopmode", MAESTRO)
        if r.returncode:
            sys.exit("latexmk fallo; ver template.log")

    pdf = RAIZ / f"{MAESTRO}.pdf"
    total = int(re.search(r"Pages:\s+(\d+)", correr("pdfinfo", str(pdf)).stdout)[1])
    destinos = paginas_destinos(pdf)
    entradas = entradas_toc()

    SALIDA.mkdir(exist_ok=True)
    shutil.copy2(pdf, SALIDA / "tesis_completa.pdf")
    print(f"  tesis_completa.pdf  ({total} págs.)")

    generados = set()
    for i, (numero, titulo, destino) in enumerate(entradas):
        if numero is None:          # índices, resumen, agradecimientos...
            continue
        desde = destinos.get(destino)
        if desde is None:
            print(f"  AVISO: no encuentro la página de '{titulo}'", file=sys.stderr)
            continue
        siguientes = [destinos[d] for _, _, d in entradas[i + 1:] if d in destinos]
        hasta = (siguientes[0] - 1) if siguientes else total
        while hasta > desde and en_blanco(pdf, hasta):
            hasta -= 1
        archivo = nombre_archivo(numero, titulo)
        extraer(pdf, desde, hasta, SALIDA / archivo)
        generados.add(archivo)
        print(f"  {archivo}  (págs. {desde}-{hasta} del PDF completo)")

    # Al insertar o reordenar capítulos cambian los números, y el PDF con el
    # nombre viejo (p. ej. cap3_implementacion_del_multitrigger.pdf cuando el
    # multitrigger pasó a ser el 4) quedaría confundiendo. Se borran sólo los
    # capN_/apX_ que este mismo script genera y que en esta corrida no salieron.
    for viejo in sorted(SALIDA.glob("*.pdf")):
        if re.fullmatch(r"(cap\d+|ap[A-Z])_.+\.pdf", viejo.name) and viejo.name not in generados:
            viejo.unlink()
            print(f"  borrado {viejo.name} (ya no corresponde a ningún capítulo)")


if __name__ == "__main__":
    main()
