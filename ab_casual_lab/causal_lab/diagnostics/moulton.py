"""
Moulton Factor and Design Effect Diagnostic
Quantifies standard error underestimation and Effective Sample Size (ESS)
arising from clustered experimental designs.
"""
from dataclasses import dataclass
import numpy as np
import pandas as pd


@dataclass(frozen=True)
class MoultonDiagnostic:
    n_obs: int
    n_clusters: int
    avg_cluster_size: float
    cluster_size_cv: float         # Coefficient of variation of cluster size
    outcome_icc: float             # rho_Y
    treatment_icc: float           # rho_T (1.0 for cluster randomization)
    design_effect: float           # DEFF = 1 + (m* - 1) * rho_Y * rho_T
    moulton_factor: float          # sqrt(DEFF)
    effective_sample_size: float   # ESS = N / DEFF
    type_1_inflation_estimate: float  # Expected false positive rate if nominal alpha = 0.05


def compute_moulton_diagnostic(
    df: pd.DataFrame,
    outcome_icc: float,
    outcome_col: str = "outcome",
    treatment_col: str = "treatment",
    cluster_col: str = "cluster_id"
) -> MoultonDiagnostic:
    """
    Computes the Moulton factor and Design Effect (DEFF) according to:
    DEFF = 1 + (m_tilde - 1) * rho_Y * rho_T
    where m_tilde accounts for cluster size variation (Eldridge et al., 2006).
    """
    sizes = df.groupby(cluster_col).size().values
    n_obs = len(df)
    n_clusters = len(sizes)

    mean_m = float(np.mean(sizes))
    var_m = float(np.var(sizes, ddof=1)) if len(sizes) > 1 else 0.0
    cv_m = float(np.sqrt(var_m) / mean_m) if mean_m > 0 else 0.0

    # Effective cluster size under unequal sizes
    m_tilde = mean_m + (var_m / (n_obs * mean_m) if n_obs > 0 else 0.0)

    # Treatment ICC: measure how clustered treatment assignment is
    # In Cluster-Randomized Trials, treatment variance is 100% between clusters (rho_T = 1.0)
    cluster_treat_means = df.groupby(cluster_col)[treatment_col].mean().values
    total_treat_var = np.var(df[treatment_col], ddof=1)
    if total_treat_var > 1e-8:
        between_treat_var = np.var(cluster_treat_means, ddof=1)
        treatment_icc = float(np.clip(between_treat_var / total_treat_var, 0.0, 1.0))
    else:
        treatment_icc = 0.0

    # Moulton Design Effect
    # When rho_T = 1 (CRT), DEFF = 1 + (m_tilde - 1) * outcome_icc
    deff = 1.0 + (m_tilde - 1.0) * max(0.0, outcome_icc) * treatment_icc
    deff = max(1.0, float(deff))
    moulton_se_mult = float(np.sqrt(deff))
    ess = float(n_obs / deff)

    # Approximate Type-I error inflation: P(|Z * moulton_factor| > 1.96)
    from scipy import stats
    z_crit = 1.96 / moulton_se_mult
    t1_inflation = float(2.0 * (1.0 - stats.norm.cdf(z_crit)))

    return MoultonDiagnostic(
        n_obs=n_obs,
        n_clusters=n_clusters,
        avg_cluster_size=mean_m,
        cluster_size_cv=cv_m,
        outcome_icc=outcome_icc,
        treatment_icc=treatment_icc,
        design_effect=deff,
        moulton_factor=moulton_se_mult,
        effective_sample_size=ess,
        type_1_inflation_estimate=t1_inflation
    )
