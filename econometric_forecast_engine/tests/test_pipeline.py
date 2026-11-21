"""
End-to-End Pipeline & FastAPI Integration Tests
"""
import pytest
import numpy as np
import pandas as pd
from starlette.testclient import TestClient

from app.ingestion.market_loader import MarketDataLoader
from app.ingestion.preprocessor import TimeSeriesPreprocessor
from app.evaluation.backtester import RollingOriginBacktester
from app.api.routes import app


@pytest.fixture(scope="module")
def api_client():
    return TestClient(app)


def test_market_loader_and_preprocessor():
    loader = MarketDataLoader(cache_dir=None)
    series = loader.load_ticker("SPY", start_date="2022-01-01")
    assert len(series) > 100
    assert not series.isna().any()

    # Log returns
    returns = TimeSeriesPreprocessor.compute_log_returns(series)
    assert len(returns) == len(series) - 1
    assert -0.5 < returns.mean() < 0.5


def test_rolling_origin_backtest():
    rng = np.random.default_rng(42)
    series = pd.Series(np.cumsum(rng.normal(0.01, 1.0, 160)))

    backtester = RollingOriginBacktester()
    summary = backtester.evaluate(
        series=series,
        model_type="auto_arima",
        initial_train_size=100,
        horizon=10,
        step_size=20,
        frequency=1
    )

    assert summary.n_folds >= 2
    assert summary.mean_rmse > 0.0
    assert summary.mean_mae > 0.0
    assert summary.mean_mase > 0.0


def test_api_endpoints(api_client):
    # 1. Health check
    res_health = api_client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "healthy"

    # 2. Stationarity diagnostic endpoint
    data = list(range(50))
    res_stat = api_client.post("/api/v1/diagnostics/stationarity", json={"series": data, "deterministic_type": "trend"})
    assert res_stat.status_code == 200
    assert "consensus_verdict" in res_stat.json()

    # 3. Univariate forecast endpoint
    res_fc = api_client.post("/api/v1/forecast/univariate", json={
        "series": [float(x) for x in range(1, 60)],
        "model_type": "auto_arima",
        "horizon": 5,
        "frequency": 1
    })
    assert res_fc.status_code == 200
    assert len(res_fc.json()["point_forecast"]) == 5
