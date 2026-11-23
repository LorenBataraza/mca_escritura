#!/usr/bin/env python3
"""Convierte los SVG exportados por Excalidraw a PDF vectorial para la tesis.

El motor es Chrome headless: Excalidraw es una app web y su SVG esta pensado
para Blink, asi que el PDF sale identico a lo que ves en Obsidian. La fuente
(Excalifont) viene embebida en el SVG como TTF base64 y Chrome la respeta, por
eso el texto no se desborda de las cajas.

El mapeo dibujo -> figura esta en tools/figuras.conf, no se descubre solo: vos
elegis que dibujo entra en la tesis y con que nombre.

Los origenes que no son SVG (PNG, PDF de matplotlib o TikZ) se copian tal cual,
con su extension, para que figuras.conf sea el unico lugar donde se decide que
figura entra. El origen puede ser absoluto o relativo a la carpeta Excalidraw/.

Uso:
    python3 tools/svg2pdf.py            # convierte lo que cambio
    python3 tools/svg2pdf.py -f         # reconvierte todo
    python3 tools/svg2pdf.py -l         # lista el mapeo y su estado
"""
import argparse
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

PX_PER_IN = 96.0
RAIZ = pathlib.Path(__file__).resolve().parent.parent
CONF = RAIZ / "tools" / "figuras.conf"
FIGS = RAIZ / "figs"
# Carpeta del vault donde Excalidraw deja los auto-export.
ORIGEN = pathlib.Path(
    "/home/lorenzo/Dropbox/DropsyncFiles/Obsidian/Lorenzo/Excalidraw"
)


def leer_conf():
    """Devuelve [(svg_origen, pdf_destino, linea)] a partir de figuras.conf."""
    if not CONF.exists():
        sys.exit(f"falta {CONF}")
    entradas = []
    for n, linea in enumerate(CONF.read_text(encoding="utf-8").splitlines(), 1):
        linea = linea.split("#")[0].strip()
        if not linea:
            continue
        if "\t" in linea:
            izq, der = linea.split("\t", 1)
        elif "|" in linea:
            izq, der = linea.split("|", 1)
        else:
            sys.exit(f"{CONF}:{n}: falta el separador (tab o |)")
        svg = ORIGEN / izq.strip()   # si izq es absoluto, pathlib ignora ORIGEN
        destino = der.strip()
        if "/" not in destino:
            sys.exit(f"{CONF}:{n}: el destino va como 'capN/nombre'")
        sufijo = ".pdf" if svg.suffix.lower() == ".svg" else svg.suffix.lower()
        entradas.append((svg, (FIGS / destino).with_suffix(sufijo), n))
    return entradas


def medida_svg(path):
    """Ancho y alto en px segun el viewBox (Excalidraw siempre lo escribe)."""
    cabeza = path.read_text(encoding="utf-8", errors="ignore")[:4000]
    m = re.search(r'viewBox="([\d.eE+\- ]+)"', cabeza)
    if not m:
        sys.exit(f"{path.name}: sin viewBox")
    p = m.group(1).split()
    return float(p[2]), float(p[3])


def convertir(svg, pdf):
    w, h = medida_svg(svg)
    win, hin = w / PX_PER_IN, h / PX_PER_IN
    # El SVG va inline y no dentro de un <img>: dentro de un <img> el documento
    # queda aislado y el @font-face embebido no se aplica.
    doc = (
        '<!DOCTYPE html><meta charset="utf-8"><style>'
        f"@page {{ size: {win:.4f}in {hin:.4f}in; margin: 0; }}"
        "html,body { margin:0; padding:0; }"
        f"svg {{ display:block; width:{win:.4f}in; height:{hin:.4f}in; }}"
        "</style>" + svg.read_text(encoding="utf-8", errors="ignore")
    )
    pdf.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        tmp = pathlib.Path(td) / "page.html"
        tmp.write_text(doc, encoding="utf-8")
        r = subprocess.run(
            [
                "google-chrome", "--headless", "--disable-gpu", "--no-sandbox",
                "--no-pdf-header-footer",
                "--run-all-compositor-stages-before-draw",
                "--virtual-time-budget=10000",
                f"--print-to-pdf={pdf}", tmp.as_uri(),
            ],
            capture_output=True, text=True, timeout=180,
        )
    if not pdf.exists():
        print(r.stderr[-1500:], file=sys.stderr)
        sys.exit(f"fallo la conversion de {svg.name}")
    return win, hin


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-f", "--forzar", action="store_true",
                    help="reconvertir aunque el PDF este al dia")
    ap.add_argument("-l", "--listar", action="store_true",
                    help="mostrar el mapeo y salir")
    args = ap.parse_args()

    entradas = leer_conf()
    faltantes = [(s, n) for s, _, n in entradas if not s.exists()]
    for svg, n in faltantes:
        print(f"  AVISO {CONF.name}:{n}: no existe {svg.name}", file=sys.stderr)

    hechos = 0
    for svg, pdf, _ in entradas:
        if not svg.exists():
            continue
        al_dia = pdf.exists() and pdf.stat().st_mtime >= svg.stat().st_mtime
        if args.listar:
            print(f"  [{'ok ' if al_dia else 'pend'}] {svg.name}"
                  f"  ->  figs/{pdf.relative_to(FIGS)}")
            continue
        if al_dia and not args.forzar:
            continue
        if svg.suffix.lower() != ".svg":
            pdf.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(svg, pdf)   # copy2 conserva el mtime: queda "al dia"
            print(f"  {svg.name}  ->  figs/{pdf.relative_to(FIGS)}   (copia)")
            hechos += 1
            continue
        win, hin = convertir(svg, pdf)
        print(f"  {svg.name}  ->  figs/{pdf.relative_to(FIGS)}"
              f"   ({win:.1f} x {hin:.1f} in, {pdf.stat().st_size / 1024:.0f} KB)")
        hechos += 1

    if not args.listar:
        print(f"{hechos} figura(s) convertida(s)"
              + (", nada que hacer" if not hechos else ""))


if __name__ == "__main__":
    main()
