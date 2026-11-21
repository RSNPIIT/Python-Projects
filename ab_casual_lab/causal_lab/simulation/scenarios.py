"""
Benchmark Experiment Scenarios for Causal Testing
"""
from causal_lab.config import DGPConfig, RandomizationScheme


def get_high_icc_null_scenario() -> DGPConfig:
    """
    Null hypothesis scenario (true tau = 0) with substantial ICC (0.35).
    Exposes extreme False Positive Rate (Type I Error inflation) of naive OLS.
    """
    return DGPConfig(
        n_clusters=40,
        avg_cluster_size=60,
        cluster_size_dispersion=0.25,
        true_tau=0.0,
        icc=0.35,
        total_variance=4.0,
        simpsons_confounding=0.0,
        randomization=RandomizationScheme.CLUSTER,
        covariate_r2=0.0,
        seed=101
    )


def get_simpsons_reversal_scenario() -> DGPConfig:
    """
    Simpson's Paradox / Confounded Cluster Rollout:
    True individual-level causal effect is POSITIVE (+2.0),
    but high-volume/high-performing clusters received less treatment,
    causing naive OLS to estimate a NEGATIVE treatment effect!
    Mixed-effects / Fixed-effects models correctly recover +2.0.
    """
    return DGPConfig(
        n_clusters=35,
        avg_cluster_size=50,
        cluster_size_dispersion=0.30,
        true_tau=2.0,
        icc=0.40,
        total_variance=5.0,
        simpsons_confounding=-1.8,  # Negative correlation between cluster baseline and treatment probability
        randomization=RandomizationScheme.INDIVIDUAL,
        covariate_r2=0.0,
        seed=202
    )


def get_cluster_randomized_scenario() -> DGPConfig:
    """
    Cluster-Randomized Trial (Geo / City level A/B test):
    Entire cities assigned to Treatment or Control.
    Large Moulton Design Effect requires cluster-level degrees of freedom.
    """
    return DGPConfig(
        n_clusters=40,
        avg_cluster_size=50,
        cluster_size_dispersion=0.15,
        true_tau=1.2,
        icc=0.20,
        total_variance=4.0,
        simpsons_confounding=0.0,
        randomization=RandomizationScheme.CLUSTER,
        covariate_r2=0.0,
        seed=303
    )


def get_cuped_efficiency_scenario() -> DGPConfig:
    """
    Clustered experiment with strong pre-experiment baseline metric (R^2 = 0.55).
    Evaluates variance reduction via Mixed-Effects ANCOVA/CUPED.
    """
    return DGPConfig(
        n_clusters=50,
        avg_cluster_size=40,
        cluster_size_dispersion=0.20,
        true_tau=1.0,
        icc=0.25,
        total_variance=4.0,
        simpsons_confounding=0.0,
        randomization=RandomizationScheme.INDIVIDUAL,
        covariate_r2=0.55,
        seed=404
    )
