#!/usr/bin/env python3
"""
Econometric Forecast Engine - CLI & Uvicorn Application Entrypoint
"""
import sys
import argparse
from pathlib import Path

# Ensure root directory is in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import numpy as np
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

BANNER = """[bold cyan]
  ███████╗ ██████╗ ██████╗ ███╗   ██╗ ██████╗ ███╗   ███╗███████╗████████╗██████╗ ██╗ ██████╗
  ██╔════╝██╔════╝██╔═══██╗████╗  ██║██╔═══██╗████╗ ████║██╔════╝╚══██╔══╝██╔══██╗██║██╔════╝
  █████╗  ██║     ██║   ██║██╔██╗ ██║██║   ██║██╔████╔██║█████╗     ██║   ██████╔╝██║██║     
  ██╔══╝  ██║     ██║   ██║██║╚██╗██║██║   ██║██║╚██╔╝██║██╔══╝     ██║   ██╔══██╗██║██║     
  ███████╗╚██████╗╚██████╔╝██║ ╚████║╚██████╔╝██║ ╚═╝ ██║███████╗   ██║   ██║  ██║██║╚██████╗
  ╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝ ╚═════╝
[/bold cyan]
[dim bold white]Econometric Forecast Engine • Hybrid Python-R Production Time Series Architecture[/dim bold white]
[dim]State-Space ETS, Auto-ARIMA, Johansen Cointegration, VAR, & Rolling-Origin Backtesting[/dim]
"""


def run_pipeline_demo():
    """Runs a full end-to-end econometric forecasting and diagnostic demonstration."""
    from app.ingestion.market_loader import MarketDataLoader
    from app.ingestion.preprocessor import TimeSeriesPreprocessor
    from app.bridge.r_forecaster import RForecaster
    from app.evaluation.backtester import RollingOriginBacktester

    console.print(Panel("[bold cyan]1. Ingesting & Aligning Multi-Asset Time Series[/bold cyan]", border_style="cyan"))

    loader = MarketDataLoader()
    tickers = ["SPY", "TLT", "GLD"]
    df_prices = loader.load_multi_asset(tickers, start_date="2021-01-01")
    df_returns = TimeSeriesPreprocessor.compute_log_returns(df_prices)

    console.print(f"[green]✓ Successfully loaded {len(df_prices):,} observations across {', '.join(tickers)}.[/green]\n")

    # 2. Stationarity Diagnostics
    console.print(Panel("[bold yellow]2. Unit Root & Stationarity Diagnostics (ADF & KPSS)[/bold yellow]", border_style="yellow"))
    forecaster = RForecaster()

    stat_table = Table(title="Unit Root Testing (ADF vs. KPSS)", header_style="bold magenta")
    stat_table.add_column("Series", style="bold white", width=12)
    stat_table.add_column("ADF Stat", justify="right", width=10)
    stat_table.add_column("ADF 5% Crit", justify="right", width=12)
    stat_table.add_column("KPSS Stat", justify="right", width=10)
    stat_table.add_column("KPSS 5% Crit", justify="right", width=12)
    stat_table.add_column("Stationarity Consensus", style="bold", width=36)

    for ticker in tickers:
        p_res = forecaster.test_stationarity(df_prices[ticker], type="trend")
        r_res = forecaster.test_stationarity(df_returns[ticker], type="drift")

        stat_table.add_row(
            f"{ticker} (Price)",
            f"{p_res.adf_statistic:.2f}",
            f"{p_res.adf_critical_values.get('pct_5', -3.43):.2f}",
            f"{p_res.kpss_statistic:.3f}",
            f"{p_res.kpss_critical_values.get('pct_5', 0.146):.3f}",
            f"[red]{p_res.consensus_verdict}[/red]"
        )
        stat_table.add_row(
            f"{ticker} (Return)",
            f"{r_res.adf_statistic:.2f}",
            f"{r_res.adf_critical_values.get('pct_5', -2.88):.2f}",
            f"{r_res.kpss_statistic:.3f}",
            f"{r_res.kpss_critical_values.get('pct_5', 0.463):.3f}",
            f"[green]{r_res.consensus_verdict}[/green]"
        )

    console.print(stat_table)
    console.print()

    # 3. Univariate State-Space & ARIMA Forecasting
    console.print(Panel("[bold green]3. Univariate Forecasting: Auto-ARIMA vs. State-Space ETS (SPY)[/bold green]", border_style="green"))

    spy_series = df_prices["SPY"]
    h = 14
    arima_res = forecaster.fit_univariate(spy_series, model_type="auto_arima", horizon=h, frequency=7)
    ets_res = forecaster.fit_univariate(spy_series, model_type="ets", horizon=h, frequency=7)

    fc_table = Table(title=f"14-Step Out-of-Sample Forecasts & Prediction Intervals (SPY)", header_style="bold magenta")
    fc_table.add_column("Step", justify="center", width=6)
    fc_table.add_column("ARIMA Point", justify="right", width=12)
    fc_table.add_column("ARIMA 95% CI", justify="center", width=22)
    fc_table.add_column("ETS Point", justify="right", width=12)
    fc_table.add_column("ETS 95% CI", justify="center", width=22)

    for i in range(h):
        ar_pt = arima_res.point_forecast[i]
        ar_low = arima_res.prediction_intervals.get("lower_95", [ar_pt])[i]
        ar_high = arima_res.prediction_intervals.get("upper_95", [ar_pt])[i]

        ets_pt = ets_res.point_forecast[i]
        ets_low = ets_res.prediction_intervals.get("lower_95", [ets_pt])[i]
        ets_high = ets_res.prediction_intervals.get("upper_95", [ets_pt])[i]

        fc_table.add_row(
            f"t+{i+1}",
            f"${ar_pt:.2f}",
            f"[${ar_low:.2f}, ${ar_high:.2f}]",
            f"${ets_pt:.2f}",
            f"[${ets_low:.2f}, ${ets_high:.2f}]"
        )

    console.print(fc_table)
    console.print(f"[dim]Auto-ARIMA Specification: [bold cyan]{arima_res.model_name}[/bold cyan] | In-Sample RMSE: {arima_res.in_sample_metrics.get('RMSE', 0.0):.2f}[/dim]")
    console.print(f"[dim]ETS Specification: [bold cyan]{ets_res.model_name}[/bold cyan] | In-Sample RMSE: {ets_res.in_sample_metrics.get('RMSE', 0.0):.2f}[/dim]\n")

    # 4. Multivariate VAR & Granger Causality
    console.print(Panel("[bold magenta]4. Multivariate Vector Autoregression (VAR) & Granger Causality[/bold magenta]", border_style="magenta"))
    var_res = forecaster.fit_multivariate_var(df_returns, max_lag=4, horizon=h)

    gc_table = Table(title=f"Granger Causality Matrix (VAR p={var_res.lag_order})", header_style="bold magenta")
    gc_table.add_column("Source Variable", style="bold white", width=16)
    gc_table.add_column("F-Statistic", justify="right", width=12)
    gc_table.add_column("p-value", justify="right", width=10)
    gc_table.add_column("Causes System (p < 0.05)", justify="center", width=24)

    for v, gc in var_res.granger_causality.items():
        causes_str = "[bold green]YES[/bold green]" if gc["causes_system"] else "[dim]No[/dim]"
        gc_table.add_row(v, f"{gc['f_statistic']:.3f}", f"{gc['p_value']:.4f}", causes_str)

    console.print(gc_table)
    console.print(f"[dim]VAR System Stability: {'STABLE (All roots < 1.0)' if var_res.is_stable else 'UNSTABLE'} (Max root: {var_res.max_eigenvalue_root:.3f})[/dim]\n")

    # 5. Rolling-Origin Backtesting
    console.print(Panel("[bold blue]5. Rolling-Origin Out-of-Sample Backtesting Evaluation[/bold blue]", border_style="blue"))
    backtester = RollingOriginBacktester(forecaster=forecaster)
    summary = backtester.evaluate(
        series=spy_series,
        model_type="auto_arima",
        initial_train_size=120,
        horizon=14,
        step_size=28,
        frequency=7
    )

    bt_table = Table(title=f"Rolling Cross-Validation Metrics ({summary.n_folds} Folds, Horizon=14)", header_style="bold magenta")
    bt_table.add_column("Model", style="bold white", width=14)
    bt_table.add_column("Out-of-Sample RMSE", justify="right", width=18)
    bt_table.add_column("MAE", justify="right", width=12)
    bt_table.add_column("MAPE (%)", justify="right", width=12)
    bt_table.add_column("MASE", justify="right", width=12)

    bt_table.add_row(
        summary.model_type,
        f"${summary.mean_rmse:.2f} (±{summary.std_rmse:.2f})",
        f"${summary.mean_mae:.2f}",
        f"{summary.mean_mape:.2f}%",
        f"{summary.mean_mase:.3f}"
    )
    console.print(bt_table)
    console.print("[dim]MASE < 1.0 indicates model outperforms the naive seasonal persistence benchmark.[/dim]\n")


def run_api_server(host: str = "0.0.0.0", port: int = 8000):
    """Starts the Uvicorn REST API server."""
    import uvicorn
    console.print(f"[bold green]Starting FastAPI Uvicorn Server at http://{host}:{port}...[/bold green]")
    uvicorn.run("app.api.routes:app", host=host, port=port, reload=False)


def main():
    parser = argparse.ArgumentParser(
        description="Econometric Forecast Engine: Python-R Time Series Infrastructure"
    )
    parser.add_argument(
        "command",
        nargs="?",
        choices=["demo", "serve"],
        default="demo",
        help="Command to run: 'demo' (end-to-end econometric pipeline) or 'serve' (FastAPI REST server)."
    )
    parser.add_argument("--host", default="0.0.0.0", help="API host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="API port (default: 8000)")

    args = parser.parse_args()

    console.print(BANNER)

    if args.command == "demo":
        run_pipeline_demo()
    elif args.command == "serve":
        run_api_server(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
