"""
Simpson's Paradox & Ecological Fallacy Detector
Decomposes treatment effect into Within-Cluster and Between-Cluster components.
"""
from dataclasses import dataclass
import numpy as np
import pandas as pd
import statsmodels.api as sm


@dataclass(frozen=True)
class SimpsonsDiagnostic:
    pooled_estimate: float
    within_estimate: float
    between_estimate: float
    is_paradox_detected: bool
    reversal_description: str


def detect_simpsons_paradox(
    df: pd.DataFrame,
    outcome_col: str = "outcome",
    treatment_col: str = "treatment",
    cluster_col: str = "cluster_id"
) -> SimpsonsDiagnostic:
    """
    Decomposes total OLS relationship into:
    1. Pooled OLS (naive)
    2. Within-cluster OLS (fixed effects / demeaned)
    3. Between-cluster OLS (cluster means regression)
    """
    # 1. Pooled OLS
    X_pool = sm.add_constant(df[treatment_col])
    fit_pool = sm.OLS(df[outcome_col], X_pool).fit()
    tau_pooled = float(fit_pool.params[treatment_col])

    # 2. Within-cluster (Demeaned / Fixed Effects)
    means = df.groupby(cluster_col)[[outcome_col, treatment_col]].transform("mean")
    y_within = df[outcome_col] - means[outcome_col]
    t_within = df[treatment_col] - means[treatment_col]

    if t_within.var() > 1e-8:
        fit_within = sm.OLS(y_within, t_within).fit()
        tau_within = float(fit_within.params.iloc[0])
    else:
        # If treatment is constant within cluster (Cluster-Randomized Trial), within variation is 0
        tau_within = tau_pooled

    # 3. Between-cluster (Cluster Means)
    cluster_df = df.groupby(cluster_col)[[outcome_col, treatment_col]].mean()
    X_between = sm.add_constant(cluster_df[treatment_col])
    if cluster_df[treatment_col].var() > 1e-8:
        fit_between = sm.OLS(cluster_df[outcome_col], X_between).fit()
        tau_between = float(fit_between.params[treatment_col])
    else:
        tau_between = 0.0

    # Paradox check: sign reversal between within and pooled, or severe divergence
    sign_reversal = (np.sign(tau_pooled) != np.sign(tau_within)) and abs(tau_within) > 0.05
    severe_bias = abs(tau_pooled - tau_within) > 1.0

    is_paradox = sign_reversal or severe_bias

    if sign_reversal:
        desc = (
            f"CRITICAL REVERSAL: Within-cluster causal effect is {tau_within:+.3f}, "
            f"but Pooled OLS estimates {tau_pooled:+.3f}! "
            f"Cluster confounding completely inverted the sign of the treatment effect."
        )
    elif severe_bias:
        desc = (
            f"SEVERE AGGREGATION BIAS: Within-cluster causal effect is {tau_within:+.3f}, "
            f"while Pooled OLS estimates {tau_pooled:+.3f} (Divergence: {abs(tau_pooled - tau_within):.3f})."
        )
    else:
        desc = "No Simpson's paradox detected. Within-cluster and pooled slopes are aligned."

    return SimpsonsDiagnostic(
        pooled_estimate=tau_pooled,
        within_estimate=tau_within,
        between_estimate=tau_between,
        is_paradox_detected=is_paradox,
        reversal_description=desc
    )
