"""Tests de estructura de las recetas.

Verifican las reglas de `docs/contribuir.md` y de `plantillas/receta.md`:
front matter, vocabulario de etiquetas, secciones, tabla nutricional y
registro en `mkdocs.yml` y en `docs/recetas/index.md`.
"""

import re
from pathlib import Path

import pytest
import yaml

RAIZ = Path(__file__).resolve().parent.parent
DIR_RECETAS = RAIZ / "docs" / "recetas"
INDICE = DIR_RECETAS / "index.md"
MKDOCS = RAIZ / "mkdocs.yml"

NUTRIENTES = {"Carbohidrato", "Proteína", "Lípido", "Fibra"}
COMIDAS = {"Desayuno", "Merienda", "Almuerzo", "Cena"}

SECCIONES = ["Ingredientes", "Preparación", "Valor nutricional", "Notas"]
FILAS_NUTRICION = ["Energía", "Carbohidratos", "Proteínas", "Grasas", "Fibra"]

SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*\.md$")
LINEA_INDICE = re.compile(r"^- \[(?P<nombre>[^\]]+)\]\((?P<archivo>[^)]+)\): (?P<detalle>.+)$")

ARCHIVOS = sorted(p for p in DIR_RECETAS.glob("*.md") if p.name != "index.md")


def _dividir(texto):
    """Devuelve (front matter parseado, cuerpo)."""
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", texto, re.DOTALL)
    assert m, "falta el front matter (bloque --- al inicio)"
    return yaml.safe_load(m.group(1)) or {}, m.group(2)


def _receta(path):
    return _dividir(path.read_text(encoding="utf-8"))


def _tags_por_dimension(tags):
    por_dim = {}
    for tag in tags:
        assert "/" in tag, f"etiqueta sin dimensión: {tag!r} (usar Dimensión/Valor)"
        dim, valor = tag.split("/", 1)
        por_dim.setdefault(dim, []).append(valor)
    return por_dim


def _entradas_nav():
    """Archivos de recetas listados en el nav de mkdocs.yml."""
    config = yaml.safe_load(MKDOCS.read_text(encoding="utf-8"))

    def aplanar(nodo):
        if isinstance(nodo, str):
            yield nodo
        elif isinstance(nodo, list):
            for x in nodo:
                yield from aplanar(x)
        elif isinstance(nodo, dict):
            for x in nodo.values():
                yield from aplanar(x)

    rutas = [r for r in aplanar(config["nav"]) if r.startswith("recetas/")]
    return [r.removeprefix("recetas/") for r in rutas if r != "recetas/index.md"]


def _entradas_indice():
    """Mapa archivo -> detalle ("Origen · nutrientes · comidas") del índice."""
    entradas = {}
    for linea in INDICE.read_text(encoding="utf-8").splitlines():
        m = LINEA_INDICE.match(linea)
        if m:
            archivo = m.group("archivo")
            assert archivo not in entradas, f"{archivo} figura dos veces en el índice"
            entradas[archivo] = m.group("detalle")
    return entradas


def test_hay_recetas():
    assert ARCHIVOS, "no se encontró ninguna receta en docs/recetas/"


@pytest.mark.parametrize("path", ARCHIVOS, ids=lambda p: p.name)
class TestReceta:
    def test_nombre_de_archivo(self, path):
        assert SLUG.match(path.name), (
            f"{path.name}: usar minúsculas, números y guiones, sin tildes ni ñ"
        )

    def test_front_matter(self, path):
        meta, _ = _receta(path)
        assert isinstance(meta.get("title"), str) and meta["title"].strip(), "falta title"
        assert isinstance(meta.get("tags"), list) and meta["tags"], "faltan tags"

    def test_etiquetas(self, path):
        meta, _ = _receta(path)
        por_dim = _tags_por_dimension(meta["tags"])

        assert set(por_dim) <= {"Origen", "Nutriente", "Comida"}, (
            f"dimensiones desconocidas: {set(por_dim) - {'Origen', 'Nutriente', 'Comida'}}"
        )
        assert len(por_dim.get("Origen", [])) == 1, "debe tener exactamente un Origen/"

        for dim, validos in (("Nutriente", NUTRIENTES), ("Comida", COMIDAS)):
            valores = por_dim.get(dim, [])
            assert valores, f"debe tener al menos un {dim}/"
            assert set(valores) <= validos, (
                f"{dim}/ inválido: {sorted(set(valores) - validos)} "
                f"(permitidos: {sorted(validos)})"
            )

        assert len(meta["tags"]) == len(set(meta["tags"])), "hay etiquetas repetidas"

    def test_titulo_coincide(self, path):
        meta, cuerpo = _receta(path)
        h1 = re.findall(r"^# (.+)$", cuerpo, re.MULTILINE)
        assert len(h1) == 1, "debe haber exactamente un título '# ...'"
        assert h1[0].strip() == meta["title"].strip(), (
            f"el título '# {h1[0]}' no coincide con title: {meta['title']!r}"
        )

    def test_secciones_en_orden(self, path):
        _, cuerpo = _receta(path)
        encontradas = re.findall(r"^## (.+)$", cuerpo, re.MULTILINE)
        encontradas = [s.strip() for s in encontradas]
        assert encontradas == SECCIONES, (
            f"secciones esperadas {SECCIONES}, encontradas {encontradas}"
        )

    def test_porciones_y_tiempo(self, path):
        _, cuerpo = _receta(path)
        assert re.search(r"^\*\*Porciones:\*\* .+ · \*\*Tiempo:\*\* .+$", cuerpo, re.MULTILINE), (
            "falta la línea '**Porciones:** … · **Tiempo:** …'"
        )

    def test_ingredientes_y_pasos(self, path):
        _, cuerpo = _receta(path)
        ingredientes = _seccion(cuerpo, "Ingredientes")
        preparacion = _seccion(cuerpo, "Preparación")
        assert re.search(r"^- \S", ingredientes, re.MULTILINE), "Ingredientes sin items '- …'"
        assert re.search(r"^1\. \S", preparacion, re.MULTILINE), "Preparación sin pasos '1. …'"

    def test_tabla_nutricional(self, path):
        _, cuerpo = _receta(path)
        tabla = _seccion(cuerpo, "Valor nutricional")
        filas = [
            [c.strip() for c in linea.strip().strip("|").split("|")]
            for linea in tabla.splitlines()
            if linea.strip().startswith("|")
        ]
        assert len(filas) >= 2, "no se encontró la tabla"
        encabezado, separador, datos = filas[0], filas[1], filas[2:]

        assert len(encabezado) == 4, "la tabla debe tener 4 columnas (nombre + 3)"
        assert re.match(r"^Por (porción|unidad)\b", encabezado[1]), (
            "la primera columna de datos debe ser 'Por porción …' o 'Por unidad …'"
        )
        assert encabezado[2] == "Por 100 g", "la segunda columna debe ser 'Por 100 g'"
        assert encabezado[3] == "Receta completa", "la tercera columna debe ser 'Receta completa'"
        assert all(set(c) <= set("-: ") for c in separador), "falta el separador de la tabla"

        assert [f[0] for f in datos] == FILAS_NUTRICION, (
            f"filas esperadas {FILAS_NUTRICION}, encontradas {[f[0] for f in datos]}"
        )
        for fila in datos:
            unidad = "kcal" if fila[0] == "Energía" else "g"
            for celda in fila[1:]:
                assert re.fullmatch(rf"\d+(\.\d{{3}})*(,\d+)? {unidad}", celda), (
                    f"{fila[0]}: valor mal formado {celda!r} "
                    f"(usar coma decimal y la unidad '{unidad}')"
                )

    def test_registrada_en_nav(self, path):
        assert path.name in _entradas_nav(), f"{path.name} falta en el nav de mkdocs.yml"

    def test_registrada_en_indice(self, path):
        assert path.name in _entradas_indice(), (
            f"{path.name} falta en docs/recetas/index.md"
        )

    def test_indice_coincide_con_etiquetas(self, path):
        meta, _ = _receta(path)
        por_dim = _tags_por_dimension(meta["tags"])
        detalle = _entradas_indice().get(path.name)
        assert detalle is not None, "no figura en el índice"

        partes = [p.strip() for p in detalle.split(" · ")]
        assert len(partes) == 3, f"formato esperado 'Origen · nutrientes · comidas': {detalle!r}"
        origen, nutrientes, comidas = partes

        assert origen == (por_dim.get("Origen") or [None])[0], (
            f"origen del índice {origen!r} != etiqueta {por_dim.get('Origen')}"
        )
        assert {n.strip() for n in nutrientes.split(",")} == {
            n.lower() for n in por_dim["Nutriente"]
        }, f"nutrientes del índice ({nutrientes}) no coinciden con las etiquetas"
        assert {c.strip() for c in comidas.split(",")} == {
            c.lower() for c in por_dim["Comida"]
        }, f"comidas del índice ({comidas}) no coinciden con las etiquetas"


def _seccion(cuerpo, nombre):
    m = re.search(rf"^## {re.escape(nombre)}\n(.*?)(?=^## |\Z)", cuerpo, re.MULTILINE | re.DOTALL)
    assert m, f"falta la sección '## {nombre}'"
    return m.group(1)


def test_nav_apunta_a_archivos_existentes():
    inexistentes = [r for r in _entradas_nav() if not (DIR_RECETAS / r).is_file()]
    assert not inexistentes, f"el nav lista archivos que no existen: {inexistentes}"


def test_indice_apunta_a_archivos_existentes():
    inexistentes = [a for a in _entradas_indice() if not (DIR_RECETAS / a).is_file()]
    assert not inexistentes, f"el índice lista archivos que no existen: {inexistentes}"


def test_nav_sin_duplicados():
    nav = _entradas_nav()
    assert len(nav) == len(set(nav)), "hay recetas repetidas en el nav"
