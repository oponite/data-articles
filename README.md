# data-articles

https://oponite.github.io/data-articles/

`data-articles` is a website featuring collection of data-driven articles at the intersection of sports, finance, math, and Python.

The site is built with [Quarto](https://quarto.org/) and Jupyter notebooks. Source notebooks and article files live in the repository, while the rendered website is committed to `docs/` for GitHub Pages publishing.

## Current Articles

- [Articles index]((https://oponite.github.io/data-articles/articles.html))
- [What makes a basketball team win?]([nba-scoring.ipynb](https://oponite.github.io/data-articles/nba-scoring.html))

## Repository Structure

- `index.ipynb`: homepage source.
- `articles.qmd`: article index.
- `nba-scoring.ipynb`: NBA team performance analysis notebook/article.
- `data/nba/`: local CSV inputs used by the NBA notebook.
- `docs/`: rendered Quarto website output for publishing.
- `_quarto.yml`: Quarto website configuration.
- `requirements.txt`: Python dependencies.

## Run Locally

Create a virtual environment, install the Python dependencies, and start the Quarto preview server:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
quarto preview
```

## Render the Site

Render the Quarto website with:

```bash
quarto render
```

Rendered HTML is written to `docs/` because `_quarto.yml` sets:

```yaml
project:
  type: website
  output-dir: docs
```

## Data Notes

The NBA CSV files in `data/nba/` are kept locally so the notebook does not need to download NBA.com game logs on every run. If the local files are missing, the notebook can fetch the data with `nba_api` and save it back to disk.

## Publishing

GitHub Pages is configured to publish from the `docs/` directory.
