"""
FastAPI REST Application Endpoints for Econometric Forecasting & Diagnostics
"""
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.ingestion.market_loader import MarketDataLoader
from app.ingestion.preprocessor import TimeSeriesPreprocessor
from app.bridge.r_forecaster import RForecaster
from app.evaluation.backtester import RollingOriginBacktester

app = FastAPI(
    title="Econometric Forecast Engine API",
    description="Production Time-Series Forecasting & Diagnostic API powered by Python and R (urca, forecast, vars)",
    version="1.0.0"
)

loader = MarketDataLoader()
preprocessor = TimeSeriesPreprocessor()
forecaster = RForecaster()
backtester = RollingOriginBacktester(forecaster=forecaster)


# ------------------------------------------------------------------------------
# Request / Response Schemas
# ------------------------------------------------------------------------------
class TickerRequest(BaseModel):
    ticker: str = Field(..., json_schema_extra={"example": "SPY"})
    start_date: str = Field("2021-01-01", json_schema_extra={"example": "2021-01-01"})
    end_date: Optional[str] = None
    frequency: str = Field("D", json_schema_extra={"example": "D"})


class StationarityRequest(BaseModel):
    series: List[float] = Field(..., description="List of numeric observations")
    deterministic_type: str = Field("trend", json_schema_extra={"example": "trend"})


class CointegrationRequest(BaseModel):
    series_dict: dict[str, List[float]] = Field(..., description="Map of variable names to lists of values")
    lag_order: int = Field(2, json_schema_extra={"example": 2})


class UnivariateForecastRequest(BaseModel):
    series: List[float] = Field(..., description="Historical time series observations")
    model_type: str = Field("auto_arima", json_schema_extra={"example": "auto_arima"})  # auto_arima, ets, tbats
    horizon: int = Field(14, json_schema_extra={"example": 14})
    frequency: int = Field(7, json_schema_extra={"example": 7})


class VARForecastRequest(BaseModel):
    series_dict: dict[str, List[float]] = Field(..., description="Multi-asset dictionary")
    max_lag: int = Field(5, json_schema_extra={"example": 5})
    horizon: int = Field(14, json_schema_extra={"example": 14})


class BacktestRequest(BaseModel):
    series: List[float]
    model_type: str = "auto_arima"
    initial_train_size: int = 120
    horizon: int = 14
    step_size: int = 14
    frequency: int = 7


# ------------------------------------------------------------------------------
# API Endpoints
# ------------------------------------------------------------------------------
@app.get("/health")
def health_check():
    """Health check endpoint checking R and Python connectivity."""
    return {
        "status": "healthy",
        "rpy2_initialized": forecaster._rpy2_ready,
        "engine": "R (forecast, urca, vars) + FastAPI"
    }


@app.post("/api/v1/data/load")
def load_market_data(req: TickerRequest):
    """Fetches market price series and calculates log-returns."""
    try:
        series = loader.load_ticker(req.ticker, start_date=req.start_date, end_date=req.end_date)
        if req.frequency != "D":
            series = preprocessor.resample_frequency(series, freq=req.frequency)

        returns = preprocessor.compute_log_returns(series)
        return {
            "ticker": req.ticker,
            "n_observations": len(series),
            "timestamps": [str(d) for d in series.index],
            "prices": series.tolist(),
            "log_returns": returns.tolist()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/diagnostics/stationarity")
def check_stationarity(req: StationarityRequest):
    """Runs ADF and KPSS unit root tests to verify stationarity."""
    try:
        res = forecaster.test_stationarity(req.series, type=req.deterministic_type)
        return {
            "n_obs": res.n_obs,
            "consensus_verdict": res.consensus_verdict,
            "recommended_differencing": res.recommended_differencing,
            "adf": {
                "statistic": res.adf_statistic,
                "lags": res.adf_lags,
                "is_stationary": res.adf_is_stationary,
                "critical_values": res.adf_critical_values
            },
            "kpss": {
                "statistic": res.kpss_statistic,
                "is_stationary": res.kpss_is_stationary,
                "critical_values": res.kpss_critical_values
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/v1/diagnostics/cointegration")
def check_cointegration(req: CointegrationRequest):
    """Runs Johansen cointegration test across multiple series."""
    try:
        import pandas as pd
        df = pd.DataFrame(req.series_dict)
        res = forecaster.test_cointegration(df, lag_k=req.lag_order)
        return {
            "n_vars": res.n_vars,
            "cointegrating_rank": res.cointegrating_rank,
            "is_cointegrated": res.is_cointegrated,
            "eigenvalues": res.eigenvalues,
            "test_statistics": res.test_statistics,
            "critical_values_5pct": res.critical_values_5pct
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/v1/forecast/univariate")
def forecast_univariate(req: UnivariateForecastRequest):
    """Fits Auto-ARIMA, ETS, or TBATS and returns forecast with prediction intervals."""
    try:
        res = forecaster.fit_univariate(
            series=req.series,
            model_type=req.model_type,
            horizon=req.horizon,
            frequency=req.frequency
        )
        return {
            "model_type": res.model_type,
            "model_name": res.model_name,
            "n_obs": res.n_obs,
            "horizon": res.horizon,
            "point_forecast": res.point_forecast,
            "prediction_intervals": res.prediction_intervals,
            "in_sample_metrics": res.in_sample_metrics,
            "ljung_box_p_value": res.ljung_box_p_value
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/v1/forecast/multivariate")
def forecast_multivariate(req: VARForecastRequest):
    """Fits Vector Autoregression and assesses Granger Causality."""
    try:
        import pandas as pd
        df = pd.DataFrame(req.series_dict)
        res = forecaster.fit_multivariate_var(df, max_lag=req.max_lag, horizon=req.horizon)
        return {
            "variables": res.variables,
            "lag_order": res.lag_order,
            "is_stable": res.is_stable,
            "max_eigenvalue_root": res.max_eigenvalue_root,
            "forecasts": res.forecasts,
            "granger_causality": res.granger_causality,
            "log_likelihood": res.log_likelihood
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/v1/evaluation/backtest")
def evaluate_rolling_backtest(req: BacktestRequest):
    """Executes rolling-origin evaluation computing RMSE, MAE, MAPE, and MASE."""
    try:
        import pandas as pd
        s = pd.Series(req.series)
        summary = backtester.evaluate(
            series=s,
            model_type=req.model_type,
            initial_train_size=req.initial_train_size,
            horizon=req.horizon,
            step_size=req.step_size,
            frequency=req.frequency
        )
        return {
            "model_type": summary.model_type,
            "n_folds": summary.n_folds,
            "horizon": summary.horizon,
            "mean_rmse": summary.mean_rmse,
            "std_rmse": summary.std_rmse,
            "mean_mae": summary.mean_mae,
            "mean_mape": summary.mean_mape,
            "mean_mase": summary.mean_mase,
            "folds": [
                {
                    "fold": f.fold_idx,
                    "rmse": f.rmse,
                    "mae": f.mae,
                    "mape": f.mape,
                    "mase": f.mase
                }
                for f in summary.fold_details
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
