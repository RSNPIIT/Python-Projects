"""
Rolling-Origin Evaluation & Time-Series Cross-Validation (RMSE, MAE, MAPE, MASE)
"""
from dataclasses import dataclass
from typing import Sequence, Optional
import numpy as np
import pandas as pd
from app.bridge.r_forecaster import RForecaster


@dataclass
class FoldMetric:
    fold_idx: int
    train_end_idx: int
    actuals: list[float]
    predictions: list[float]
    rmse: float
    mae: float
    mape: float
    mase: float


@dataclass
class BacktestSummary:
    model_type: str
    n_folds: int
    horizon: int
    mean_rmse: float
    std_rmse: float
    mean_mae: float
    mean_mape: float
    mean_mase: float
    fold_details: list[FoldMetric]


class RollingOriginBacktester:
    """Evaluates time series forecasting models via rolling-origin cross-validation."""

    def __init__(self, forecaster: Optional[RForecaster] = None):
        self.forecaster = forecaster or RForecaster()

    def evaluate(
        self,
        series: pd.Series,
        model_type: str = "auto_arima",
        initial_train_size: int = 120,
        horizon: int = 14,
        step_size: int = 14,
        frequency: int = 7
    ) -> BacktestSummary:
        values = series.dropna().values
        n_total = len(values)

        if n_total < initial_train_size + horizon:
            raise ValueError(
                f"Series length ({n_total}) is insufficient for initial_train_size ({initial_train_size}) + horizon ({horizon})."
            )

        folds = []
        current_train_end = initial_train_size

        fold_idx = 0
        while current_train_end + horizon <= n_total:
            train_data = values[:current_train_end]
            test_data = values[current_train_end : current_train_end + horizon]

            # In-sample naive mean absolute difference for MASE normalization
            naive_diff = np.abs(np.diff(train_data))
            scale_factor = np.mean(naive_diff) if len(naive_diff) > 0 and np.mean(naive_diff) > 1e-8 else 1.0

            try:
                # Fit model on training slice
                fc_res = self.forecaster.fit_univariate(
                    series=train_data,
                    model_type=model_type,
                    horizon=horizon,
                    frequency=frequency
                )
                preds = np.array(fc_res.point_forecast)

                # Error metrics for fold
                errors = test_data - preds
                abs_errors = np.abs(errors)
                rmse = float(np.sqrt(np.mean(errors ** 2)))
                mae = float(np.mean(abs_errors))
                mape = float(np.mean(abs_errors / (np.abs(test_data) + 1e-8)) * 100.0)
                mase = float(mae / scale_factor)

                folds.append(FoldMetric(
                    fold_idx=fold_idx,
                    train_end_idx=current_train_end,
                    actuals=test_data.tolist(),
                    predictions=preds.tolist(),
                    rmse=rmse,
                    mae=mae,
                    mape=mape,
                    mase=mase
                ))
            except Exception as e:
                # In case a specific fold fails to converge
                pass

            fold_idx += 1
            current_train_end += step_size

        if not folds:
            raise RuntimeError("All rolling-origin evaluation folds failed to execute.")

        rmses = [f.rmse for f in folds]
        maes = [f.mae for f in folds]
        mapes = [f.mape for f in folds]
        mases = [f.mase for f in folds]

        return BacktestSummary(
            model_type=model_type,
            n_folds=len(folds),
            horizon=horizon,
            mean_rmse=float(np.mean(rmses)),
            std_rmse=float(np.std(rmses, ddof=1)) if len(rmses) > 1 else 0.0,
            mean_mae=float(np.mean(maes)),
            mean_mape=float(np.mean(mapes)),
            mean_mase=float(np.mean(mases)),
            fold_details=folds
        )
