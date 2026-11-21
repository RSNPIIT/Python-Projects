"""
Naive Ordinary Least Squares (OLS) Estimator
Ignores cluster hierarchy and intraclass correlation (i.i.d. assumption).
Suffers from Moulton standard error deflation and severe Type-I error inflation.
"""
import time
import pandas as pd
import statsmodels.api as sm
from causal_lab.estimators.base import BaseEstimator
from causal_lab.bridge.schemas import EstimatorResult, ModelCoefficient


class NaiveOLSEstimator(BaseEstimator):
    @property
    def name(self) -> str:
        return "Naive OLS (Unclustered)"

    def fit(self, df: pd.DataFrame, outcome_col: str = "outcome", treatment_col: str = "treatment") -> EstimatorResult:
        t0 = time.perf_counter()

        X = sm.add_constant(df[treatment_col])
        y = df[outcome_col]

        model = sm.OLS(y, X)
        results = model.fit()

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

        n_clusters = df["cluster_id"].nunique() if "cluster_id" in df.columns else 1

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
            diagnostics={"cov_type": "nonrobust"}
        )
