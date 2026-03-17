# Sample Datasets

Static datasets for educational illustration. Both files cover the same
period and share identical date indices — they can be merged directly.

---

## Files

### `fund_returns.csv`

Monthly total returns (%) for three anonymised Indian open-ended equity funds.

| Column | Archetype | Character |
|--------|-----------|-----------|
| `Fund_A` | Momentum | High-conviction, concentrated; strong upside but elevated crash risk |
| `Fund_B` | Quality | Low-volatility, quality-oriented; best downside protection in the set |
| `Fund_C` | Market beta | Large-cap blend; returns largely explained by systematic factor exposure |

- **Period:** January 2015 – December 2020 (72 months)
- **Frequency:** Monthly, month-end
- **Units:** Total return, percent (e.g. `2.5` = +2.5%)
- **Source:** Publicly available NAV data. Fund identities withheld for
  educational use. Returns are actual published figures.
- **Notable events covered:** Demonetisation (Nov 2016), IL&FS crisis
  (Sep–Oct 2018), COVID crash and recovery (Mar–Dec 2020)

---

### `nifty_monthly_returns.csv`

Monthly returns (%) for nine NSE factor and market-cap indices.

| Column | Index |
|--------|-------|
| `nifty100` | NIFTY 100 — large-cap benchmark |
| `nifty_midcap150` | Nifty Midcap 150 |
| `nifty_smallcap250` | Nifty Smallcap 250 |
| `nifty500_value50` | NIFTY500 Value 50 — value factor |
| `nifty100_quality30` | NIFTY100 Quality 30 — quality factor, large-cap |
| `nifty_midcap150_quality50` | Nifty Midcap150 Quality 50 |
| `nifty_smallcap250_quality50` | Nifty Smallcap250 Quality 50 |
| `nifty200_momentum30` | NIFTY200 Momentum 30 — momentum factor |
| `nifty_midcap150_momentum50` | Nifty Midcap150 Momentum 50 |

- **Period:** January 2015 – December 2020 (72 months)
- **Frequency:** Monthly, month-end (resampled from daily index values)
- **Units:** Percentage return (month-on-month, from month-end prices)
- **Source:** NSE India published index values. Derived monthly returns
  computed for educational use.

---

## Usage

```python
from src.data import load_fund_sample, load_nifty_sample

funds = load_fund_sample()          # returns DataFrame, 72 x 3
nifty = load_nifty_sample()         # returns DataFrame, 72 x 9

# Both share the same DatetimeIndex — merge directly
import pandas as pd
combined = pd.concat([funds, nifty], axis=1)
```

---

## Notes

- These are **frozen datasets** — they will not be updated.
- The Invespar Indian Factor Library (live, updated) is accessed via
  the `indiafactorlibrary` package — see `data/invespar/README.md`.
- For analysis requiring data beyond Dec 2020, use the live factor
  library and source current index data independently.
