"""
CUPED-Adjusted Clustered Mixed-Effects Estimator
Combines pre-experiment baseline covariate residualization (CUPED)
with hierarchical linear mixed models to maximize statistical power.
"""
import numpy as np
import pandas as pd
from causal_lab.estimators.base import BaseEstimator
from causal_lab.bridge.r_bridge import RBridge
from causal_lab.bridge.schemas import EstimatorResult


class CUPEDMixedEffectsEstimator(BaseEstimator):
    def __init__(self, bridge: RBridge | None = None, covariate_col: str = "pre_covariate"):
        self.bridge = bridge or RBridge()
        self.covariate_col = covariate_col

    @property
    def name(self) -> str:
        return "CUPED + Mixed-Effects"

    def fit(self, df: pd.DataFrame, outcome_col: str = "outcome", treatment_col: str = "treatment") -> EstimatorResult:
        if self.covariate_col not in df.columns:
            raise ValueError(f"Pre-experiment covariate '{self.covariate_col}' not found in DataFrame.")

        # Compute optimal theta: Cov(Y, X) / Var(X)
        cov = np.cov(df[outcome_col], df[self.covariate_col])[0, 1]
        var_x = np.var(df[self.covariate_col], ddof=1)
        theta = cov / (var_x + 1e-12)

        # Residualize outcome
        mean_x = df[self.covariate_col].mean()
        df_cuped = df.copy()
        df_cuped["outcome_cuped"] = df[outcome_col] - theta * (df[self.covariate_col] - mean_x)

        # Fit Mixed-Effects on CUPED outcome
        formula = f"outcome_cuped ~ {treatment_col} + (1 | cluster_id)"
        result = self.bridge.fit_mixed_effects(df_cuped, formula=formula, reml=True)
        result.estimator_name = self.name
        result.diagnostics["cuped_theta"] = float(theta)
        result.diagnostics["variance_reduction_ratio"] = float(df_cuped["outcome_cuped"].var() / (df[outcome_col].var() + 1e-12))
        return result
