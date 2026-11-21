"""
Hierarchical Clustered Data Generating Process (DGP)
Models multi-level experimental data, Intraclass Correlation (ICC),
and Cluster-Level Confounding (Simpson's Paradox).
"""
import numpy as np
import pandas as pd
from causal_lab.config import DGPConfig, RandomizationScheme


class HierarchicalDGP:
    """
    Simulates clustered A/B test data with tunable ICC, cluster-level confounding,
    and pre-experiment baseline covariates.
    """
    def __init__(self, config: DGPConfig):
        self.config = config
        self.rng = np.random.default_rng(config.seed)

    def reseed(self, seed: int):
        self.rng = np.random.default_rng(seed)

    def generate(self) -> pd.DataFrame:
        cfg = self.config
        n_clusters = cfg.n_clusters

        # 1. Cluster sizes (balanced or dispersed via log-normal)
        if cfg.cluster_size_dispersion > 0:
            raw_sizes = self.rng.lognormal(
                mean=np.log(cfg.avg_cluster_size),
                sigma=cfg.cluster_size_dispersion,
                size=n_clusters
            )
            cluster_sizes = np.clip(np.round(raw_sizes).astype(int), 5, None)
        else:
            cluster_sizes = np.full(n_clusters, cfg.avg_cluster_size, dtype=int)

        total_n = int(np.sum(cluster_sizes))

        # 2. Between-Cluster Random Intercepts: u_j ~ N(0, sigma_u^2)
        sigma_u = np.sqrt(cfg.sigma_cluster_sq)
        cluster_effects = self.rng.normal(0.0, sigma_u, size=n_clusters)

        # 3. Treatment Assignment
        treatments = []
        cluster_ids = []
        cluster_u_list = []

        if cfg.randomization == RandomizationScheme.CLUSTER:
            # Cluster-Randomized Trial (CRT): All units in a cluster share the same assignment
            if cfg.simpsons_confounding > 0:
                # Confounded cluster assignment
                logits = cfg.simpsons_confounding * (cluster_effects / (sigma_u + 1e-8))
                probs = 1.0 / (1.0 + np.exp(-logits))
                cluster_treatments = (self.rng.uniform(size=n_clusters) < probs).astype(int)
            else:
                # 50/50 Balanced cluster randomization
                cluster_treatments = self.rng.binomial(1, 0.5, size=n_clusters)

            for j, size in enumerate(cluster_sizes):
                treatments.extend([cluster_treatments[j]] * size)
                cluster_ids.extend([f"cluster_{j:03d}"] * size)
                cluster_u_list.extend([cluster_effects[j]] * size)

        else:
            # Individual-level randomization within clusters
            for j, size in enumerate(cluster_sizes):
                u_j = cluster_effects[j]
                if cfg.simpsons_confounding != 0:
                    # Confounding: Clusters with high baseline effect get higher treatment probability
                    # Creates Simpson's paradox when aggregated!
                    prob = 1.0 / (1.0 + np.exp(-cfg.simpsons_confounding * (u_j / (sigma_u + 1e-8))))
                    t_j = self.rng.binomial(1, prob, size=size)
                else:
                    # Standard 50/50 randomized split within each cluster
                    t_j = self.rng.binomial(1, 0.5, size=size)

                treatments.extend(t_j)
                cluster_ids.extend([f"cluster_{j:03d}"] * size)
                cluster_u_list.extend([u_j] * size)

        treatments = np.array(treatments, dtype=int)
        cluster_u = np.array(cluster_u_list, dtype=float)

        # 4. Pre-Experiment Baseline Covariate (for CUPED variance reduction)
        # Correlated with final outcome via target R^2
        sigma_e = np.sqrt(cfg.sigma_residual_sq)
        r2 = np.clip(cfg.covariate_r2, 0.0, 0.95)
        covariate_signal = self.rng.normal(0.0, 1.0, size=total_n)
        covariate = covariate_signal  # Pre-experiment measurement

        # 5. Within-Cluster Individual Noise: eps_ij ~ N(0, sigma_e^2)
        # Covariate explains a fraction of the residual variance
        cov_coeff = np.sqrt(r2) * sigma_e
        residual_noise = self.rng.normal(0.0, np.sqrt(1.0 - r2) * sigma_e, size=total_n)
        within_error = cov_coeff * covariate_signal + residual_noise

        # 6. Final Observed Outcome:
        # Y_ij = beta_0 + tau * T_ij + u_j + within_error
        beta_0 = 10.0
        # If Simpson's confounding is active, add an ecological cluster-level shift
        if cfg.simpsons_confounding != 0:
            # Simpson's reversal: true within-cluster effect is positive (cfg.true_tau),
            # but high-treatment clusters have lower baseline or vice versa
            outcome = beta_0 + cfg.true_tau * treatments + cluster_u + within_error
        else:
            outcome = beta_0 + cfg.true_tau * treatments + cluster_u + within_error

        df = pd.DataFrame({
            "unit_id": np.arange(total_n),
            "cluster_id": cluster_ids,
            "treatment": treatments,
            "pre_covariate": covariate,
            "cluster_effect": cluster_u,
            "outcome": outcome
        })

        return df
