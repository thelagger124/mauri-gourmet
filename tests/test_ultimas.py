"""Tests del generador de "Últimas recetas" (scripts/ultimas.py)."""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

import ultimas  # noqa: E402


def test_la_home_tiene_los_marcadores():
    texto = ultimas.INDEX.read_text(encoding="utf-8")
    assert texto.count(ultimas.INICIO) == 1 and texto.count(ultimas.FIN) == 1


def test_render_arma_tarjetas():
    bloque = ultimas.render([("chipa.md", "Chipa", "Paraguay", "merienda")])
    assert "-   **[Chipa](recetas/chipa.md)**" in bloque
    assert "    Paraguay · merienda" in bloque
    assert bloque.startswith(ultimas.INICIO) and bloque.endswith(ultimas.FIN)


def test_actualizar_reemplaza_solo_el_bloque_y_es_idempotente():
    recetas = [("chipa.md", "Chipa", "Paraguay", "merienda")]
    texto = f"antes\n{ultimas.INICIO}\nviejo\n{ultimas.FIN}\ndespués\n"
    nuevo = ultimas.actualizar(texto, recetas)
    assert "viejo" not in nuevo
    assert nuevo.startswith("antes\n") and nuevo.endswith("\ndespués\n")
    assert ultimas.actualizar(nuevo, recetas) == nuevo


def test_ultimas_respeta_la_cantidad():
    assert len(ultimas.ultimas(3)) == 3
