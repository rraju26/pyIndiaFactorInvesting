"""
src/data.py
===========
Data loading and alignment utilities for pyIndiaFactorInvesting.

All functions return clean DataFrames with a DatetimeIndex.
No raw price data is written to disk; only derived/aggregated outputs.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Repo-root anchor — all paths are relative to this
# ---------------------------------------------------------------------------
_REPO_ROOT = Path(__file__).resolve().parents[1]
_SAMPLE_DIR = _REPO_ROOT / "data" / "sample"

# ---------------------------------------------------------------------------
# Invespar / IndiaFactorLibrary
# ---------------------------------------------------------------------------

_FF6_COLUMNS = ["MKT", "SMB5", "HML", "RMW", "CMA", "WML", "RF", "MF"]
_FF6_RENAME: dict[str, str] = {}   # populated if library uses different names


def load_invespar_factors(
    start: Optional[str] = None,
    end: Optional[str] = None,
) -> pd.DataFrame:
    """Load Fama-French 6-factor data for India from the IndiaFactorLibrary.

    Wraps ``IndiaFactorLibrary().load_ff6()`` and returns a tidy monthly
    DataFrame ready for regression.

    Parameters
    ----------
    start : str, optional
        Inclusive start date, e.g. ``'2010-01-01'``.  If ``None``, all
        available history is returned.
    end : str, optional
        Inclusive end date, e.g. ``'2023-12-31'``.  If ``None``, all
        available history is returned.

    Returns
    -------
    pd.DataFrame
        Monthly factor returns with a ``DatetimeIndex`` (month-end).
        Columns: ``MKT, SMB5, HML, RMW, CMA, WML, RF, MF``.
        Values are in decimal form (0.01 = 1 %).

    Raises
    ------
    ImportError
        If ``indiafactorlibrary`` is not installed.
    ValueError
        If the loaded data is empty after date filtering.

    Example
    -------
    >>> factors = load_invespar_factors(start='2015-01-01', end='2022-12-31')
    >>> factors.shape
    (96, 8)
    """
    try:
        from indiafactorlibrary import IndiaFactorLibrary  # type: ignore
    except ImportError as exc:
        raise ImportError(
            "The 'indiafactorlibrary' package is required but not installed.\n"
            "Install it with:  pip install indiafactorlibrary"
        ) from exc

    ifl = IndiaFactorLibrary()
    raw: pd.DataFrame = ifl.load_ff6()

    # Normalise the index to a proper DatetimeIndex (month-end)
    if not isinstance(raw.index, pd.DatetimeIndex):
        raw.index = pd.to_datetime(raw.index)
    raw.index = raw.index.to_period("M").to_timestamp("M")
    raw.index.name = "Date"

    # Rename columns to the project standard if needed
    col_map = {c: c.upper() for c in raw.columns}
    # Common alternative names returned by the library
    col_map.update({
        "Mkt-RF": "MKT",
        "MKT-RF": "MKT",
        "Mkt_RF": "MKT",
        "Mom": "WML",
        "MOM": "WML",
        "SMB": "SMB5",
    })
    raw = raw.rename(columns=col_map)

    # Ensure the MF convenience column exists (MKT + RF = gross market)
    if "MF" not in raw.columns and "MKT" in raw.columns and "RF" in raw.columns:
        raw["MF"] = raw["MKT"] + raw["RF"]

    # Keep only standard columns that exist in the loaded data
    available = [c for c in _FF6_COLUMNS if c in raw.columns]
    df = raw[available].copy()

    # Optional date slicing
    if start is not None:
        df = df.loc[pd.Timestamp(start):]
    if end is not None:
        df = df.loc[:pd.Timestamp(end)]

    if df.empty:
        raise ValueError(
            f"No data found for the requested date range "
            f"({start} – {end}).  Check available history with "
            f"load_invespar_factors() (no date args)."
        )

    df = df.dropna(how="all")
    return df


# ---------------------------------------------------------------------------
# Nifty index sample
# ---------------------------------------------------------------------------

def load_nifty_sample(
    frequency: str = "monthly",
    start: str = "2016-01-01",
    end: str = "2019-12-31",
) -> pd.DataFrame:
    """Load the sample Nifty index dataset.

    Reads ``data/sample/nifty_indices.csv`` (daily price levels), optionally
    resamples to month-end, and returns percentage returns.

    Parameters
    ----------
    frequency : {'monthly', 'daily'}
        ``'monthly'`` resamples daily prices to month-end before computing
        returns.  ``'daily'`` returns day-over-day percentage returns.
    start : str
        Inclusive start date (default ``'2016-01-01'``).
    end : str
        Inclusive end date (default ``'2019-12-31'``).

    Returns
    -------
    pd.DataFrame
        Percentage returns (values in decimal form, 0.01 = 1 %) with a
        ``DatetimeIndex``.  Columns mirror the index columns in the CSV.

    Raises
    ------
    FileNotFoundError
        If ``data/sample/nifty_indices.csv`` does not exist.
    ValueError
        If *frequency* is not ``'monthly'`` or ``'daily'``, or if the
        resulting DataFrame is empty.

    Example
    -------
    >>> rets = load_nifty_sample(frequency='monthly', start='2017-01-01')
    >>> rets.head()
    """
    if frequency not in ("monthly", "daily"):
        raise ValueError(
            f"frequency must be 'monthly' or 'daily', got '{frequency}'."
        )

    csv_path = _SAMPLE_DIR / "nifty_indices.csv"
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Sample data file not found: {csv_path}\n"
            "Place 'nifty_indices.csv' in data/sample/ before calling this function."
        )

    prices = pd.read_csv(csv_path, index_col=0, parse_dates=True)
    prices.index.name = "Date"
    prices = prices.sort_index()

    # Slice to requested window before resampling
    prices = prices.loc[pd.Timestamp(start): pd.Timestamp(end)]

    if prices.empty:
        raise ValueError(
            f"No data in range {start} – {end}.  "
            "Check the date range against available data."
        )

    if frequency == "monthly":
        prices = prices.resample("ME").last()

    returns = prices.pct_change().dropna(how="all")
    return returns


# ---------------------------------------------------------------------------
# Fund NAV sample
# ---------------------------------------------------------------------------

_FUND_LABELS = {i: f"Fund_{chr(65 + i)}" for i in range(26)}   # A–Z


def load_fund_sample() -> pd.DataFrame:
    """Load the sample fund NAV dataset and return anonymised monthly returns.

    Reads ``data/sample/fund_nav.csv``.  If the file contains NAV levels,
    month-end prices are used to compute returns.  If the file already
    contains returns (values < 1 in absolute terms on average), they are
    used directly.  Fund columns are renamed Fund_A, Fund_B, … .

    Parameters
    ----------
    None

    Returns
    -------
    pd.DataFrame
        Monthly returns in decimal form with a ``DatetimeIndex`` (month-end).
        Columns: ``Fund_A``, ``Fund_B``, … (anonymised).

    Raises
    ------
    FileNotFoundError
        If ``data/sample/fund_nav.csv`` does not exist.

    Example
    -------
    >>> funds = load_fund_sample()
    >>> funds.columns.tolist()
    ['Fund_A', 'Fund_B', 'Fund_C']
    """
    csv_path = _SAMPLE_DIR / "fund_nav.csv"
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Sample data file not found: {csv_path}\n"
            "Place 'fund_nav.csv' in data/sample/ before calling this function."
        )

    df = pd.read_csv(csv_path, index_col=0, parse_dates=True)
    df.index.name = "Date"
    df = df.sort_index()

    # Resample to month-end if higher frequency detected
    if df.index.freq is None or df.index.freq.freqstr not in ("ME", "M", "BM"):
        inferred = pd.infer_freq(df.index[:20]) if len(df) >= 20 else None
        if inferred and inferred not in ("ME", "M", "BM", "MS"):
            df = df.resample("ME").last()

    # Detect whether data are NAV levels or returns
    median_abs = df.abs().median().median()
    if median_abs > 2:
        # Looks like price/NAV levels — compute returns
        df = df.pct_change().dropna(how="all")
    else:
        # Already returns; convert percentage points to decimal if needed
        if median_abs > 0.5:
            df = df / 100.0
        df = df.dropna(how="all")

    # Anonymise column names
    rename_map = {
        orig: _FUND_LABELS.get(i, f"Fund_{i}")
        for i, orig in enumerate(df.columns)
    }
    df = df.rename(columns=rename_map)

    return df


# ---------------------------------------------------------------------------
# Alignment utility
# ---------------------------------------------------------------------------

def align_data(*dataframes: pd.DataFrame) -> Tuple[pd.DataFrame, ...]:
    """Align multiple DataFrames to their common DatetimeIndex.

    All DataFrames are inner-joined on their index (intersection), then rows
    containing any NaN are dropped from each frame consistently.

    Parameters
    ----------
    *dataframes : pd.DataFrame
        Two or more DataFrames with a ``DatetimeIndex``.

    Returns
    -------
    tuple of pd.DataFrame
        Same number of DataFrames as inputs, trimmed to the common date range
        with no NaN rows.

    Raises
    ------
    ValueError
        If fewer than two DataFrames are supplied, if any input lacks a
        ``DatetimeIndex``, or if the intersection is empty.

    Example
    -------
    >>> f_aligned, r_aligned = align_data(factors, returns)
    """
    if len(dataframes) < 2:
        raise ValueError("align_data requires at least two DataFrames.")

    for i, df in enumerate(dataframes):
        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError(
                f"DataFrame at position {i} does not have a DatetimeIndex.  "
                "Convert the index with pd.to_datetime() first."
            )

    # Intersection of all indices
    common_index = dataframes[0].index
    for df in dataframes[1:]:
        common_index = common_index.intersection(df.index)

    if common_index.empty:
        raise ValueError(
            "The intersection of all provided DatetimeIndexes is empty.  "
            "Check that the DataFrames share an overlapping date range."
        )

    aligned = tuple(df.loc[common_index] for df in dataframes)

    # Drop dates where *any* frame has NaN
    combined_mask = np.ones(len(common_index), dtype=bool)
    for df in aligned:
        combined_mask &= df.notna().all(axis=1).values

    if not combined_mask.any():
        raise ValueError(
            "After dropping NaN rows, no observations remain.  "
            "Check for missing data in the input DataFrames."
        )

    return tuple(df.loc[combined_mask] for df in aligned)
