"""
Typed Python-R Bridge Interface
Provides two execution backends:
1. In-process high-performance rpy2 connection (Primary)
2. Subprocess Rscript execution with JSON IPC (Robust Fallback)
"""
import os
import json
import time
import tempfile
import subprocess
from pathlib import Path
from typing import Optional
import pandas as pd

from causal_lab.bridge.schemas import EstimatorResult, ModelCoefficient

SCRIPT_DIR = Path(__file__).resolve().parent.parent.parent
R_SCRIPT_PATH = SCRIPT_DIR / "r_engine" / "mixed_models.R"


class RBridge:
    """Enterprise-grade bridge interfacing Python with R lme4/lmerTest."""

    def __init__(self, prefer_rpy2: bool = True):
        self.prefer_rpy2 = prefer_rpy2
        self._rpy2_initialized = False
        self._r_fit_fn = None

        if self.prefer_rpy2:
            self._init_rpy2()

    def _init_rpy2(self):
        try:
            import rpy2.robjects as ro
            from rpy2.robjects import pandas2ri
            from rpy2.robjects.packages import importr

            pandas2ri.activate()
            # Source R mixed models script
            if not R_SCRIPT_PATH.exists():
                raise FileNotFoundError(f"R script not found at {R_SCRIPT_PATH}")

            ro.r(f'source("{R_SCRIPT_PATH.as_posix()}")')
            self._r_fit_fn = ro.globalenv["fit_mixed_model"]
            self._rpy2_initialized = True
        except Exception as e:
            self._rpy2_initialized = False

    def fit_mixed_effects(
        self,
        df: pd.DataFrame,
        formula: str = "outcome ~ treatment + (1 | cluster_id)",
        reml: bool = True
    ) -> EstimatorResult:
        """
        Fits a linear mixed-effects model using R lme4/lmerTest.
        Uses in-process rpy2 if available, otherwise delegates to Rscript CLI.
        """
        t0 = time.perf_counter()

        if self._rpy2_initialized and self._r_fit_fn is not None:
            try:
                return self._fit_via_rpy2(df, formula, reml, t0)
            except Exception:
                # Graceful fallback to subprocess on rpy2 runtime error
                pass

        return self._fit_via_subprocess(df, formula, reml, t0)

    def _fit_via_rpy2(
        self,
        df: pd.DataFrame,
        formula: str,
        reml: bool,
        start_time: float
    ) -> EstimatorResult:
        import rpy2.robjects as ro
        from rpy2.robjects import pandas2ri

        # Convert DataFrame to R
        with (ro.default_converter + pandas2ri.converter).context():
            r_df = ro.conversion.get_conversion().py2rpy(df)

        r_result = self._r_fit_fn(r_df, formula_str=formula, REML=reml)

        # Unpack R list into Python dict
        py_res = {}
        for name in r_result.names:
            val = r_result.rx2(name)
            if name == "fixed_effects":
                py_res["fixed_effects"] = self._unpack_r_fixed_effects(val)
            else:
                py_res[name] = val[0] if hasattr(val, "__len__") and len(val) == 1 else val

        return self._build_estimator_result(py_res, time.perf_counter() - start_time)

    def _unpack_r_fixed_effects(self, r_fe_list) -> dict[str, dict]:
        fe_dict = {}
        for term_name in r_fe_list.names:
            term_obj = r_fe_list.rx2(term_name)
            item = {}
            for field in term_obj.names:
                val = term_obj.rx2(field)
                item[field] = val[0] if hasattr(val, "__len__") and len(val) == 1 else val
            fe_dict[term_name] = item
        return fe_dict

    def _fit_via_subprocess(
        self,
        df: pd.DataFrame,
        formula: str,
        reml: bool,
        start_time: float
    ) -> EstimatorResult:
        """Fallback via Rscript executable with JSON payload."""
        with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False) as in_f:
            in_path = in_f.name
            df.to_json(in_path, orient="records")

        with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False) as out_f:
            out_path = out_f.name

        try:
            cmd = ["Rscript", str(R_SCRIPT_PATH), in_path, formula, out_path]
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)

            with open(out_path, "r", encoding="utf-8") as fp:
                data = json.load(fp)

            return self._build_estimator_result(data, time.perf_counter() - start_time)

        finally:
            for p in (in_path, out_path):
                if os.path.exists(p):
                    try:
                        os.remove(p)
                    except OSError:
                        pass

    def _build_estimator_result(self, data: dict, elapsed: float) -> EstimatorResult:
        fe_raw = data.get("fixed_effects", {})
        coefficients = {}

        for term, vals in fe_raw.items():
            coefficients[term] = ModelCoefficient(
                term=term,
                estimate=float(vals.get("estimate", 0.0)),
                std_error=float(vals.get("std_error", 0.0)),
                statistic=float(vals.get("statistic", 0.0)),
                p_value=float(vals.get("p_value", 1.0)),
                ci_lower=float(vals.get("ci_lower", 0.0)),
                ci_upper=float(vals.get("ci_upper", 0.0)),
                df=float(vals["df"]) if vals.get("df") is not None else None
            )

        # Primary treatment effect
        treat_coeff = (
            coefficients.get("treatment") or
            coefficients.get("treatment:1") or
            next((c for k, c in coefficients.items() if "treatment" in k.lower()), None)
        )

        if treat_coeff is None:
            treat_coeff = ModelCoefficient("treatment", 0.0, 0.0, 0.0, 1.0, 0.0, 0.0)

        return EstimatorResult(
            estimator_name=f"LMM ({data.get('engine', 'R lme4')})",
            treatment_effect=treat_coeff,
            all_coefficients=coefficients,
            sigma_cluster=float(data.get("sigma_cluster", 0.0)),
            sigma_residual=float(data.get("sigma_residual", 0.0)),
            icc=float(data.get("icc", 0.0)),
            is_singular=bool(data.get("is_singular", False)),
            aic=float(data.get("aic", 0.0)) if data.get("aic") else None,
            bic=float(data.get("bic", 0.0)) if data.get("bic") else None,
            n_obs=int(data.get("n_obs", 0)),
            n_clusters=int(data.get("n_clusters", 0)),
            fit_time_seconds=elapsed,
            diagnostics={"engine": data.get("engine")}
        )
