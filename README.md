# El Sibarita

Web de comida amateur, publicada en [sibarita.xyz](https://sibarita.xyz). Recetas en Markdown, clasificadas por **origen**, **aporte nutricional** (carbohidrato, proteína, lípido, fibra) y **comida del día** (desayuno, merienda, almuerzo, cena). Sitio generado con [Zensical](https://zensical.org/) (configuración compatible con MkDocs Material).

## Uso

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/zensical serve      # http://127.0.0.1:8000
```

## Estructura

- `docs/recetas/`: una receta por archivo, con las etiquetas en el front matter.
- `plantillas/receta.md`: plantilla para nuevas recetas.
- `docs/contribuir.md`: convenciones y vocabulario de etiquetas.
- `.github/workflows/deploy.yml`: publica en GitHub Pages al hacer push a `main`.
- `docs/CNAME`: dominio propio (`sibarita.xyz`) para GitHub Pages.
- `docs/resources/`: imágenes del sitio (`banner.webp` es la versión liviana del banner).
