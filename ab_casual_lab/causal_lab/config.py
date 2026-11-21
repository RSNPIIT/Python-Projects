"""
Simulation, DGP, and Estimator Configuration
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class RandomizationScheme(str, Enum):
    INDIVIDUAL = "individual"  # Users within each cluster randomized (e.g. 50/50 split per city)
    CLUSTER = "cluster"        # Entire cluster assigned treatment or control (e.g. Geo-experiments)


@dataclass(frozen=True)
class DGPConfig:
    """Configuration parameters for the Hierarchical Data Generating Process."""
    n_clusters: int = 40
    avg_cluster_size: int = 50
    cluster_size_dispersion: float = 0.2  # Log-normal standard deviation for unbalanced clusters
    true_tau: float = 1.5                # True Average Treatment Effect (ATE)
    icc: float = 0.25                     # Intraclass Correlation Coefficient (rho in [0, 1))
    total_variance: float = 4.0          # Total outcome variance (sigma^2_u + sigma^2_e)
    simpsons_confounding: float = 0.0     # Confounding strength between cluster baseline and treatment
    randomization: RandomizationScheme = RandomizationScheme.INDIVIDUAL
    covariate_r2: float = 0.40           # Pre-experiment baseline covariate explanatory power (for CUPED)
    seed: Optional[int] = 42

    @property
    def sigma_cluster_sq(self) -> float:
        """Between-cluster variance sigma_u^2."""
        return self.total_variance * self.icc

    @property
    def sigma_residual_sq(self) -> float:
        """Within-cluster residual variance sigma_e^2."""
        return self.total_variance * (1.0 - self.icc)


@dataclass(frozen=True)
class BenchmarkConfig:
    """Monte Carlo benchmark evaluation settings."""
    n_replications: int = 100
    alpha: float = 0.05
    dgp: DGPConfig = field(default_factory=DGPConfig)
    parallel: bool = False
