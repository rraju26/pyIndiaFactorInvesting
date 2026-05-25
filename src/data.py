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
_FF6_CACHE = _REPO_ROOT / "data" / "invespar" / "ff6_factors.csv"


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
    if _FF6_CACHE.exists():
        raw = pd.read_csv(_FF6_CACHE, index_col=0, parse_dates=True)
    else:
        try:
            from indiafactorlibrary import IndiaFactorLibrary  # type: ignore
        except ImportError as exc:
            raise ImportError(
                "The 'indiafactorlibrary' package is required but not installed.\n"
                "Install it with:  pip install indiafactorlibrary"
            ) from exc
        ifl = IndiaFactorLibrary()
        raw = ifl.read('FF6')[0]

    # Normalise the index to a proper DatetimeIndex (month-end)
    if not isinstance(raw.index, pd.DatetimeIndex):
        raw.index = pd.to_datetime(raw.index)
    raw.index = raw.index.to_period("M").to_timestamp("M")
    raw.index.name = "Date"

    # Keep only standard columns that exist in the loaded data
    available = [c for c in _FF6_COLUMNS if c in raw.columns]
    df = raw[available].copy()

    # Library returns percent form (1.0 = 1 %); convert to decimal
    df = df / 100.0

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
    start: str = "2015-01-01",
    end: str = "2020-12-31",
) -> pd.DataFrame:
    """Load the sample Nifty index dataset.

    Reads ``data/sample/nifty_monthly_returns.csv``, which contains
    pre-computed monthly returns in percentage form (6.1 = +6.1 %).

    Parameters
    ----------
    frequency : {'monthly'}
        Only ``'monthly'`` is supported for this sample file.
        Passing ``'daily'`` raises ``NotImplementedError``.
    start : str
        Inclusive start date (default ``'2015-01-01'``).
    end : str
        Inclusive end date (default ``'2020-12-31'``).

    Returns
    -------
    pd.DataFrame
        Monthly returns in decimal form (0.01 = 1 %) with a
        ``DatetimeIndex``.  Columns mirror the index columns in the CSV.

    Raises
    ------
    FileNotFoundError
        If ``data/sample/nifty_monthly_returns.csv`` does not exist.
    NotImplementedError
        If *frequency* is ``'daily'`` (daily data not in this sample file).
    ValueError
        If *frequency* is not ``'monthly'`` or ``'daily'``, or if the
        resulting DataFrame is empty.

    Example
    -------
    >>> rets = load_nifty_sample(frequency='monthly', start='2017-01-01')
    >>> rets.head()
    """
    if frequency == "daily":
        raise NotImplementedError(
            "Daily frequency is not available in the sample file "
            "nifty_monthly_returns.csv.  Only 'monthly' is supported."
        )
    if frequency != "monthly":
        raise ValueError(
            f"frequency must be 'monthly' or 'daily', got '{frequency}'."
        )

    csv_path = _SAMPLE_DIR / "nifty_monthly_returns.csv"
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Sample data file not found: {csv_path}\n"
            "Place 'nifty_monthly_returns.csv' in data/sample/ before calling this function."
        )

    df = pd.read_csv(csv_path, index_col=0, parse_dates=True)
    df.index.name = "Date"
    df = df.sort_index()

    df = df.loc[pd.Timestamp(start): pd.Timestamp(end)]

    if df.empty:
        raise ValueError(
            f"No data in range {start} – {end}.  "
            "Check the date range against available data."
        )

    # CSV values are in percent form (6.1 = +6.1 %); convert to decimal
    return df / 100.0


# ---------------------------------------------------------------------------
# Fund NAV sample
# ---------------------------------------------------------------------------

_FUND_LABELS = {i: f"Fund_{chr(65 + i)}" for i in range(26)}   # A–Z


def load_fund_sample() -> pd.DataFrame:
    """Load the sample fund returns dataset.

    Reads ``data/sample/fund_returns.csv``, which contains pre-computed
    monthly returns in percentage form (6.1 = +6.1 %) with columns
    Fund_A, Fund_B, Fund_C.

    Parameters
    ----------
    None

    Returns
    -------
    pd.DataFrame
        Monthly returns in decimal form with a ``DatetimeIndex`` (month-end).
        Columns: ``Fund_A``, ``Fund_B``, ``Fund_C``.

    Raises
    ------
    FileNotFoundError
        If ``data/sample/fund_returns.csv`` does not exist.

    Example
    -------
    >>> funds = load_fund_sample()
    >>> funds.columns.tolist()
    ['Fund_A', 'Fund_B', 'Fund_C']
    """
    csv_path = _SAMPLE_DIR / "fund_returns.csv"
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Sample data file not found: {csv_path}\n"
            "Place 'fund_returns.csv' in data/sample/ before calling this function."
        )

    df = pd.read_csv(csv_path, index_col=0, parse_dates=True)
    df.index.name = "Date"
    df = df.sort_index()

    # CSV values are in percent form (6.1 = +6.1 %); convert to decimal
    return df / 100.0


# ---------------------------------------------------------------------------
# Fixed income factor proxies
# ---------------------------------------------------------------------------

_FI_FACTORS_CACHE = _REPO_ROOT / "data" / "invespar" / "fi_factors.csv"


def load_fi_factors(
    start: Optional[str] = None,
    end: Optional[str] = None,
) -> pd.DataFrame:
    """Load TERM_IN and CREDIT_IN fixed income factor proxies for India.

    Wraps ``IndiaFactorLibrary().read('fi_factors')`` and returns a tidy monthly
    DataFrame ready for regression.  These are **synthetic benchmark-exposure
    proxies** constructed from LSEG Datastream benchmark yields; they are not
    directly observed investable total return indices (Raju 2026, SSRN 6419998).

    A local CSV cache at ``data/invespar/fi_factors.csv`` is used when present
    (faster for local execution); otherwise the library is called directly.

    Parameters
    ----------
    start : str, optional
        Inclusive start date, e.g. ``'2015-01-01'``.
    end : str, optional
        Inclusive end date, e.g. ``'2025-03-31'``.

    Returns
    -------
    pd.DataFrame
        Monthly factor returns in decimal form (0.01 = 1 %) with a
        ``DatetimeIndex`` (month-end).  Columns: ``TERM_IN``, ``CREDIT_IN``.
        CREDIT_IN is available from Jun 2012 onward.

    Raises
    ------
    ImportError
        If ``indiafactorlibrary`` is not installed and no cache file exists.
    ValueError
        If the resulting DataFrame is empty after date filtering.

    Example
    -------
    >>> fi = load_fi_factors(start='2015-01-01')
    >>> fi.columns.tolist()
    ['TERM_IN', 'CREDIT_IN']
    """
    if _FI_FACTORS_CACHE.exists():
        raw = pd.read_csv(_FI_FACTORS_CACHE, index_col=0, parse_dates=True)
    else:
        try:
            from indiafactorlibrary import IndiaFactorLibrary  # type: ignore
        except ImportError as exc:
            raise ImportError(
                "The 'indiafactorlibrary' package is required but not installed.\n"
                "Install it with:  pip install indiafactorlibrary"
            ) from exc
        ifl = IndiaFactorLibrary()
        raw = ifl.read('fi_factors')[0]

    if not isinstance(raw.index, pd.DatetimeIndex):
        raw.index = pd.to_datetime(raw.index)
    raw.index = raw.index.to_period("M").to_timestamp("M")
    raw.index.name = "Date"

    df = raw.sort_index() / 100.0  # percent → decimal

    if start is not None:
        df = df.loc[pd.Timestamp(start):]
    if end is not None:
        df = df.loc[:pd.Timestamp(end)]

    if df.empty:
        raise ValueError(
            f"No fixed income factor data in range ({start} – {end}).  "
            "Check available history with load_fi_factors() (no date args)."
        )

    return df


# ---------------------------------------------------------------------------
# Fixed income fund sample
# ---------------------------------------------------------------------------

_FI_FUND_SAMPLE = _REPO_ROOT / "data" / "sample" / "fi_fund_returns.csv"


def load_fi_fund_sample(
    start: Optional[str] = None,
    end: Optional[str] = None,
) -> pd.DataFrame:
    """Load five anonymised Indian fixed income fund monthly returns.

    Reads ``data/sample/fi_fund_returns.csv``.  The five funds span the
    debt-fund category spectrum: gilt (Fund_A), dynamic bond (Fund_B),
    short duration (Fund_C), corporate bond (Fund_D), and credit risk (Fund_E).

    Parameters
    ----------
    start : str, optional
        Inclusive start date, e.g. ``'2015-01-01'``.
    end : str, optional
        Inclusive end date, e.g. ``'2025-03-31'``.

    Returns
    -------
    pd.DataFrame
        Monthly returns in decimal form (0.01 = 1 %) with a ``DatetimeIndex``
        (month-end).  Columns: ``Fund_A``, ``Fund_B``, ``Fund_C``,
        ``Fund_D``, ``Fund_E``.  Period: Jun 2012 – Mar 2025.

    Raises
    ------
    FileNotFoundError
        If the sample file does not exist.
    ValueError
        If the resulting DataFrame is empty after date filtering.

    Example
    -------
    >>> funds = load_fi_fund_sample()
    >>> funds.columns.tolist()
    ['Fund_A', 'Fund_B', 'Fund_C', 'Fund_D', 'Fund_E']
    """
    if not _FI_FUND_SAMPLE.exists():
        raise FileNotFoundError(
            f"FI fund sample not found: {_FI_FUND_SAMPLE}\n"
            "Place 'fi_fund_returns.csv' in data/sample/ before calling this function."
        )

    df = pd.read_csv(_FI_FUND_SAMPLE, index_col=0, parse_dates=True)
    df.index.name = "Date"
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    df.index = df.index.to_period("M").to_timestamp("M")
    df = df.sort_index() / 100.0  # percent → decimal

    if start is not None:
        df = df.loc[pd.Timestamp(start):]
    if end is not None:
        df = df.loc[:pd.Timestamp(end)]

    if df.empty:
        raise ValueError(
            f"No FI fund data in range ({start} – {end}).  "
            "Check available history with load_fi_fund_sample() (no date args)."
        )

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
