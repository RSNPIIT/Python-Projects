"""
Typed Data Schemas for Estimator Outputs and R Bridge Marshaling
"""
from dataclasses import dataclass, field
from typing import Optional, Any


@dataclass(frozen=True)
class ModelCoefficient:
    """Standardized representation of a single regression coefficient."""
    term: str
    estimate: float
    std_error: float
    statistic: float
    p_value: float
    ci_lower: float
    ci_upper: float
    df: Optional[float] = None

    @property
    def is_significant(self) -> bool:
        return self.p_value < 0.05


@dataclass
class EstimatorResult:
    """Standardized output from any causal estimator in the lab."""
    estimator_name: str
    treatment_effect: ModelCoefficient
    all_coefficients: dict[str, ModelCoefficient] = field(default_factory=dict)
    sigma_cluster: Optional[float] = None
    sigma_residual: Optional[float] = None
    icc: Optional[float] = None
    is_singular: bool = False
    aic: Optional[float] = None
    bic: Optional[float] = None
    n_obs: int = 0
    n_clusters: int = 0
    fit_time_seconds: float = 0.0
    diagnostics: dict[str, Any] = field(default_factory=dict)
