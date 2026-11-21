"""
Command-Line Application and Interactive Workflow Runner
"""
import sys
from rich.console import Console
from rich.panel import Panel

from causal_lab.config import DGPConfig, BenchmarkConfig, RandomizationScheme
from causal_lab.simulation.generator import HierarchicalDGP
from causal_lab.simulation import scenarios
from causal_lab.simulation.benchmarks import MonteCarloBenchmark, print_benchmark_table
from causal_lab.bridge.r_bridge import RBridge
from causal_lab.estimators.naive_ols import NaiveOLSEstimator
from causal_lab.estimators.cluster_robust_ols import ClusterRobustOLSEstimator
from causal_lab.estimators.mixed_effects import MixedEffectsEstimator
from causal_lab.estimators.cuped_cluster import CUPEDMixedEffectsEstimator
from causal_lab.diagnostics.moulton import compute_moulton_diagnostic
from causal_lab.diagnostics.simpsons_detector import detect_simpsons_paradox
from causal_lab.diagnostics.report import (
    print_comparison_table,
    print_moulton_diagnostic,
    print_simpsons_diagnostic
)

console = Console()


def run_experiment_deep_dive(scenario_type: str = "simpsons"):
    """Runs a single-shot detailed deep-dive comparison across all estimators."""
    console.print(Panel(
        f"[bold cyan]Running Causal Deep-Dive: Scenario '{scenario_type.upper()}'[/bold cyan]",
        border_style="cyan"
    ))

    # Select scenario
    if scenario_type == "simpsons":
        cfg = scenarios.get_simpsons_reversal_scenario()
    elif scenario_type == "null":
        cfg = scenarios.get_high_icc_null_scenario()
    elif scenario_type == "cluster_crt":
        cfg = scenarios.get_cluster_randomized_scenario()
    else:
        cfg = scenarios.get_cuped_efficiency_scenario()

    # Generate data
    dgp = HierarchicalDGP(cfg)
    df = dgp.generate()

    console.print(f"[dim]Generated {len(df):,} observations across {cfg.n_clusters} clusters (Avg size: {cfg.avg_cluster_size}).[/dim]\n")

    # Initialize estimators
    bridge = RBridge()
    estimators = [
        NaiveOLSEstimator(),
        ClusterRobustOLSEstimator(),
        MixedEffectsEstimator(bridge=bridge),
        CUPEDMixedEffectsEstimator(bridge=bridge)
    ]

    # Fit estimators
    results = []
    for est in estimators:
        try:
            res = est.fit(df)
            results.append(res)
        except Exception as e:
            console.print(f"[red]Error fitting {est.name}: {e}[/red]")

    # 1. Print Estimator Comparison Table
    print_comparison_table(results, true_tau=cfg.true_tau)

    # 2. Extract ICC from Mixed Model
    lmm_res = next((r for r in results if "Mixed-Effects" in r.estimator_name), None)
    est_icc = lmm_res.icc if lmm_res and lmm_res.icc is not None else cfg.icc

    # 3. Moulton Factor Diagnostic
    moulton_diag = compute_moulton_diagnostic(
        df=df,
        outcome_icc=est_icc,
        outcome_col="outcome",
        treatment_col="treatment",
        cluster_col="cluster_id"
    )
    print_moulton_diagnostic(moulton_diag)

    # 4. Simpson's Paradox Diagnostic
    simpsons_diag = detect_simpsons_paradox(
        df=df,
        outcome_col="outcome",
        treatment_col="treatment",
        cluster_col="cluster_id"
    )
    print_simpsons_diagnostic(simpsons_diag)


def run_monte_carlo_validation(n_reps: int = 50):
    """Runs Monte Carlo benchmark proving Type-I error inflation under high ICC."""
    console.print(Panel(
        f"[bold yellow]Monte Carlo Empirical Validation: Type-I Error & Coverage ({n_reps} Replications)[/bold yellow]\n"
        "[dim]DGP: Null Hypothesis (True tau = 0.0), Cluster Randomization, ICC = 0.35.[/dim]",
        border_style="yellow"
    ))

    cfg = scenarios.get_high_icc_null_scenario()
    bench_cfg = BenchmarkConfig(n_replications=n_reps, alpha=0.05, dgp=cfg)

    bridge = RBridge()
    estimators = [
        NaiveOLSEstimator(),
        ClusterRobustOLSEstimator(),
        MixedEffectsEstimator(bridge=bridge)
    ]

    benchmark = MonteCarloBenchmark(estimators, bench_cfg)
    summaries = benchmark.run()

    print_benchmark_table(summaries, true_tau=cfg.true_tau, alpha=0.05)
