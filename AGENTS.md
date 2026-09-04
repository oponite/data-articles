# data-articles

Quarto/Jupyter website for data-driven articles. Sources live in `website/`, rendered site is committed to `docs/` for GitHub Pages.
Live site: https://oponite.github.io/data-articles/

## Developer commands

- **Setup Python env**
  ```bash
  python -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  ```
  Kernel used in notebooks is `.venv` (Python 3.14.6). `requirements.txt` contains: jupyter, ipykernel, matplotlib, nba_api, numpy, pandas, scikit-learn, scipy, statsmodels, yfinance.

- **Preview locally**
  ```bash
  quarto preview website
  ```
  Serves the site from the root `_quarto.yml` config.

- **Render site**
  ```bash
  quarto render website
  ```
  Writes HTML to `docs/` . Output dir is set in `_quarto.yml`:
  ```yaml
  project:
    type: website
    output-dir: docs
  ```
  Render list is explicit in `_quarto.yml`:
  - `website/index.ipynb`
  - `website/articles.qmd`
  - `website/nba-scoring.ipynb`
  - `website/btc-accumulation.ipynb`

GitHub Pages publishes from `docs/`.

## Project structure

- `website/` — editable notebooks and qmd, article index, `styles.css`
- `data/` — local inputs and cached datasets used by notebooks
- `figures/` — generated figures referenced by notebooks
- `docs/` — rendered Quarto output, committed for publishing
- `drafts/` — working notebooks not included in site build
- `_quarto.yml` — root Quarto website config
- `requirements.txt` — Python dependencies
- `SETUP.md`, `README.md` — human setup notes

## Conventions & gotchas

- Config is at repository root, not in `website/`. Sources are in `website/`.
- Do not commit Quarto cache: `.gitignore` excludes `/.quarto/`, `b_*.ipynb`, `**/*.quarto_ipynb`.
- Notebooks can refresh missing data from source APIs; `data/` is kept locally to avoid re-downloads and speed reruns.
- `website/articles.qmd` is the manual article index; add new articles there and update `_quarto.yml` render list if needed.
- No test suite or CI workflows are present in the repo.
