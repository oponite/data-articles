# Doofenshmirtz audit inputs

The CSV files and Lana program are the reviewed inputs for the published article.
The site renders the notebook's saved outputs without rerunning it.

To rerun source validation, retain the original local snapshot in
`drafts/doofenshmirtz-corpus/`, including `github-transcripts/raw/` and
`github-transcripts/full-inventory-review/`. The manifest records source hashes
and screening-record paths; the notebook verifies them before analysis.
The full transcripts and screening records are not bundled with the site.

Transcript source: https://github.com/captainsidd/phineas-ferb/tree/b49d21b85f5ae0725a68d414b62f34b069330239

From the repository root, with Python dependencies installed and Lana 4.0.0 on PATH:

```sh
.venv/bin/jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=120 website/doofenshmirtz-informational-audit.ipynb
quarto render website
```
