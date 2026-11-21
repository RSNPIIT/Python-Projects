"""
Time Series Preprocessor (Transformations, Stationarity Prep, Returns)
"""
from typing import Union
import numpy as np
import pandas as pd


class TimeSeriesPreprocessor:
    """Handles time series stationarity transformations and frequency alignment."""

    @staticmethod
    def compute_log_returns(data: Union[pd.Series, pd.DataFrame]) -> Union[pd.Series, pd.DataFrame]:
        """Calculates continuously compounded log-returns: r_t = ln(P_t / P_{t-1})."""
        log_data = np.log(data)
        returns = log_data.diff().dropna()
        return returns

    @staticmethod
    def difference(data: Union[pd.Series, pd.DataFrame], order: int = 1) -> Union[pd.Series, pd.DataFrame]:
        """Calculates d-th order discrete differences to achieve stationarity."""
        diff_data = data
        for _ in range(order):
            diff_data = diff_data.diff().dropna()
        return diff_data

    @staticmethod
    def resample_frequency(data: Union[pd.Series, pd.DataFrame], freq: str = "W") -> Union[pd.Series, pd.DataFrame]:
        """Resamples series to specified frequency (D=Daily, W=Weekly, M=Monthly)."""
        resampled = data.resample(freq).last().dropna()
        return resampled

    @staticmethod
    def impute_missing(data: Union[pd.Series, pd.DataFrame], method: str = "linear") -> Union[pd.Series, pd.DataFrame]:
        """Imputes missing timestamps via time-based or linear interpolation."""
        if method == "linear":
            return data.interpolate(method="time").ffill().bfill()
        return data.ffill().bfill()

    @staticmethod
    def detect_outliers_mad(series: pd.Series, threshold: float = 3.5) -> pd.Series:
        """Detects anomalous jumps using Median Absolute Deviation (MAD)."""
        clean = series.dropna()
        median = clean.median()
        mad = np.median(np.abs(clean - median))
        if mad < 1e-12:
            return pd.Series(False, index=series.index)
        modified_z = 0.6745 * (clean - median) / mad
        return pd.Series(np.abs(modified_z) > threshold, index=clean.index)
