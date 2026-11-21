# A/B Causal Lab • Professional Clustered Experimentation & Mixed-Effects Engine

A causal inference laboratory bridging the **Python scientific ecosystem** (`numpy`, `pandas`, `statsmodels`) with **R's mixed-effects modeling architecture** (`lme4`, `lmerTest`).

Designed to model and resolve the three critical failure modes of classical A/B testing in hierarchical/clustered environments:
1. **Moulton Standard Error Deflation**: Severe Type-I error inflation (false positives jumping from 5% to 30%–60%) when observations share unobserved cluster variance.
2. **Simpson's Paradox / Ecological Confounding**: Treatment rollout correlated with cluster baselines, inverting the sign of the estimated treatment effect.
3. **Inefficient Variance Reduction**: How to correctly apply CUPED (ANCOVA) in the presence of hierarchical random intercepts.

---

## 📐 Mathematical Formulation

### 1. Hierarchical Linear Mixed Model (LMM / HLM)
For unit $i$ in cluster $j \in \{1, \dots, J\}$:
$$Y_{ij} = \beta_0 + \tau T_{ij} + X_{ij}\beta + u_j + \varepsilon_{ij}$$
where:
- $\tau$ is the true Average Treatment Effect (ATE).
- $u_j \sim \mathcal{N}(0, \sigma_u^2)$ is the between-cluster random intercept.
- $\varepsilon_{ij} \sim \mathcal{N}(0, \sigma_\varepsilon^2)$ is the within-cluster idiosyncratic error.

### 2. Intraclass Correlation Coefficient (ICC)
$$\rho_{\text{ICC}} = \frac{\sigma_u^2}{\sigma_u^2 + \sigma_\varepsilon^2}$$

### 3. The Moulton Factor & Design Effect
When observations within a cluster are correlated, standard errors estimated by naive OLS are deflated by the **Moulton Factor** $\sqrt{\text{DEFF}}$:
$$\text{DEFF} = 1 + (\tilde{m} - 1) \cdot \rho_Y \cdot \rho_T$$
where:
- $\tilde{m}$ is the effective cluster size accounting for size dispersion.
- $\rho_Y$ is the outcome ICC.
- $\rho_T$ is the treatment allocation ICC ($\rho_T = 1.0$ in Cluster-Randomized Trials).
- **Effective Sample Size (ESS)**:
  $$\text{ESS} = \frac{N}{\text{DEFF}}$$

---

## 🏛️ Project Architecture

```
ab_causal_lab/
├── r_engine/
│   ├── mixed_models.R         # Pure R: lme4/lmerTest with Satterthwaite DF & REML
│   └── diagnostics.R          # Residual normality & singularity checks
├── causal_lab/
│   ├── config.py              # Strongly-typed DGP & benchmark configurations
│   ├── simulation/
│   │   ├── generator.py       # Hierarchical DGP with ICC & Simpson's confounding
│   │   ├── scenarios.py       # Curated causal benchmark scenarios
│   │   └── benchmarks.py      # Monte Carlo empirical validator (Type-I error, Power, Coverage)
│   ├── bridge/
│   │   ├── r_bridge.py        # In-process rpy2 bridge with CLI subprocess fallback
│   │   └── schemas.py         # Standardized typed output schemas
│   ├── estimators/
│   │   ├── base.py            # Abstract BaseEstimator interface
│   │   ├── naive_ols.py       # Naive OLS (i.i.d. assumption)
│   │   ├── cluster_robust_ols.py # Huber-White Cluster-Robust OLS (CRVE)
│   │   ├── mixed_effects.py   # Linear Mixed-Effects Model (via R lme4/lmerTest)
│   │   └── cuped_cluster.py   # CUPED variance reduction with cluster random effects
│   ├── diagnostics/
│   │   ├── moulton.py         # Moulton factor, DEFF & Effective Sample Size (ESS)
│   │   ├── simpsons_detector.py # Within- vs. between-cluster slope decomposition
│   │   └── report.py          # Rich terminal formatted tables and diagnostic panels
│   └── cli/
│       └── app.py             # Interactive CLI execution workflows
├── tests/
│   ├── test_simulation.py     # DGP tests
│   ├── test_estimators.py     # Estimator property tests
│   └── test_bridge.py         # R bridge execution tests
├── main.py                    # Top-level entrypoint
├── pyproject.toml
└── requirements.txt
```

---

## 🚀 Quickstart & Execution

### 1. Run the Full Laboratory (Deep-Dive + Monte Carlo Benchmark):
```bash
/Users/ramrupsatpati/Desktop/Python/venv/bin/python main.py
```

### 2. Run Specific Scenario Deep-Dives:
```bash
# Simpson's Paradox Reversal Demonstration
/Users/ramrupsatpati/Desktop/Python/venv/bin/python main.py --mode deep-dive --scenario simpsons

# High ICC Null Hypothesis (Type-I Error Inflation Demonstration)
/Users/ramrupsatpati/Desktop/Python/venv/bin/python main.py --mode deep-dive --scenario null

# Cluster-Randomized Trial (Geo / City level A/B test)
/Users/ramrupsatpati/Desktop/Python/venv/bin/python main.py --mode deep-dive --scenario cluster_crt

# CUPED Variance Reduction with Hierarchical Random Intercepts
/Users/ramrupsatpati/Desktop/Python/venv/bin/python main.py --mode deep-dive --scenario cuped
```

### 3. Run Monte Carlo Benchmark (50 Replications):
```bash
/Users/ramrupsatpati/Desktop/Python/venv/bin/python main.py --mode benchmark --reps 50
```

### 4. Run Unit Tests:
```bash
/Users/ramrupsatpati/Desktop/Python/venv/bin/pytest tests/
```
