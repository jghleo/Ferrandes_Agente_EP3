#!/usr/bin/env python3
"""Convierte informe/Evaluacion_Pauta_EP3_Ferrandes.md a Word.

Uso: /tmp/opencode/venv/bin/python scripts/generar_evaluacion.py
"""
from __future__ import annotations

import re
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

RAIZ = Path(__file__).resolve().parent.parent
ORIGEN = RAIZ / "informe" / "Evaluacion_Pauta_EP3_Ferrandes.md"
DESTINO = RAIZ / "informe" / "Evaluacion_Pauta_EP3_Ferrandes.docx"
AZUL = RGBColor(0x1F, 0x4E, 0x79)


def limpiar(texto: str) -> str:
    texto = re.sub(r"`([^`]+)`", r"\1", texto)
    texto = texto.replace("**", "")
    return texto.strip()


def sombrear(celda, color: str) -> None:
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), color)
    celda._tc.get_or_add_tcPr().append(shd)


def anadir_inline(parrafo, texto: str, size: float = 9.0) -> None:
    """Aplica negrita a los segmentos **...** y monoespacio a `...`."""
    for parte in re.split(r"(\*\*[^*]+\*\*|`[^`]+`)", texto):
        if not parte:
            continue
        run = parrafo.add_run()
        if parte.startswith("**") and parte.endswith("**"):
            run.text = parte[2:-2]
            run.bold = True
        elif parte.startswith("`") and parte.endswith("`"):
            run.text = parte[1:-1]
            run.font.name = "DejaVu Sans Mono"
        else:
            run.text = parte
        run.font.size = Pt(size)


def anadir_tabla(doc, filas: list[list[str]]) -> None:
    if not filas:
        return
    anchos = [3.2, 7.2, 2.0, 2.0, 2.6][: len(filas[0])]
    tabla = doc.add_table(rows=1, cols=len(filas[0]))
    tabla.style = "Table Grid"
    tabla.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, texto in enumerate(filas[0]):
        celda = tabla.rows[0].cells[i]
        celda.text = ""
        anadir_inline(celda.paragraphs[0], texto, size=8.3)
        sombrear(celda, "D6E4F0")
        for run in celda.paragraphs[0].runs:
            run.bold = True
    for fila in filas[1:]:
        celdas = tabla.add_row().cells
        for i, texto in enumerate(fila):
            celdas[i].text = ""
            anadir_inline(celdas[i].paragraphs[0], texto, size=8.3)
    for fila in tabla.rows:
        for i, ancho in enumerate(anchos):
            fila.cells[i].width = Cm(ancho)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def main() -> None:
    lineas = ORIGEN.read_text(encoding="utf-8").splitlines()
    doc = Document()
    seccion = doc.sections[0]
    seccion.top_margin = Cm(1.4)
    seccion.bottom_margin = Cm(1.4)
    seccion.left_margin = Cm(1.6)
    seccion.right_margin = Cm(1.6)
    normal = doc.styles["Normal"]
    normal.font.name = "DejaVu Sans"
    normal.font.size = Pt(9)

    buf_tabla: list[list[str]] = []

    def volcar_tabla() -> None:
        if buf_tabla:
            anadir_tabla(doc, buf_tabla[:1] + buf_tabla[2:])
            buf_tabla.clear()

    for linea in lineas + [""]:
        if linea.strip().startswith("|") and linea.strip().endswith("|"):
            celdas = [c.strip() for c in linea.strip().strip("|").split("|")]
            if not all(re.fullmatch(r":?-{3,}:?", c) for c in celdas):
                buf_tabla.append(celdas)
            continue
        volcar_tabla()
        if not linea.strip():
            continue
        if linea.startswith("# "):
            p = doc.add_paragraph()
            p.alignment = 1
            r = p.add_run(limpiar(linea[2:]))
            r.bold = True
            r.font.size = Pt(17)
            r.font.color.rgb = AZUL
        elif linea.startswith("## "):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(9)
            r = p.add_run(limpiar(linea[3:]))
            r.bold = True
            r.font.size = Pt(12)
            r.font.color.rgb = AZUL
        elif linea.startswith("### "):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(6)
            r = p.add_run(limpiar(linea[4:]))
            r.bold = True
            r.font.size = Pt(10)
            r.font.color.rgb = AZUL
        elif linea.startswith("> "):
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(0.5)
            anadir_inline(p, linea[2:], size=8.8)
            for r in p.runs:
                r.italic = True
        elif re.match(r"^\s*[-*] ", linea):
            p = doc.add_paragraph(style="List Bullet")
            anadir_inline(p, re.sub(r"^\s*[-*] ", "", linea))
        elif re.match(r"^\s*\d+\. ", linea):
            p = doc.add_paragraph(style="List Number")
            anadir_inline(p, re.sub(r"^\s*\d+\. ", "", linea))
        else:
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(3)
            anadir_inline(p, linea)

    doc.save(DESTINO)
    print("Evaluación generada:", DESTINO)


if __name__ == "__main__":
    main()
