"""
src/factors.py
==============
Factor return computations and regression utilities for pyIndiaFactorInvesting.

All return inputs are expected in decimal form (0.01 = 1 %).
All annualisation assumes 12 monthly observations per year.
"""

from __future__ import annotations

from typing import Dict, Any

import numpy as np
import pandas as pd
import statsmodels.api as sm

_MONTHS_PER_YEAR = 12


# ---------------------------------------------------------------------------
# Descriptive statistics
# ---------------------------------------------------------------------------

def compute_factor_summary(factor_df: pd.DataFrame) -> pd.DataFrame:
    """Compute annualised summary statistics for each factor column.

    Parameters
    ----------
    factor_df : pd.DataFrame
        Monthly factor returns in decimal form with a ``DatetimeIndex``.
        Each column is treated as an independent return series.

    Returns
    -------
    pd.DataFrame
        Index = factor names.  Columns:
        ``Ann. Mean``, ``Ann. Vol``, ``Sharpe``, ``Skewness``,
        ``Max Drawdown``.
        Sharpe is computed as Ann. Mean / Ann. Vol (no risk-free adjustment).

    Raises
    ------
    ValueError
        If *factor_df* is empty or contains no numeric columns.

    Example
    -------
    >>> summary = compute_factor_summary(factors[['MKT', 'SMB5', 'HML']])
    >>> summary['Ann. Mean']
    """
    if factor_df.empty:
        raise ValueError("factor_df is empty.")

    numeric_df = factor_df.select_dtypes(include=[np.number])
    if numeric_df.empty:
        raise ValueError("factor_df contains no numeric columns.")

    records = {}
    for col in numeric_df.columns:
        series = numeric_df[col].dropna()
        ann_mean = series.mean() * _MONTHS_PER_YEAR
        ann_vol = series.std() * np.sqrt(_MONTHS_PER_YEAR)
        sharpe = ann_mean / ann_vol if ann_vol != 0 else np.nan
        skew = series.skew()
        max_dd = _max_drawdown(series)
        records[col] = {
            "Ann. Mean": ann_mean,
            "Ann. Vol": ann_vol,
            "Sharpe": sharpe,
            "Skewness": skew,
            "Max Drawdown": max_dd,
        }

    return pd.DataFrame(records).T


def _max_drawdown(returns: pd.Series) -> float:
    """Compute the maximum drawdown from a monthly return series."""
    cum = (1 + returns).cumprod()
    rolling_max = cum.cummax()
    drawdown = (cum - rolling_max) / rolling_max
    return float(drawdown.min())


# ---------------------------------------------------------------------------
# Rolling regression
# ---------------------------------------------------------------------------

def rolling_regression(
    returns_series: pd.Series,
    factor_df: pd.DataFrame,
    window: int = 36,
) -> pd.DataFrame:
    """Rolling OLS regression of a return series on factor returns.

    Parameters
    ----------
    returns_series : pd.Series
        Monthly portfolio/fund returns in decimal form, ``DatetimeIndex``.
    factor_df : pd.DataFrame
        Monthly factor returns in decimal form, same ``DatetimeIndex`` as
        *returns_series*.  A constant (intercept) is added automatically.
    window : int
        Rolling window length in months (default 36).

    Returns
    -------
    pd.DataFrame
        Rolling coefficients and R-squared, indexed by the end date of each
        window.  Columns: one per factor plus ``const`` and ``R_squared``.

    Raises
    ------
    ValueError
        If *window* is larger than the number of observations, or if
        *returns_series* and *factor_df* do not share a common index.

    Example
    -------
    >>> coefs = rolling_regression(fund_returns, factors[['MKT', 'SMB5']])
    >>> coefs['MKT'].plot()
    """
    if len(returns_series) < window:
        raise ValueError(
            f"window={window} exceeds the number of observations "
            f"({len(returns_series)}).  Reduce window or provide more data."
        )

    common = returns_series.index.intersection(factor_df.index)
    if common.empty:
        raise ValueError(
            "returns_series and factor_df share no common dates.  "
            "Use align_data() before calling rolling_regression()."
        )

    y = returns_series.loc[common]
    X = sm.add_constant(factor_df.loc[common], has_const=False)

    cols = list(X.columns) + ["R_squared"]
    results: dict[pd.Timestamp, dict] = {}

    for end_pos in range(window, len(y) + 1):
        start_pos = end_pos - window
        y_win = y.iloc[start_pos:end_pos]
        X_win = X.iloc[start_pos:end_pos]

        try:
            model = sm.OLS(y_win, X_win).fit()
            row = dict(zip(X.columns, model.params))
            row["R_squared"] = model.rsquared
        except Exception:
            row = {c: np.nan for c in cols}

        results[y.index[end_pos - 1]] = row

    result_df = pd.DataFrame(results).T
    result_df.index.name = "Date"
    return result_df


# ---------------------------------------------------------------------------
# Full-sample regression
# ---------------------------------------------------------------------------

def run_factor_regression(
    returns_series: pd.Series,
    factor_df: pd.DataFrame,
) -> Dict[str, Any]:
    """Full-sample OLS regression of returns on factor returns.

    Parameters
    ----------
    returns_series : pd.Series
        Monthly portfolio/fund returns in decimal form, ``DatetimeIndex``.
    factor_df : pd.DataFrame
        Monthly factor returns in decimal form.  A constant is added
        automatically to capture alpha.

    Returns
    -------
    dict
        Keys:
        - ``alpha``       : annualised alpha (float)
        - ``betas``       : dict of {factor_name: coefficient}
        - ``t_stats``     : dict of {param_name: t-statistic}
        - ``p_values``    : dict of {param_name: p-value}
        - ``r_squared``   : float
        - ``adj_r_squared``: float
        - ``n_obs``       : int
        - ``summary``     : full statsmodels ``RegressionResultsWrapper``

    Raises
    ------
    ValueError
        If *returns_series* and *factor_df* share fewer than 12 overlapping
        observations (regression would be unreliable).

    Example
    -------
    >>> result = run_factor_regression(fund_returns, factors)
    >>> result['alpha'], result['r_squared']
    """
    common = returns_series.index.intersection(factor_df.index)
    if len(common) < 12:
        raise ValueError(
            f"Only {len(common)} overlapping observations found.  "
            "At least 12 are required for a meaningful regression.  "
            "Use align_data() to check date overlap."
        )

    y = returns_series.loc[common]
    X = sm.add_constant(factor_df.loc[common], has_const=False)

    model = sm.OLS(y, X).fit()

    betas = {k: v for k, v in model.params.items() if k != "const"}
    t_stats = dict(zip(model.params.index, model.tvalues))
    p_values = dict(zip(model.params.index, model.pvalues))

    # Annualise alpha (intercept is monthly)
    alpha_monthly = float(model.params.get("const", np.nan))
    alpha_annual = (1 + alpha_monthly) ** _MONTHS_PER_YEAR - 1

    return {
        "alpha": alpha_annual,
        "betas": betas,
        "t_stats": t_stats,
        "p_values": p_values,
        "r_squared": float(model.rsquared),
        "adj_r_squared": float(model.rsquared_adj),
        "n_obs": int(model.nobs),
        "summary": model,
    }


# ---------------------------------------------------------------------------
# Information ratio
# ---------------------------------------------------------------------------

def compute_information_ratio(
    portfolio_returns: pd.Series,
    benchmark_returns: pd.Series,
) -> float:
    """Compute the annualised Information Ratio.

    IR = (Ann. mean active return) / (Ann. tracking error)

    Parameters
    ----------
    portfolio_returns : pd.Series
        Monthly portfolio returns in decimal form.
    benchmark_returns : pd.Series
        Monthly benchmark returns in decimal form.  Must share at least
        one date with *portfolio_returns*.

    Returns
    -------
    float
        Annualised Information Ratio.  Returns ``np.nan`` if tracking
        error is zero.

    Raises
    ------
    ValueError
        If the two series share no overlapping dates.

    Example
    -------
    >>> ir = compute_information_ratio(fund_returns, nifty_returns)
    >>> round(ir, 2)
    0.45
    """
    common = portfolio_returns.index.intersection(benchmark_returns.index)
    if common.empty:
        raise ValueError(
            "portfolio_returns and benchmark_returns share no common dates."
        )

    active = portfolio_returns.loc[common] - benchmark_returns.loc[common]
    ann_active_mean = active.mean() * _MONTHS_PER_YEAR
    ann_tracking_error = active.std() * np.sqrt(_MONTHS_PER_YEAR)

    if ann_tracking_error == 0:
        return np.nan

    return float(ann_active_mean / ann_tracking_error)
