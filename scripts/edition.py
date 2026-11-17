#!/usr/bin/env python3
"""Validate and render the current Morning Brief edition from content/edition.json."""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "content" / "edition.json"
SECTION_IDS = ("riesgo", "gestion", "xr", "campus", "aprender")
EDITION_ID = re.compile(r"^\d{4}-\d{2}-\d{2}-\d{3}$")


class EditionError(Exception):
    pass


def nonempty(value, label):
    if not isinstance(value, str) or not value.strip():
        raise EditionError(f"{label}: debe ser texto no vacío")
    return value.strip()


def validate(path=SOURCE):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise EditionError(f"No existe {path}. Copia content/edition.example.json a content/edition.json.")
    except json.JSONDecodeError as exc:
        raise EditionError(f"JSON inválido en línea {exc.lineno}, columna {exc.colno}: {exc.msg}")

    if not isinstance(data, dict):
        raise EditionError("La edición debe ser un objeto JSON.")

    if data.get("schema_version") != 1:
        raise EditionError("schema_version debe ser 1.")
    edition_id = nonempty(data.get("id"), "id")
    if not EDITION_ID.fullmatch(edition_id):
        raise EditionError("id debe tener el formato AAAA-MM-DD-NNN, por ejemplo 2026-10-23-004.")
    try:
        parsed_date = date.fromisoformat(nonempty(data.get("date"), "date"))
    except ValueError:
        raise EditionError("date debe tener el formato AAAA-MM-DD y ser una fecha válida.")
    if edition_id[:10] != parsed_date.isoformat():
        raise EditionError("Los primeros diez caracteres de id deben coincidir con date.")

    for key in ("label", "title", "dek", "footer"):
        nonempty(data.get(key), key)

    sections = data.get("sections")
    if not isinstance(sections, list) or len(sections) != len(SECTION_IDS):
        raise EditionError("sections debe incluir exactamente las cinco secciones editoriales.")
    seen_ids = set()
    for index, (section, expected_id) in enumerate(zip(sections, SECTION_IDS), start=1):
        if not isinstance(section, dict) or section.get("id") != expected_id:
            raise EditionError(f"Sección {index}: se esperaba id '{expected_id}'.")
        nonempty(section.get("title"), f"Sección {index}: title")
        items = section.get("items")
        if not isinstance(items, list) or not items:
            raise EditionError(f"Sección {index}: items debe contener al menos una pieza.")
        for item_index, item in enumerate(items, start=1):
            where = f"Sección {index}, pieza {item_index}"
            if not isinstance(item, dict):
                raise EditionError(f"{where}: debe ser un objeto.")
            for key in ("tag", "headline", "summary", "analysis"):
                nonempty(item.get(key), f"{where}: {key}")
            facts = item.get("facts", [])
            if not isinstance(facts, list) or any(not isinstance(x, str) or not x.strip() for x in facts):
                raise EditionError(f"{where}: facts debe ser una lista de textos no vacíos.")
            if expected_id != "aprender" and not facts:
                raise EditionError(f"{where}: agrega al menos un hecho para separar evidencia de análisis.")
            if expected_id != "aprender":
                source = item.get("source")
                if not isinstance(source, dict):
                    raise EditionError(f"{where}: source requiere label y url.")
                nonempty(source.get("label"), f"{where}: source.label")
                url = nonempty(source.get("url"), f"{where}: source.url")
                parsed = urlparse(url)
                if parsed.scheme != "https" or not parsed.netloc:
                    raise EditionError(f"{where}: source.url debe ser una URL HTTPS completa.")
            item_id = item.get("id")
            if item_id is not None:
                item_id = nonempty(item_id, f"{where}: id")
                if item_id in seen_ids:
                    raise EditionError(f"{where}: id duplicado '{item_id}'.")
                seen_ids.add(item_id)
    return data


def esc(value):
    return html.escape(str(value), quote=True)


def render(data):
    nav = "".join(f'<a href="#{esc(s["id"])}">{esc(s["title"])}</a>' for s in data["sections"])
    sections_html = []
    for section in data["sections"]:
        cards = []
        for item in section["items"]:
            facts = "".join(f'<p class="fact"><b>Hecho:</b> {esc(fact)}</p>' for fact in item.get("facts", []))
            source = item.get("source")
            source_html = (f'<a href="{esc(source["url"])}" target="_blank" rel="noopener noreferrer">'
                           f'{esc(source["label"])} ↗</a>') if source else ""
            cards.append(
                '<article class="card">'
                f'<div class="tag">{esc(item["tag"])}</div>'
                f'<h3>{esc(item["headline"])}</h3>'
                f'<p>{esc(item["summary"])}</p>{facts}'
                f'<p class="analysis"><b>Lectura editorial:</b> {esc(item["analysis"])}</p>'
                f'{source_html}</article>'
            )
        sections_html.append(
            f'<section id="{esc(section["id"])}"><h2>{esc(section["title"])}</h2>'
            + "".join(cards) + "</section>"
        )
    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(data["title"])} | The Morning Brief</title>
<style>
:root{{--bg:#121215;--panel:#232327;--text:#f4f0ed;--muted:#bcb4b2;--red:#ed4746;--yellow:#f5c84c;--line:#454047}}
*{{box-sizing:border-box}}body{{background:var(--bg);color:var(--text);margin:0;font:16px/1.6 system-ui,sans-serif}}
main{{max-width:960px;margin:auto;padding:24px}}header{{border-bottom:1px solid var(--line);padding:18px 0;color:var(--yellow);font-size:13px;letter-spacing:.12em}}
h1{{font-size:clamp(54px,11vw,105px);line-height:.93;letter-spacing:-.06em;margin:50px 0 20px}}h1 span{{color:var(--red)}}
h2{{font-size:30px;border-bottom:1px solid #48444a;padding-bottom:10px}}h3{{font-size:24px;line-height:1.22}}
.lead{{font-size:20px;color:#ddd}}.grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:18px}}
.card{{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:22px;margin:16px 0}}
.tag{{color:var(--yellow);letter-spacing:.1em;font-size:11px;font-weight:bold}}a{{color:var(--yellow);text-underline-offset:3px}}
.fact{{border-left:3px solid var(--red);padding-left:12px}}.analysis{{color:#ddd}}
footer{{border-top:1px solid #444;margin-top:55px;padding:25px 0;color:var(--muted);font-size:13px}}
nav{{display:flex;flex-wrap:wrap;gap:8px 16px}}nav a{{font-size:13px}}
@media(max-width:720px){{.grid{{grid-template-columns:1fr}}h1{{margin-top:35px}}.card{{padding:18px}}main{{padding:18px}}}}
</style></head><body><main>
<header>THE MORNING BRIEF · {esc(data["label"])}</header>
<h1>WHAT<br><span>MATTERS.</span></h1>
<p class="lead">{esc(data["dek"])}</p><nav aria-label="Secciones">{nav}</nav>
{"".join(sections_html)}
<footer>{esc(data["footer"])}</footer>
</main></body></html>"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate", help="Valida content/edition.json.")
    build = sub.add_parser("build", help="Genera latest/index.html.")
    build.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    try:
        data = validate()
        if args.command == "validate":
            print(f"Edición válida: {data['id']}")
            return 0
        target = args.output_dir / "latest" / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render(data), encoding="utf-8")
        print(f"Vista generada: {target}")
        return 0
    except EditionError as exc:
        print(f"Error de edición: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
