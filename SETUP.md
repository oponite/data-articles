
## Run Locally

Create a virtual environment, install the Python dependencies, and start the Quarto preview server:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
quarto preview website
```

## Render the Site

Render the Quarto website with:

```bash
quarto render website
```

Rendered HTML is written to `docs/` because `_quarto.yml` sets:

```yaml
project:
  type: website
  output-dir: docs
```

## Data Notes

The `data/` directory contains local inputs and cached datasets used by the notebooks. Keeping these files locally avoids unnecessary downloads and makes reruns faster; notebooks can refresh missing data when their source APIs are available.

## Publishing

GitHub Pages is configured to publish from the `docs/` directory.

Quarto writes the generated site to `docs/` because `_quarto.yml` sets `output-dir: docs`.
