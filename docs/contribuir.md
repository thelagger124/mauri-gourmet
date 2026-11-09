# Contribuir

## Agregar una receta

1. Copiá `plantillas/receta.md` a `docs/recetas/<nombre-en-minusculas-con-guiones>.md`.
2. Completá el front matter con las etiquetas (ver abajo) y el contenido.
3. Agregala a `nav` en `mkdocs.yml` y a la lista de [Recetas](recetas/index.md).

## Vocabulario de etiquetas

Cada etiqueta lleva el prefijo de su dimensión: `Dimensión/Valor`.

| Dimensión | Valores | Cantidad |
|---|---|---|
| `Origen/` | Libre: país o región (`Origen/Italia`) | una |
| `Nutriente/` | `Carbohidrato`, `Proteína`, `Lípido`, `Fibra` | una o más |
| `Comida/` | `Desayuno`, `Merienda`, `Almuerzo`, `Cena` | una o más |

Respetá mayúsculas y tildes: `Proteína` y `proteina` serían etiquetas distintas.

## Tests

Un test de estructura (`tests/test_recetas.py`) revisa que cada receta tenga el front matter, las etiquetas del vocabulario, las secciones y la tabla nutricional, y que esté registrada en `mkdocs.yml` y en el índice. También corre antes de publicar el sitio: si falla, no se publica.

```bash
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/pytest
```

## Probar en local

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/zensical serve
```
