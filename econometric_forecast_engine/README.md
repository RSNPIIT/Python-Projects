# Econometric Forecast Engine • Hybrid Python-R Time Series Platform

A production-grade econometric platform that bridges **Python's data ingestion and serving capabilities** (`pandas`, `fastapi`, `uvicorn`) with **R's gold-standard time-series modeling libraries** (`urca`, `forecast`, `vars`, `tseries`).

Designed for quantitative researchers, macroeconomists, and data scientists requiring rigorous statistical diagnostics, unit root verification, automated state-space modeling, vector autoregression, and out-of-sample backtesting.

---

## 🏛️ Architecture Overview

```
econometric_forecast_engine/
├── config/
│   └── settings.yaml            # Tickers, horizons, frequency, model defaults
├── r_engine/
│   ├── stationarity.R           # Unit root (ADF, KPSS) & Johansen cointegration
│   ├── univariate_models.R      # State-space ETS, auto.arima, TBATS
│   └── multivariate_models.R    # Vector Autoregression (vars) & Granger causality
├── app/
│   ├── ingestion/
│   │   ├── market_loader.py     # Yahoo Finance loader & synthetic offline fallback
│   │   └── preprocessor.py      # Log-returns, differencing, interpolation, MAD outlier detection
│   ├── bridge/
│   │   └── r_forecaster.py      # rpy2 bridge with localconverter & Rscript subprocess fallback
│   ├── evaluation/
│   │   └── backtester.py        # Rolling-origin evaluation (RMSE, MAE, MAPE, MASE)
│   └── api/
│       └── routes.py            # FastAPI REST endpoints for forecasting & diagnostics
├── tests/
│   ├── test_r_bridge.py         # Unit tests for R bridge & econometric functions
│   └── test_pipeline.py         # End-to-end pipeline & FastAPI tests
├── notebooks/
│   └── exploratory_diagnostics.ipynb  # Interactive Jupyter notebook with %%R cell magic
├── main.py                      # CLI runner & Uvicorn API server
├── requirements.txt             # Python dependencies
├── pyproject.toml               # Setuptools configuration
└── install_r_deps.R             # Reproducible R package installer
```

---

## 📊 Econometric Methodology

### 1. Unit Root & Stationarity Testing
- **Augmented Dickey-Fuller (ADF)** (`urca::ur.df`): Tests $H_0: \text{Unit root present}$ against $H_1: \text{Stationary}$.
- **KPSS Test** (`urca::ur.kpss`): Tests $H_0: \text{Trend/Level Stationary}$ against $H_1: \text{Unit root}$.
- **Consensus Engine**: Compares ADF and KPSS to distinguish true stationarity, difference stationarity $I(1)$, and trend stationarity.

### 2. Univariate State-Space & ARIMA
- **Hyndman-Khandakar Auto-ARIMA** (`forecast::auto.arima`): Automated search across non-seasonal $(p,d,q)$ and seasonal $(P,D,Q)_m$ orders using AICc minimization and unit-root differencing tests.
- **State-Space Exponential Smoothing (ETS)** (`forecast::ets`): 30 possible model combinations over Error, Trend, and Seasonality components.
- **TBATS** (`forecast::tbats`): Handles non-integer and complex multiple seasonalities with Box-Cox transformation and Fourier series.

### 3. Multivariate VAR & Granger Causality
- **Vector Autoregression** (`vars::VAR`): Interdependent $K$-variable system:
  $$\mathbf{Y}_t = \mathbf{c} + \sum_{i=1}^p \mathbf{A}_i \mathbf{Y}_{t-i} + \mathbf{\varepsilon}_t$$
- **Granger Causality** (`vars::causality`): Wald $F$-tests identifying whether past values of series $X$ predict series $Y$ conditional on past values of $Y$.
- **Johansen Cointegration** (`urca::ca.jo`): Maximum eigenvalue and trace statistics for long-run stationary equilibrium relationships.

### 4. Rolling-Origin Time-Series Cross-Validation
- Evaluates models across expanding rolling windows $T_0, T_0 + k, \dots$.
- Computes **Mean Absolute Scaled Error (MASE)** (Hyndman & Koehler, 2006):
  $$\text{MASE} = \frac{\text{MAE}}{\frac{1}{N-1}\sum_{t=2}^N |y_t - y_{t-1}|}$$
  where $\text{MASE} < 1.0$ confirms the model outperforms a naive persistence benchmark.

---

## 🚀 Quickstart & Execution

### 1. Run the End-to-End Econometric Pipeline Demo:
```bash
cd /Users/ramrupsatpati/Desktop/Python/econometric_forecast_engine
/Users/ramrupsatpati/Desktop/Python/venv/bin/python main.py demo
```

### 2. Start the FastAPI REST Server:
```bash
/Users/ramrupsatpati/Desktop/Python/venv/bin/python main.py serve --port 8000
```
Interactive OpenAPI documentation will be accessible at:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### 3. Run the Automated Test Suite:
```bash
/Users/ramrupsatpati/Desktop/Python/venv/bin/pytest tests/
```

### 4. Install R Dependencies:
```bash
Rscript install_r_deps.R
```
