"""
src/visualise.py
================
Chart helpers for pyIndiaFactorInvesting.

Style conventions
-----------------
- No top or right spines.
- Source annotation at bottom-right of every chart.
- 10 pt base font throughout.
- Each function returns the Axes object so callers can further customise.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.axes import Axes

_BASE_FONT = 10
_SOURCE_DEFAULT = "Invespar Indian Factor Library"
_FIG_DPI = 120


def _apply_style(ax: Axes) -> None:
    """Remove top/right spines and set base font size."""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(labelsize=_BASE_FONT)
    ax.xaxis.label.set_size(_BASE_FONT)
    ax.yaxis.label.set_size(_BASE_FONT)
    ax.title.set_size(_BASE_FONT + 1)


def _add_source(ax: Axes, source: str) -> None:
    """Add a small source annotation at the bottom-right of the figure."""
    ax.annotate(
        f"Source: {source}",
        xy=(1, 0),
        xycoords="axes fraction",
        ha="right",
        va="top",
        fontsize=_BASE_FONT - 2,
        color="grey",
        xytext=(0, -30),
        textcoords="offset points",
    )


# ---------------------------------------------------------------------------
# Cumulative returns
# ---------------------------------------------------------------------------

def plot_cumulative_returns(
    returns_df: pd.DataFrame,
    title: str,
    source: str = _SOURCE_DEFAULT,
) -> Axes:
    """Plot cumulative (compounded) returns for one or more return series.

    Parameters
    ----------
    returns_df : pd.DataFrame
        Monthly returns in decimal form with a ``DatetimeIndex``.
        Each column is plotted as a separate line.
    title : str
        Chart title.
    source : str
        Data source annotation displayed at bottom-right.
        Default: ``'Invespar Indian Factor Library'``.

    Returns
    -------
    matplotlib.axes.Axes

    Example
    -------
    >>> ax = plot_cumulative_returns(factors[['MKT', 'SMB5']], 'Factor Returns')
    >>> plt.show()
    """
    cum_ret = (1 + returns_df).cumprod() - 1

    fig, ax = plt.subplots(figsize=(9, 4), dpi=_FIG_DPI)
    for col in cum_ret.columns:
        ax.plot(cum_ret.index, cum_ret[col], label=col, linewidth=1.4)

    ax.set_title(title, fontsize=_BASE_FONT + 1, fontweight="bold")
    ax.set_xlabel("Date", fontsize=_BASE_FONT)
    ax.set_ylabel("Cumulative Return", fontsize=_BASE_FONT)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1, decimals=0))
    ax.legend(fontsize=_BASE_FONT - 1, frameon=False)
    ax.axhline(0, color="black", linewidth=0.6, linestyle="--")
    _apply_style(ax)
    _add_source(ax, source)
    fig.tight_layout()
    return ax


# ---------------------------------------------------------------------------
# Rolling beta
# ---------------------------------------------------------------------------

def plot_rolling_beta(
    rolling_coef_df: pd.DataFrame,
    factor_name: str,
    title: str,
    source: str = _SOURCE_DEFAULT,
) -> Axes:
    """Plot a rolling regression coefficient with a ±1 std band.

    Parameters
    ----------
    rolling_coef_df : pd.DataFrame
        Output of ``src.factors.rolling_regression()``.  Must contain a
        column named *factor_name*.
    factor_name : str
        Column name in *rolling_coef_df* to plot (e.g. ``'MKT'``).
    title : str
        Chart title.
    source : str
        Data source annotation.

    Returns
    -------
    matplotlib.axes.Axes

    Example
    -------
    >>> ax = plot_rolling_beta(coefs, 'MKT', 'Rolling Market Beta (36-month)')
    >>> plt.show()
    """
    if factor_name not in rolling_coef_df.columns:
        raise ValueError(
            f"Column '{factor_name}' not found in rolling_coef_df.  "
            f"Available columns: {list(rolling_coef_df.columns)}"
        )

    series = rolling_coef_df[factor_name].dropna()
    roll_mean = series.rolling(window=6, min_periods=1).mean()
    roll_std = series.rolling(window=6, min_periods=1).std()

    fig, ax = plt.subplots(figsize=(9, 4), dpi=_FIG_DPI)
    ax.plot(series.index, series.values, linewidth=1.4, label=factor_name)
    ax.fill_between(
        series.index,
        (roll_mean - roll_std).values,
        (roll_mean + roll_std).values,
        alpha=0.20,
        label="±1 std (6-month rolling)",
    )
    ax.axhline(0, color="black", linewidth=0.6, linestyle="--")
    ax.set_title(title, fontsize=_BASE_FONT + 1, fontweight="bold")
    ax.set_xlabel("Date", fontsize=_BASE_FONT)
    ax.set_ylabel(f"{factor_name} Coefficient", fontsize=_BASE_FONT)
    ax.legend(fontsize=_BASE_FONT - 1, frameon=False)
    _apply_style(ax)
    _add_source(ax, source)
    fig.tight_layout()
    return ax


# ---------------------------------------------------------------------------
# Drawdown (underwater curve)
# ---------------------------------------------------------------------------

def plot_drawdown(
    returns_series: pd.Series,
    title: str,
    source: str = _SOURCE_DEFAULT,
) -> Axes:
    """Plot an underwater equity curve (drawdown over time).

    Parameters
    ----------
    returns_series : pd.Series
        Monthly returns in decimal form with a ``DatetimeIndex``.
    title : str
        Chart title.
    source : str
        Data source annotation.

    Returns
    -------
    matplotlib.axes.Axes

    Example
    -------
    >>> ax = plot_drawdown(fund_returns['Fund_A'], 'Fund A Drawdown')
    >>> plt.show()
    """
    cum = (1 + returns_series).cumprod()
    rolling_max = cum.cummax()
    drawdown = (cum - rolling_max) / rolling_max

    fig, ax = plt.subplots(figsize=(9, 3.5), dpi=_FIG_DPI)
    ax.fill_between(drawdown.index, drawdown.values, 0, color="crimson", alpha=0.6)
    ax.plot(drawdown.index, drawdown.values, color="crimson", linewidth=0.8)
    ax.set_title(title, fontsize=_BASE_FONT + 1, fontweight="bold")
    ax.set_xlabel("Date", fontsize=_BASE_FONT)
    ax.set_ylabel("Drawdown", fontsize=_BASE_FONT)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1, decimals=0))
    ax.axhline(0, color="black", linewidth=0.6)
    _apply_style(ax)
    _add_source(ax, source)
    fig.tight_layout()
    return ax


# ---------------------------------------------------------------------------
# Factor summary table
# ---------------------------------------------------------------------------

def plot_factor_summary_table(
    summary_df: pd.DataFrame,
    title: str,
    source: str = _SOURCE_DEFAULT,
) -> Axes:
    """Render a factor summary statistics DataFrame as a matplotlib table.

    Parameters
    ----------
    summary_df : pd.DataFrame
        Output of ``src.factors.compute_factor_summary()``.
        Rows = factor names, columns = statistic names.
    title : str
        Title displayed above the table.
    source : str
        Data source annotation.

    Returns
    -------
    matplotlib.axes.Axes

    Example
    -------
    >>> ax = plot_factor_summary_table(summary, 'Indian Factor Summary')
    >>> plt.show()
    """
    # Format values for display
    fmt_df = summary_df.copy()
    pct_cols = {"Ann. Mean", "Ann. Vol", "Max Drawdown"}
    for col in fmt_df.columns:
        if col in pct_cols:
            fmt_df[col] = fmt_df[col].map(lambda x: f"{x:.1%}" if pd.notna(x) else "—")
        else:
            fmt_df[col] = fmt_df[col].map(lambda x: f"{x:.2f}" if pd.notna(x) else "—")

    n_rows, n_cols = fmt_df.shape
    fig_height = max(1.5, 0.45 * (n_rows + 2))
    fig, ax = plt.subplots(figsize=(min(12, 2.5 * n_cols), fig_height), dpi=_FIG_DPI)
    ax.axis("off")

    table = ax.table(
        cellText=fmt_df.values,
        rowLabels=fmt_df.index.tolist(),
        colLabels=fmt_df.columns.tolist(),
        cellLoc="center",
        loc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(_BASE_FONT)
    table.scale(1, 1.4)

    # Header styling
    for (row, col), cell in table.get_celld().items():
        if row == 0 or col == -1:
            cell.set_facecolor("#2c3e50")
            cell.set_text_props(color="white", fontweight="bold")
        elif row % 2 == 0:
            cell.set_facecolor("#f2f2f2")
        cell.set_edgecolor("white")

    ax.set_title(title, fontsize=_BASE_FONT + 1, fontweight="bold", pad=12)
    _add_source(ax, source)
    fig.tight_layout()
    return ax
