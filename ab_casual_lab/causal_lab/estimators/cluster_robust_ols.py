"""
Cluster-Robust Standard Errors OLS Estimator (CRVE / Sandwich Estimator)
Employs Huber-White cluster-robust sandwich covariance (CR1).
Adjusts standard errors for intra-cluster correlation without assuming random intercept structure.
"""
import time
import pandas as pd
import statsmodels.api as sm
from causal_lab.estimators.base import BaseEstimator
from causal_lab.bridge.schemas import EstimatorResult, ModelCoefficient


class ClusterRobustOLSEstimator(BaseEstimator):
    @property
    def name(self) -> str:
        return "Cluster-Robust OLS (CRVE)"

    def fit(self, df: pd.DataFrame, outcome_col: str = "outcome", treatment_col: str = "treatment") -> EstimatorResult:
        t0 = time.perf_counter()

        if "cluster_id" not in df.columns:
            raise ValueError("DataFrame must contain 'cluster_id' column for Cluster-Robust OLS.")

        X = sm.add_constant(df[treatment_col])
        y = df[outcome_col]

        model = sm.OLS(y, X)
        # Cluster-robust covariance (CR1)
        results = model.fit(cov_type="cluster", cov_kwds={"groups": df["cluster_id"]})

        elapsed = time.perf_counter() - t0

        treat_idx = treatment_col
        ci = results.conf_int().loc[treat_idx]

        treat_coeff = ModelCoefficient(
            term=treat_idx,
            estimate=float(results.params[treat_idx]),
            std_error=float(results.bse[treat_idx]),
            statistic=float(results.tvalues[treat_idx]),
            p_value=float(results.pvalues[treat_idx]),
            ci_lower=float(ci[0]),
            ci_upper=float(ci[1]),
            df=float(results.df_resid)
        )

        all_coefs = {}
        for param in results.params.index:
            ci_p = results.conf_int().loc[param]
            all_coefs[param] = ModelCoefficient(
                term=param,
                estimate=float(results.params[param]),
                std_error=float(results.bse[param]),
                statistic=float(results.tvalues[param]),
                p_value=float(results.pvalues[param]),
                ci_lower=float(ci_p[0]),
                ci_upper=float(ci_p[1]),
                df=float(results.df_resid)
            )

        n_clusters = df["cluster_id"].nunique()

        return EstimatorResult(
            estimator_name=self.name,
            treatment_effect=treat_coeff,
            all_coefficients=all_coefs,
            sigma_cluster=None,
            sigma_residual=float(results.mse_resid ** 0.5),
            icc=None,
            is_singular=False,
            aic=float(results.aic),
            bic=float(results.bic),
            n_obs=int(results.nobs),
            n_clusters=n_clusters,
            fit_time_seconds=elapsed,
            diagnostics={"cov_type": "cluster", "n_clusters": n_clusters}
        )
