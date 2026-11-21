# ==============================================================================
# Econometric Forecast Engine - Multivariate VAR & Granger Causality
# Libraries: vars, jsonlite
# ==============================================================================

suppressPackageStartupMessages({
  library(vars)
  library(jsonlite)
})

#' Fit Vector Autoregression (VAR) Model with Diagnostics & Granger Causality
#'
#' @param df_data Data frame or matrix of numeric time series
#' @param max_lag Maximum lag to evaluate during lag selection
#' @param ic Information criterion for optimal lag ("AIC", "HQ", "SC", "FPE")
#' @param horizon Forecast horizon
#' @return Comprehensive VAR results: coefficients, Granger causality tests, forecasts
fit_multivariate_var <- function(
  df_data,
  max_lag = 5,
  ic = "AIC",
  horizon = 14
) {
  df <- as.data.frame(na.omit(df_data))
  n_obs <- nrow(df)
  var_names <- colnames(df)
  k <- length(var_names)

  if (k < 2) {
    stop("Vector Autoregression requires at least 2 endogenous variables.")
  }
  if (n_obs < max(30, max_lag * k * 2)) {
    stop("Insufficient observations for Vector Autoregression with selected variables and lags.")
  }

  # 1. Optimal Lag Order Selection
  lag_selection <- vars::VARselect(df, lag.max = min(max_lag, n_obs %/% 5), type = "const")
  selected_p <- as.integer(lag_selection$selection[[paste0(ic, "(n)")]])
  selected_p <- max(1, min(selected_p, max_lag))

  # 2. Fit VAR(p) Model
  var_fit <- vars::VAR(df, p = selected_p, type = "const")

  # 3. Pairwise Granger Causality Tests
  granger_results <- list()
  for (cause_var in var_names) {
    gc_test <- vars::causality(var_fit, cause = cause_var)
    f_stat <- as.numeric(gc_test$Granger$statistic)
    p_val <- as.numeric(gc_test$Granger$p.value)
    
    granger_results[[cause_var]] <- list(
      cause = cause_var,
      f_statistic = f_stat,
      p_value = p_val,
      causes_system = as.logical(p_val < 0.05),
      interpretation = if (p_val < 0.05) {
        paste(cause_var, "Granger-causes the remaining system variables at alpha = 0.05")
      } else {
        paste("No statistically significant Granger causality from", cause_var)
      }
    )
  }

  # 4. Multi-step Ahead Forecasts
  var_fc <- predict(var_fit, n.ahead = horizon, ci = 0.95)
  forecasts <- list()
  for (v in var_names) {
    fc_matrix <- as.matrix(var_fc$fcst[[v]])
    forecasts[[v]] <- list(
      point_forecast = as.numeric(fc_matrix[, "fcst"]),
      lower_95 = as.numeric(fc_matrix[, "lower"]),
      upper_95 = as.numeric(fc_matrix[, "upper"]),
      ci_interval = as.numeric(fc_matrix[, "CI"])
    )
  }

  # 5. Extract Model Coefficients and Log-Likelihood
  roots <- as.numeric(roots(var_fit))
  is_stable <- all(roots < 1.0)

  return(list(
    n_obs = as.integer(n_obs),
    variables = var_names,
    lag_order = as.integer(selected_p),
    lag_criteria = as.data.frame(lag_selection$criteria),
    is_stable = as.logical(is_stable),
    max_eigenvalue_root = as.numeric(max(roots)),
    granger_causality = granger_results,
    forecasts = forecasts,
    log_likelihood = as.numeric(logLik(var_fit))
  ))
}

# CLI Handler
if (!interactive() && exists("commandArgs")) {
  args <- commandArgs(trailingOnly = TRUE)
  if (length(args) >= 1) {
    payload <- jsonlite::fromJSON(args[1])
    res <- fit_multivariate_var(
      df_data = payload$data,
      max_lag = ifelse(!is.null(payload$max_lag), payload$max_lag, 5),
      horizon = ifelse(!is.null(payload$horizon), payload$horizon, 14)
    )
    if (length(args) >= 2) {
      jsonlite::write_json(res, args[2], auto_unbox = TRUE, pretty = TRUE)
    } else {
      cat(jsonlite::toJSON(res, auto_unbox = TRUE, pretty = TRUE))
    }
  }
}
