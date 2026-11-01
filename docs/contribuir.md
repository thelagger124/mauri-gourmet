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

## Probar en local

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/zensical serve
```
