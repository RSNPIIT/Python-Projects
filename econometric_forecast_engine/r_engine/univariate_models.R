# ==============================================================================
# Econometric Forecast Engine - Univariate Models (ARIMA, ETS, TBATS)
# Libraries: forecast, jsonlite
# ==============================================================================

suppressPackageStartupMessages({
  library(forecast)
  library(jsonlite)
})

#' Fit Univariate Time Series Model and Generate Out-of-Sample Forecasts
#'
#' @param series Numeric vector
#' @param model_type "auto_arima", "ets", or "tbats"
#' @param horizon Integer forward steps (default 14)
#' @param frequency Seasonality frequency (default 7 for daily, 12 for monthly, 1 for non-seasonal)
#' @param conf_levels Confidence levels e.g. c(80, 95)
#' @return Structured list containing model specifications, point forecasts, prediction intervals, and metrics
fit_univariate_model <- function(
  series,
  model_type = "auto_arima",
  horizon = 14,
  frequency = 7,
  conf_levels = c(80, 95)
) {
  clean_series <- as.numeric(na.omit(series))
  n <- length(clean_series)
  if (n < 15) {
    stop("Series is too short for econometric forecasting (requires >= 15 observations).")
  }

  ts_obj <- ts(clean_series, frequency = max(1, frequency))
  h <- as.integer(horizon)

  fitted_model <- NULL
  model_name <- ""
  model_spec <- list()

  if (model_type == "auto_arima") {
    # Hyndman-Khandakar Auto-ARIMA
    fitted_model <- forecast::auto.arima(
      ts_obj,
      stepwise = TRUE,
      approximation = (n > 150),
      seasonal = (frequency > 1)
    )
    ar_order <- fitted_model$arma
    model_name <- as.character(fitted_model)
    model_spec <- list(
      p = as.integer(ar_order[1]),
      q = as.integer(ar_order[2]),
      P = as.integer(ar_order[3]),
      Q = as.integer(ar_order[4]),
      s = as.integer(ar_order[5]),
      d = as.integer(ar_order[6]),
      D = as.integer(ar_order[7])
    )

  } else if (model_type == "ets") {
    # State-Space Exponential Smoothing
    fitted_model <- forecast::ets(ts_obj)
    model_name <- as.character(fitted_model)
    model_spec <- list(
      components = fitted_model$components,
      alpha = as.numeric(fitted_model$par["alpha"]),
      beta = as.numeric(fitted_model$par["beta"]),
      gamma = as.numeric(fitted_model$par["gamma"]),
      phi = as.numeric(fitted_model$par["phi"])
    )

  } else if (model_type == "tbats") {
    # TBATS: Trigonometric seasonal, Box-Cox, ARMA errors, Trend, Seasonal
    fitted_model <- forecast::tbats(ts_obj, use.box.cox = TRUE)
    model_name <- as.character(fitted_model)
    model_spec <- list(
      box_cox_lambda = as.numeric(fitted_model$lambda),
      damped_trend = as.logical(fitted_model$damping.parameter)
    )

  } else {
    stop(paste("Unknown model_type:", model_type, ". Choose 'auto_arima', 'ets', or 'tbats'."))
  }

  # Generate Forecast
  fc <- forecast::forecast(fitted_model, h = h, level = conf_levels)

  # Residual Ljung-Box Portmanteau Autocorrelation Test
  resids <- as.numeric(residuals(fitted_model))
  lb_test <- tryCatch({
    lb <- Box.test(resids, lag = min(10, n %/% 4), type = "Ljung-Box")
    list(statistic = as.numeric(lb$statistic), p_value = as.numeric(lb$p.value))
  }, error = function(e) list(statistic = NA, p_value = NA))

  # In-Sample Accuracy Metrics
  acc <- forecast::accuracy(fitted_model)
  metrics <- list(
    RMSE = as.numeric(acc[1, "RMSE"]),
    MAE = as.numeric(acc[1, "MAE"]),
    MAPE = as.numeric(acc[1, "MAPE"]),
    MASE = if ("MASE" %in% colnames(acc)) as.numeric(acc[1, "MASE"]) else NA,
    AIC = as.numeric(AIC(fitted_model)),
    BIC = as.numeric(BIC(fitted_model))
  )

  # Extract Prediction Intervals
  lower_matrix <- as.matrix(fc$lower)
  upper_matrix <- as.matrix(fc$upper)
  intervals <- list()
  for (i in seq_along(conf_levels)) {
    lvl <- as.character(conf_levels[i])
    intervals[[paste0("lower_", lvl)]] <- as.numeric(lower_matrix[, i])
    intervals[[paste0("upper_", lvl)]] <- as.numeric(upper_matrix[, i])
  }

  return(list(
    model_type = model_type,
    model_name = model_name,
    model_spec = model_spec,
    n_obs = as.integer(n),
    horizon = h,
    point_forecast = as.numeric(fc$mean),
    fitted_values = as.numeric(fitted(fitted_model)),
    residuals = resids,
    prediction_intervals = intervals,
    in_sample_metrics = metrics,
    ljung_box_test = lb_test
  ))
}

# CLI handler
if (!interactive() && exists("commandArgs")) {
  args <- commandArgs(trailingOnly = TRUE)
  if (length(args) >= 1) {
    payload <- jsonlite::fromJSON(args[1])
    res <- fit_univariate_model(
      series = payload$series,
      model_type = ifelse(!is.null(payload$model_type), payload$model_type, "auto_arima"),
      horizon = ifelse(!is.null(payload$horizon), payload$horizon, 14),
      frequency = ifelse(!is.null(payload$frequency), payload$frequency, 7)
    )
    if (length(args) >= 2) {
      jsonlite::write_json(res, args[2], auto_unbox = TRUE, pretty = TRUE)
    } else {
      cat(jsonlite::toJSON(res, auto_unbox = TRUE, pretty = TRUE))
    }
  }
}
