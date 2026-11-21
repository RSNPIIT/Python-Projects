# ==============================================================================
# Econometric Forecast Engine - R Dependencies Installer
# ==============================================================================

required_packages <- c(
  "jsonlite",    # High-performance JSON serialization
  "zoo",         # Irregular and regular time series representations
  "xts",         # Extensible time series
  "tseries",     # Time series analysis and computational finance
  "urca",        # Unit Root and Cointegration Tests (ADF, KPSS, Johansen)
  "forecast",    # State-space ETS, auto.arima, TBATS, cross-validation
  "vars",        # Vector Autoregression, impulse responses, Granger causality
  "strucchange"  # Structural change and breakpoint detection
)

installed <- rownames(installed.packages())
to_install <- required_packages[!required_packages %in% installed]

if (length(to_install) > 0) {
  cat("Installing missing R packages:", paste(to_install, collapse = ", "), "\n")
  install.packages(to_install, repos = "https://cloud.r-project.org", quiet = FALSE)
} else {
  cat("All required R packages are already installed!\n")
}

cat("\nPackage Verification:\n")
for (pkg in required_packages) {
  loaded <- requireNamespace(pkg, quietly = TRUE)
  cat(sprintf("  [%s] %s\n", if (loaded) "OK" else "FAIL", pkg))
}
