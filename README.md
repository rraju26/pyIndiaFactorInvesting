# pyIndiaFactorInvesting

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/rraju26/pyIndiaFactorInvesting/main?urlpath=lab)
[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/rraju26/pyIndiaFactorInvesting/blob/main/notebooks/factor_based_analysis.ipynb)

<!-- One-sentence description -->

---

## Overview

<!-- What this repo is, who it is for, and what they will learn -->

---

## Repository Structure

```
pyIndiaFactorInvesting/
├── notebooks/          # Numbered Jupyter notebooks (run in sequence)
├── src/                # Reusable Python modules
│   ├── data.py         # Data loading and alignment utilities
│   ├── factors.py      # Factor computations and regressions
│   └── visualise.py    # Chart helpers
├── data/
│   ├── sample/         # Anonymised sample datasets (committed)
│   └── invespar/       # Raw Invespar downloads (git-ignored)
├── requirements.txt
├── environment.yml
├── pyproject.toml      # uv project definition + dependencies (PEP 621)
└── uv.lock             # pinned versions for reproducible uv installs
```

---

## Notebooks

| # | Notebook | Topic |
|---|----------|-------|
| 00 | `00_indian_market_puzzles.ipynb` | Five empirical puzzles in Indian market data — entry point, no theory |
| 01 | `01_factor_zoo.ipynb` | What is a factor and why does it persist? MPT and CAPM as context |
| 02 | `02_factor_construction.ipynb` | Building SMB, HML, WML for India using the Invespar Factor Library |
| 03 | `03_factor_models.ipynb` | Four and five-factor models — evidence from Indian equities |
| 04 | `04_momentum_deep_dive.ipynb` | Momentum variants, crash risk, and implementation in India |
| 05 | `05_fund_decomposition.ipynb` | Factor attribution of three Indian equity funds |
| 06 | `06_hypothesis_testing.ipynb` | Testing your own hypothesis with Indian factor data |

---

## Going Deeper

These notebooks are not required reading but reward the curious reader.

| Notebook | Topic |
|----------|-------|
| `intro_to_ap.ipynb` | Regression mechanics, CAPM, FF3/4/5/6 — full technical treatment |
| `intro_multicoll.ipynb` | Multicollinearity in asset pricing models |

---

## Data Sources

<!-- Invespar Indian Factor Library URL and citation -->

---

## Setup

### Option 1 — Binder / Colab (no installation)

<!-- Instructions -->

### Option 2 — Conda (recommended for local use)

```bash
conda env create -f environment.yml
conda activate pyIndiaFactorInvesting
jupyter notebook
```

### Option 3 — pip

```bash
pip install -r requirements.txt
jupyter notebook
```

### Option 4 — uv

[uv](https://docs.astral.sh/uv/) provisions the Python version *and* the dependencies in one step. After [installing uv](https://docs.astral.sh/uv/getting-started/installation/):

```bash
uv sync              # creates .venv with Python 3.11 + locked dependencies
uv run jupyter lab
```

uv reads `.python-version` and `pyproject.toml`, so there is nothing else to configure. To change a dependency, edit `pyproject.toml` (or run `uv add <pkg>`), then commit the regenerated `uv.lock` so everyone resolves to the same versions.

---

## src Module Reference

<!-- Brief description of each public function in data.py, factors.py, visualise.py -->

---

## References

1. Fama, E. F., & French, K. R. (1993). Common risk factors in the returns on stocks and bonds. *Journal of Financial Economics, 33*(1), 3–56.
2. Fama, E. F., & French, K. R. (2015). A five-factor asset pricing model. *Journal of Financial Economics, 116*(1), 1–22.
3. Carhart, M. M. (1997). On persistence in mutual fund performance. *The Journal of Finance, 52*(1), 57–82.
4. Raju, R. (2022). Four and Five-Factor Models in the Indian Equities Market. *SSRN eLibrary*.
5. Raju, R. (2022). A Five-Factor Asset Pricing Model: Preliminary Evidence from India. *SSRN eLibrary*.
6. Agarwalla, S. K., Jacob, J., & Varma, J. R. (2013). Four factor model in Indian equities market. *Indian Institute of Management Ahmedabad Working Paper*.
7. Data: [Invespar Indian Factor Library](http://invespar.com/research)

---

## Contributing

<!-- Suggestions welcome — open an issue or PR -->

## License

<!-- License type -->
