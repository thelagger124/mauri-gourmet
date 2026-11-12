"""Genera la sección "Últimas recetas" de la home.

Ordena las recetas por la fecha de su primer commit en git (las que todavía
no están commiteadas cuentan como nuevas) y reescribe el bloque de
`docs/index.md` delimitado por los marcadores ULTIMAS. Es idempotente.

Uso: python scripts/ultimas.py [cantidad]
"""

import re
import subprocess
import sys
import time
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parent.parent
DIR_RECETAS = RAIZ / "docs" / "recetas"
INDEX = RAIZ / "docs" / "index.md"

CANTIDAD = 6
INICIO = "<!-- ULTIMAS:INICIO (generado por scripts/ultimas.py, no editar a mano) -->"
FIN = "<!-- ULTIMAS:FIN -->"
BLOQUE = re.compile(re.escape(INICIO) + r".*?" + re.escape(FIN), re.DOTALL)


def fecha_alta(path):
    """Timestamp del commit que agregó el archivo; ahora si todavía no existe en git."""
    salida = subprocess.run(
        ["git", "log", "--follow", "--diff-filter=A", "--format=%at", "--", str(path)],
        cwd=RAIZ, capture_output=True, text=True, check=True,
    ).stdout.split()
    return int(salida[-1]) if salida else int(time.time())


def leer(path):
    m = re.match(r"^---\n(.*?)\n---\n", path.read_text(encoding="utf-8"), re.DOTALL)
    meta = yaml.safe_load(m.group(1)) if m else {}
    por_dim = {}
    for tag in meta.get("tags", []):
        dim, _, valor = tag.partition("/")
        por_dim.setdefault(dim, []).append(valor)
    origen = (por_dim.get("Origen") or [""])[0]
    comidas = ", ".join(c.lower() for c in por_dim.get("Comida", []))
    return meta["title"], origen, comidas


def ultimas(cantidad=CANTIDAD):
    """Devuelve [(archivo, título, origen, comidas)], de la más nueva a la más vieja."""
    recetas = sorted(
        (p for p in DIR_RECETAS.glob("*.md") if p.name != "index.md"),
        key=lambda p: (-fecha_alta(p), p.name),
    )
    return [(p.name, *leer(p)) for p in recetas[:cantidad]]


def render(recetas):
    tarjetas = []
    for archivo, titulo, origen, comidas in recetas:
        detalle = " · ".join(x for x in (origen, comidas) if x)
        tarjetas.append(f"-   **[{titulo}](recetas/{archivo})**\n\n    {detalle}")
    cuerpo = "\n\n".join(tarjetas)
    return f'{INICIO}\n<div class="grid cards" markdown>\n\n{cuerpo}\n\n</div>\n{FIN}'


def actualizar(texto, recetas):
    assert BLOQUE.search(texto), "faltan los marcadores ULTIMAS en docs/index.md"
    return BLOQUE.sub(lambda _: render(recetas), texto)


def main():
    cantidad = int(sys.argv[1]) if len(sys.argv) > 1 else CANTIDAD
    texto = INDEX.read_text(encoding="utf-8")
    nuevo = actualizar(texto, ultimas(cantidad))
    if nuevo != texto:
        INDEX.write_text(nuevo, encoding="utf-8")
        print("docs/index.md actualizado")
    else:
        print("docs/index.md ya estaba al día")


if __name__ == "__main__":
    main()
