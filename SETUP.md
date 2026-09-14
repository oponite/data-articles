# Publishing Setup

## 1. Render Notebook

From the repo root:

```bash
quarto render website/notebook-name.md
```

Quarto executes the notebook and writes the rendered HTML into `docs/`.

## 2. Render Site

Render the Quarto website with:

```bash
quarto render website
```

This renders every file listed in `_quarto.yml` and refreshes `docs/`.

## 3. Commit source and rendered output

```
git add website/notebook-name.ipynb docs/
git commit -m "YOUR MESSSAGE HERE"
git push
```

## Data Notes

The `data/` directory contains local inputs and cached datasets used by the notebooks. Keeping these files locally avoids unnecessary downloads and makes reruns faster; notebooks can refresh missing data when their source APIs are available.