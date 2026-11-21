# ==============================================================================
# Econometric Forecast Engine - Stationarity & Cointegration Tests
# Libraries: urca, tseries, jsonlite
# ==============================================================================

suppressPackageStartupMessages({
  library(urca)
  library(tseries)
  library(jsonlite)
})

#' Run Comprehensive Unit Root Tests (ADF, KPSS, Phillips-Perron)
#'
#' @param series Numeric vector representing the univariate time series
#' @param type Type of deterministic term for ADF: "none", "drift", "trend"
#' @param selectlags Lag selection criterion: "AIC" or "BIC"
#' @return Structured list with test statistics, critical values, and stationarity decisions
test_stationarity <- function(series, type = "trend", selectlags = "AIC") {
  clean_series <- as.numeric(na.omit(series))
  n <- length(clean_series)
  
  if (n < 15) {
    stop("Time series is too short for stationarity testing (minimum 15 observations required).")
  }

  # 1. Augmented Dickey-Fuller (ADF) Test via urca
  adf_res <- urca::ur.df(clean_series, type = type, selectlags = selectlags)
  adf_stat <- as.numeric(adf_res@teststat[1])
  adf_cvals <- as.numeric(adf_res@cval[1, ])
  adf_lags <- adf_res@lags
  # ADF Null: Unit root is present (Non-stationary). Reject if teststat < critical value (5%)
  adf_5pct <- adf_cvals[2]
  adf_is_stationary <- adf_stat < adf_5pct

  # 2. KPSS Test via urca (Null: Stationary around level or trend)
  kpss_type <- if (type == "trend") "tau" else "mu"
  kpss_res <- urca::ur.kpss(clean_series, type = kpss_type)
  kpss_stat <- as.numeric(kpss_res@teststat)
  kpss_cvals <- as.numeric(kpss_res@cval)
  # KPSS Null: Stationary. Reject if teststat > critical value (5%)
  kpss_5pct <- kpss_cvals[2]
  kpss_is_stationary <- kpss_stat < kpss_5pct

  # 3. Phillips-Perron Test via tseries
  pp_res <- tryCatch({
    pp <- tseries::pp.test(clean_series, alternative = "stationary")
    list(stat = as.numeric(pp$statistic), p_value = as.numeric(pp$p.value))
  }, error = function(e) {
    list(stat = NA, p_value = NA)
  })

  # Joint Consensus Verdict
  consensus <- if (adf_is_stationary && kpss_is_stationary) {
    "Stationary (Both ADF and KPSS agree)"
  } else if (!adf_is_stationary && !kpss_is_stationary) {
    "Non-Stationary (Unit Root detected by ADF and KPSS)"
  } else if (adf_is_stationary && !kpss_is_stationary) {
    "Difference-Stationary (Trend-Stationary / Mixed Signal)"
  } else {
    "Ambiguous (Requires First-Differencing)"
  }

  return(list(
    n_obs = as.integer(n),
    adf = list(
      statistic = adf_stat,
      lags = as.integer(adf_lags),
      critical_values = list(
        pct_1 = adf_cvals[1],
        pct_5 = adf_cvals[2],
        pct_10 = adf_cvals[3]
      ),
      is_stationary = as.logical(adf_is_stationary),
      interpretation = if (adf_is_stationary) "Reject Null: Series is stationary" else "Fail to reject Null: Unit root present"
    ),
    kpss = list(
      statistic = kpss_stat,
      critical_values = list(
        pct_10 = kpss_cvals[1],
        pct_5 = kpss_cvals[2],
        pct_2_5 = kpss_cvals[3],
        pct_1 = kpss_cvals[4]
      ),
      is_stationary = as.logical(kpss_is_stationary),
      interpretation = if (kpss_is_stationary) "Fail to reject Null: Series is stationary" else "Reject Null: Series has unit root"
    ),
    phillips_perron = pp_res,
    consensus_verdict = consensus,
    recommended_differencing = if (!adf_is_stationary || !kpss_is_stationary) 1L else 0L
  ))
}

#' Run Johansen Cointegration Test on Multiple Time Series
#'
#' @param matrix_data Matrix or data.frame with multiple time series columns
#' @param type "trace" or "eigen"
#' @param ecdet "none", "const", or "trend"
#' @param K Lag order
#' @return Cointegrating rank r, eigenvalues, and test statistics
test_cointegration_johansen <- function(matrix_data, type = "trace", ecdet = "const", K = 2) {
  df <- as.matrix(na.omit(matrix_data))
  n_vars <- ncol(df)

  if (n_vars < 2) {
    stop("Johansen cointegration test requires at least 2 time series.")
  }

  jo_fit <- urca::ca.jo(df, type = type, ecdet = ecdet, K = K)
  
  test_stats <- as.numeric(jo_fit@teststat)
  cvals <- jo_fit@cval
  eigenvalues <- as.numeric(jo_fit@lambda)
  v_mat <- jo_fit@V

  # Determine cointegrating rank r at 5% significance
  r <- 0
  for (i in rev(seq_along(test_stats))) {
    stat <- test_stats[i]
    crit_5 <- cvals[i, "5pct"]
    if (stat > crit_5) {
      r <- length(test_stats) - i + 1
    }
  }

  return(list(
    n_vars = as.integer(n_vars),
    test_type = type,
    lag_order = as.integer(K),
    cointegrating_rank = as.integer(r),
    is_cointegrated = as.logical(r > 0),
    eigenvalues = eigenvalues,
    test_statistics = test_stats,
    critical_values_5pct = as.numeric(cvals[, "5pct"]),
    eigenvectors = as.data.frame(v_mat)
  ))
}

# CLI execution handler
if (!interactive() && exists("commandArgs")) {
  args <- commandArgs(trailingOnly = TRUE)
  if (length(args) >= 1) {
    payload <- jsonlite::fromJSON(args[1])
    res <- test_stationarity(payload$series, type = ifelse(!is.null(payload$type), payload$type, "trend"))
    if (length(args) >= 2) {
      jsonlite::write_json(res, args[2], auto_unbox = TRUE, pretty = TRUE)
    } else {
      cat(jsonlite::toJSON(res, auto_unbox = TRUE, pretty = TRUE))
    }
  }
}
