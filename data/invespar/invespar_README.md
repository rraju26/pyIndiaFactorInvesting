# Invespar Indian Factor Library

Factor data is accessed live via the `indiafactorlibrary` Python package.
No files are stored in this directory.

## Installation

```bash
pip install indiafactorlibrary
```

## Available factors

| Column | Factor |
|--------|--------|
| `MKT` | Market excess return |
| `MF` | Market factor (raw) |
| `SMB5` | Small Minus Big (size) |
| `HML` | High Minus Low (value) |
| `RMW` | Robust Minus Weak (profitability) |
| `CMA` | Conservative Minus Aggressive (investment) |
| `WML` | Winners Minus Losers (momentum) |
| `RF` | Risk-free rate |

- **Frequency:** Monthly
- **Coverage:** October 2006 – present (updated regularly)
- **Source:** [Invespar Data Library](http://invespar.com/research)

## Usage

```python
from src.data import load_invespar_factors

factors = load_invespar_factors(start='2015-01-01', end='2020-12-31')
```

## Reference

Raju, R. (2022). Four and Five-Factor Models in the Indian Equities Market.
*SSRN eLibrary*. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4054146
