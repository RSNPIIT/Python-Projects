#!/usr/bin/env python3
"""
A/B Causal Lab - Main Command-Line Application
Production Clustered Experimentation & Mixed-Effects Causal Laboratory
"""
import sys
import argparse
from pathlib import Path

# Ensure root package directory is in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from rich.console import Console
from rich.panel import Panel
from causal_lab.cli.app import run_experiment_deep_dive, run_monte_carlo_validation

console = Console()

BANNER = """[bold cyan]
   █████╗ ██████╗      ██████╗ █████╗ ██╗   ██╗███████╗ █████╗ ██╗     
  ██╔══██╗██╔══██╗    ██╔════╝██╔══██╗██║   ██║██╔════╝██╔══██╗██║     
  ███████║██████╔╝    ██║     ███████║██║   ██║███████╗███████║██║     
  ██╔══██║██╔══██╗    ██║     ██╔══██║██║   ██║╚════██║██╔══██║██║     
  ██║  ██║██████╔╝    ╚██████╗██║  ██║╚██████╔╝███████║██║  ██║███████╗
  ╚═╝  ╚═╝╚═════╝      ╚═════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝╚══════╝
[/bold cyan]
[dim bold white]A/B Causal Lab • Clustered Experimentation & Mixed-Effects Causal Inference Engine[/dim bold white]
[dim]Integration of Python Scientific Stack (NumPy, Pandas, Statsmodels) with Pure R (lme4, lmerTest)[/dim]
"""

def main():
    parser = argparse.ArgumentParser(
        description="A/B Causal Lab: Professional Clustered Experimentation & Mixed-Effects Causal Testing"
    )
    parser.add_argument(
        "--mode",
        choices=["deep-dive", "benchmark", "all"],
        default="all",
        help="Execution mode: 'deep-dive' (single detailed run), 'benchmark' (Monte Carlo), or 'all' (both)."
    )
    parser.add_argument(
        "--scenario",
        choices=["simpsons", "null", "cluster_crt", "cuped"],
        default="simpsons",
        help="Scenario for deep-dive: 'simpsons', 'null', 'cluster_crt', or 'cuped'."
    )
    parser.add_argument(
        "--reps",
        type=int,
        default=30,
        help="Number of Monte Carlo replications for benchmark mode (default: 30)."
    )

    args = parser.parse_args()

    console.print(BANNER)

    if args.mode in ("deep-dive", "all"):
        console.print("[bold]1. Executing Causal Deep-Dive Comparison...[/bold]\n")
        run_experiment_deep_dive(scenario_type=args.scenario)

    if args.mode in ("benchmark", "all"):
        console.print("\n[bold]2. Executing Monte Carlo Empirical Validation...[/bold]\n")
        run_monte_carlo_validation(n_reps=args.reps)

    console.print("\n[bold green]✓ A/B Causal Lab execution completed successfully.[/bold green]\n")


if __name__ == "__main__":
    main()
