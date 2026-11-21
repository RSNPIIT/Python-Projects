"""
Rich Terminal Report Generator for Clustered Causal Comparisons
"""
from typing import Sequence
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from causal_lab.bridge.schemas import EstimatorResult
from causal_lab.diagnostics.moulton import MoultonDiagnostic
from causal_lab.diagnostics.simpsons_detector import SimpsonsDiagnostic

console = Console()


def print_comparison_table(results: Sequence[EstimatorResult], true_tau: float):
    """Prints a structured comparison table across fitted causal estimators."""
    table = Table(
        title="[bold cyan]Causal Estimator Performance & Clustered Inference Comparison[/bold cyan]",
        show_header=True,
        header_style="bold magenta",
        border_style="dim"
    )

    table.add_column("Estimator", style="bold white", width=26)
    table.add_column("Estimate", justify="right", width=10)
    table.add_column("Std. Error", justify="right", width=11)
    table.add_column("95% CI", justify="center", width=22)
    table.add_column("t / z", justify="right", width=8)
    table.add_column("p-value", justify="right", width=10)
    table.add_column("df", justify="right", width=8)
    table.add_column("Sig (p<.05)", justify="center", width=12)
    table.add_column("Time (ms)", justify="right", width=10)

    for res in results:
        t_eff = res.treatment_effect
        sig_str = "[bold red]REJECT H0[/bold red]" if t_eff.is_significant else "[green]ACCEPT H0[/green]"
        ci_str = f"[{t_eff.ci_lower:+.3f}, {t_eff.ci_upper:+.3f}]"
        df_str = f"{t_eff.df:.1f}" if t_eff.df is not None else "-"
        time_ms = f"{res.fit_time_seconds * 1000.0:.1f}"

        # Color estimate green if close to true_tau, red if sign inverted or biased
        est_diff = abs(t_eff.estimate - true_tau)
        est_color = "green" if est_diff < 0.35 else ("yellow" if est_diff < 0.8 else "bold red")
        est_styled = f"[{est_color}]{t_eff.estimate:+.3f}[/{est_color}]"

        p_str = f"{t_eff.p_value:.4f}" if t_eff.p_value >= 0.0001 else "< 0.0001"

        table.add_row(
            res.estimator_name,
            est_styled,
            f"{t_eff.std_error:.4f}",
            ci_str,
            f"{t_eff.statistic:+.2f}",
            p_str,
            df_str,
            sig_str,
            time_ms
        )

    console.print(table)
    console.print(f"[dim]True Treatment Effect (Ground Truth): [bold yellow]tau = {true_tau:+.3f}[/bold yellow][/dim]\n")


def print_moulton_diagnostic(diag: MoultonDiagnostic):
    """Renders the Moulton design effect and effective sample size breakdown."""
    content = Text()
    content.append("• Observations: ", style="bold")
    content.append(f"{diag.n_obs:,} across {diag.n_clusters} clusters (avg size: {diag.avg_cluster_size:.1f})\n")

    content.append("• Outcome Intraclass Correlation (ICC / rho_Y): ", style="bold")
    content.append(f"{diag.outcome_icc:.4f}\n", style="bold yellow")

    content.append("• Treatment Allocation Clusteredness (rho_T): ", style="bold")
    content.append(f"{diag.treatment_icc:.4f}\n")

    content.append("• Moulton Design Effect (DEFF): ", style="bold")
    content.append(f"{diag.design_effect:.2f}x\n", style="bold red" if diag.design_effect > 1.5 else "green")

    content.append("• Standard Error Multiplier: ", style="bold")
    content.append(f"{diag.moulton_factor:.2f}x (Naive OLS standard errors are deflated by this ratio!)\n", style="yellow")

    content.append("• Effective Sample Size (ESS): ", style="bold")
    content.append(f"{diag.effective_sample_size:.1f} units (out of {diag.n_obs:,} nominal observations)\n", style="cyan")

    content.append("• Predicted Naive False Positive Rate: ", style="bold")
    content.append(
        f"{diag.type_1_inflation_estimate * 100.0:.1f}% (Nominal alpha: 5.0%)\n",
        style="bold red" if diag.type_1_inflation_estimate > 0.10 else "green"
    )

    panel = Panel(
        content,
        title="[bold yellow]Moulton Factor & Design Effect Diagnostic[/bold yellow]",
        border_style="yellow",
        expand=False
    )
    console.print(panel)


def print_simpsons_diagnostic(diag: SimpsonsDiagnostic):
    """Renders Simpson's Paradox diagnostic alert."""
    if diag.is_paradox_detected:
        color = "red"
        title = "[bold red]CRITICAL ALERT: Simpson's Paradox / Confounding Detected[/bold red]"
    else:
        color = "green"
        title = "[bold green]Simpson's Diagnostic: Consistent Slopes[/bold green]"

    content = Text()
    content.append("• Pooled OLS Slope: ", style="bold")
    content.append(f"{diag.pooled_estimate:+.3f}\n")
    content.append("• Within-Cluster Causal Slope: ", style="bold")
    content.append(f"{diag.within_estimate:+.3f}\n", style="bold green")
    content.append("• Between-Cluster Ecological Slope: ", style="bold")
    content.append(f"{diag.between_estimate:+.3f}\n")
    content.append(f"\n{diag.reversal_description}", style="bold " + color)

    panel = Panel(content, title=title, border_style=color, expand=False)
    console.print(panel)
