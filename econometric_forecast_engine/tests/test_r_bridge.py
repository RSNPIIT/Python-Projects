"""
Unit Tests for R Forecaster Bridge (ADF, KPSS, ARIMA, ETS, VAR)
"""
import pytest
import numpy as np
import pandas as pd
from app.bridge.r_forecaster import (
    RForecaster,
    StationarityResult,
    UnivariateForecastResult,
    VARForecastResult
)


@pytest.fixture(scope="module")
def r_forecaster():
    return RForecaster()


def test_stationarity_unit_root(r_forecaster):
    # 1. Non-stationary random walk
    rng = np.random.default_rng(42)
    random_walk = np.cumsum(rng.normal(0.05, 1.0, size=150))
    res_rw = r_forecaster.test_stationarity(random_walk, type="trend")

    assert isinstance(res_rw, StationarityResult)
    assert res_rw.n_obs == 150
    assert not res_rw.adf_is_stationary  # Random walk should fail ADF
    assert res_rw.recommended_differencing == 1

    # 2. Stationary white noise
    white_noise = rng.normal(0.0, 1.0, size=150)
    res_wn = r_forecaster.test_stationarity(white_noise, type="none")
    assert res_wn.adf_is_stationary


def test_univariate_auto_arima(r_forecaster):
    # Simulated AR(1) series: y_t = 0.7 * y_{t-1} + e_t
    rng = np.random.default_rng(123)
    e = rng.normal(0, 1, 120)
    y = np.zeros(120)
    for t in range(1, 120):
        y[t] = 0.7 * y[t - 1] + e[t]

    res = r_forecaster.fit_univariate(y, model_type="auto_arima", horizon=10, frequency=1)
    assert isinstance(res, UnivariateForecastResult)
    assert len(res.point_forecast) == 10
    assert "lower_95" in res.prediction_intervals
    assert "upper_95" in res.prediction_intervals
    assert res.in_sample_metrics["RMSE"] > 0.0


def test_univariate_ets(r_forecaster):
    rng = np.random.default_rng(456)
    series = np.linspace(10, 50, 100) + rng.normal(0, 2, 100)

    res = r_forecaster.fit_univariate(series, model_type="ets", horizon=7, frequency=7)
    assert isinstance(res, UnivariateForecastResult)
    assert len(res.point_forecast) == 7
    assert res.in_sample_metrics["AIC"] is not None


def test_multivariate_var(r_forecaster):
    # 2 correlated random walks
    rng = np.random.default_rng(789)
    x1 = np.cumsum(rng.normal(0, 1, 100))
    x2 = 0.5 * x1 + np.cumsum(rng.normal(0, 0.5, 100))
    df = pd.DataFrame({"AssetA": x1, "AssetB": x2})

    res = r_forecaster.fit_multivariate_var(df, max_lag=3, horizon=8)
    assert isinstance(res, VARForecastResult)
    assert len(res.variables) == 2
    assert "AssetA" in res.forecasts
    assert "AssetB" in res.forecasts
    assert len(res.forecasts["AssetA"]["point_forecast"]) == 8
    assert "AssetA" in res.granger_causality
