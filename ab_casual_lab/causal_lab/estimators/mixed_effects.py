"""
Linear Mixed-Effects Model (LMM / HLM) Estimator
Integrates with R lme4/lmerTest for exact Satterthwaite degrees of freedom,
REML variance components estimation, and Intraclass Correlation (ICC).
"""
import pandas as pd
from causal_lab.estimators.base import BaseEstimator
from causal_lab.bridge.r_bridge import RBridge
from causal_lab.bridge.schemas import EstimatorResult


class MixedEffectsEstimator(BaseEstimator):
    def __init__(self, bridge: RBridge | None = None, formula: str = "outcome ~ treatment + (1 | cluster_id)"):
        self.bridge = bridge or RBridge()
        self.formula = formula

    @property
    def name(self) -> str:
        return "Mixed-Effects Model (LMM)"

    def fit(self, df: pd.DataFrame, outcome_col: str = "outcome", treatment_col: str = "treatment") -> EstimatorResult:
        if "cluster_id" not in df.columns:
            raise ValueError("DataFrame must contain 'cluster_id' column for Mixed-Effects Model.")

        # Dynamically ensure formula matches column names
        formula = f"{outcome_col} ~ {treatment_col} + (1 | cluster_id)"
        result = self.bridge.fit_mixed_effects(df, formula=formula, reml=True)
        result.estimator_name = self.name
        return result
