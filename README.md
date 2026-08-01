# data-articles

<!-- plain-english:start -->
> **1-sentence Summary:** This repo is a Quarto/Jupyter website for data-driven articles, with source notebooks and rendered GitHub Pages output kept together.
<!-- plain-english:end -->


https://oponite.github.io/data-articles/

`data-articles` is a website featuring a collection of data-driven articles at the intersection of sports, finance, math, and Python.

The site is built with [Quarto](https://quarto.org/) and Jupyter notebooks. Editable website sources live in `website/`, the Quarto configuration remains at the repository root, and the rendered website is committed to `docs/` for GitHub Pages publishing.

## Repository Structure (core components)

- `website/`: editable notebooks, article index, and stylesheet.
- `data/`: local inputs and cached datasets used by the notebooks.
- `figures/`: generated figures used by the notebooks.
- `docs/`: rendered Quarto website output for publishing.
- `_quarto.yml`: Quarto website configuration.
- `requirements.txt`: Python dependencies.
