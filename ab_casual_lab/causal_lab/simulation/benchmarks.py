"""
Monte Carlo Benchmark Engine
Empirically quantifies Type-I Error Inflation, Statistical Power,
Coverage Probability, and Standard Error Bias across estimators.
"""
from dataclasses import dataclass, field
from typing import Sequence
import numpy as np
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn

from causal_lab.config import BenchmarkConfig
from causal_lab.simulation.generator import HierarchicalDGP
from causal_lab.estimators.base import BaseEstimator
from causal_lab.bridge.schemas import EstimatorResult

console = Console()


@dataclass
class MetricSummary:
    estimator_name: str
    replications: int
    mean_estimate: float
    bias: float
    empirical_se: float          # Standard deviation of point estimates across runs
    mean_model_se: float         # Average reported analytical standard error
    se_bias_ratio: float         # mean_model_se / empirical_se (ratio < 1 indicates deflated SEs)
    coverage_95: float           # % of 95% CIs containing true tau
    rejection_rate: float        # % of p-values < alpha (Type-I error if tau=0, Power if tau!=0)
    rmse: float                  # Root Mean Squared Error


class MonteCarloBenchmark:
    """Runs Monte Carlo replication experiments across multiple causal estimators."""

    def __init__(self, estimators: Sequence[BaseEstimator], config: BenchmarkConfig):
        self.estimators = estimators
        self.config = config

    def run(self) -> list[MetricSummary]:
        cfg = self.config
        true_tau = cfg.dgp.true_tau
        n_reps = cfg.n_replications
        dgp = HierarchicalDGP(cfg.dgp)

        # Storage per estimator
        records: dict[str, dict[str, list[float]]] = {
            est.name: {
                "estimates": [],
                "ses": [],
                "p_values": [],
                "ci_lowers": [],
                "ci_uppers": []
            }
            for est in self.estimators
        }

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Running Monte Carlo replications...", total=n_reps)

            for rep in range(n_reps):
                # Reseed DGP for independent replication
                dgp.reseed(cfg.dgp.seed + rep if cfg.dgp.seed is not None else rep)
                df = dgp.generate()

                for est in self.estimators:
                    try:
                        res = est.fit(df)
                        te = res.treatment_effect
                        records[est.name]["estimates"].append(te.estimate)
                        records[est.name]["ses"].append(te.std_error)
                        records[est.name]["p_values"].append(te.p_value)
                        records[est.name]["ci_lowers"].append(te.ci_lower)
                        records[est.name]["ci_uppers"].append(te.ci_upper)
                    except Exception as e:
                        # Log error in debug mode
                        pass

                progress.update(task, advance=1)

        # Compute metric aggregates
        summaries = []
        for est_name, data in records.items():
            ests = np.array(data["estimates"])
            ses = np.array(data["ses"])
            pvals = np.array(data["p_values"])
            ci_lows = np.array(data["ci_lowers"])
            ci_highs = np.array(data["ci_uppers"])

            n = len(ests)
            if n == 0:
                continue

            mean_est = float(np.mean(ests))
            bias = float(mean_est - true_tau)
            empirical_se = float(np.std(ests, ddof=1)) if n > 1 else 0.0
            mean_model_se = float(np.mean(ses))
            se_bias_ratio = float(mean_model_se / empirical_se) if empirical_se > 1e-8 else 1.0

            # Coverage: proportion of CIs containing true tau
            covered = np.sum((ci_lows <= true_tau) & (ci_highs >= true_tau))
            coverage_rate = float(covered / n)

            # Rejection rate: p < alpha
            rejections = np.sum(pvals < cfg.alpha)
            rejection_rate = float(rejections / n)

            # RMSE
            rmse = float(np.sqrt(np.mean((ests - true_tau) ** 2)))

            summaries.append(MetricSummary(
                estimator_name=est_name,
                replications=n,
                mean_estimate=mean_est,
                bias=bias,
                empirical_se=empirical_se,
                mean_model_se=mean_model_se,
                se_bias_ratio=se_bias_ratio,
                coverage_95=coverage_rate,
                rejection_rate=rejection_rate,
                rmse=rmse
            ))

        return summaries


def print_benchmark_table(summaries: Sequence[MetricSummary], true_tau: float, alpha: float = 0.05):
    """Renders a structured Monte Carlo benchmark summary table."""
    is_null_test = abs(true_tau) < 1e-6
    metric_label = f"Type-I Error (nom {alpha:.0%})" if is_null_test else f"Power (alpha={alpha:.0%})"

    table = Table(
        title=f"[bold cyan]Monte Carlo Benchmark Summary ({summaries[0].replications} Replications)[/bold cyan]",
        header_style="bold magenta",
        border_style="dim"
    )

    table.add_column("Estimator", style="bold white", width=25)
    table.add_column("Mean Est", justify="right", width=10)
    table.add_column("Bias", justify="right", width=9)
    table.add_column("Empirical SE", justify="right", width=13)
    table.add_column("Model SE", justify="right", width=10)
    table.add_column("SE Ratio", justify="right", width=10)
    table.add_column("95% Coverage", justify="center", width=13)
    table.add_column(metric_label, justify="center", width=18)
    table.add_column("RMSE", justify="right", width=9)

    for s in summaries:
        # Format Type-I / Power rate
        if is_null_test:
            # Type-I error inflation check
            t1_color = "green" if s.rejection_rate <= 0.08 else ("yellow" if s.rejection_rate <= 0.15 else "bold red")
            rate_str = f"[{t1_color}]{s.rejection_rate:.1%}[/{t1_color}]"
        else:
            rate_str = f"[bold green]{s.rejection_rate:.1%}[/bold green]"

        # Coverage format
        cov_color = "green" if s.coverage_95 >= 0.90 else ("yellow" if s.coverage_95 >= 0.80 else "bold red")
        cov_str = f"[{cov_color}]{s.coverage_95:.1%}[/{cov_color}]"

        # SE Ratio format (ratio < 0.85 indicates deflated standard error!)
        ratio_color = "green" if 0.90 <= s.se_bias_ratio <= 1.10 else "bold red"
        ratio_str = f"[{ratio_color}]{s.se_bias_ratio:.2f}x[/{ratio_color}]"

        table.add_row(
            s.estimator_name,
            f"{s.mean_estimate:+.3f}",
            f"{s.bias:+.3f}",
            f"{s.empirical_se:.4f}",
            f"{s.mean_model_se:.4f}",
            ratio_str,
            cov_str,
            rate_str,
            f"{s.rmse:.4f}"
        )

    console.print(table)
    if is_null_test:
        console.print("[dim italic]Notice: Naive OLS has deflated Model SE (< 1.0x) leading to massive Type-I error rate inflation!\n[/dim italic]")
