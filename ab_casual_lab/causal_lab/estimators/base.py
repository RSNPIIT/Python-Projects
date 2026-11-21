"""
Base Abstract Estimator Interface
"""
from abc import ABC, abstractmethod
import pandas as pd
from causal_lab.bridge.schemas import EstimatorResult


class BaseEstimator(ABC):
    """Abstract base class for all causal treatment effect estimators."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the estimator."""
        pass

    @abstractmethod
    def fit(self, df: pd.DataFrame, outcome_col: str = "outcome", treatment_col: str = "treatment") -> EstimatorResult:
        """Fit estimator and return standardized EstimatorResult."""
        pass
