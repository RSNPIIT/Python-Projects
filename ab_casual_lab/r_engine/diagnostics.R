# ==============================================================================
# Pure R Mixed-Effects Model Diagnostics & Residual Analysis
# ==============================================================================

suppressPackageStartupMessages({
  library(lme4)
  library(lmerTest)
})

#' Run Statistical Diagnostics on Fitted Mixed Model
#'
#' @param fit An lmerMod or lmerModLmerTest object
#' @return A list containing Shapiro-Wilk p-values, cluster shrinkage, and residual metrics
diagnose_model <- function(fit) {
  resids <- residuals(fit, type = "response")
  ran_efs <- ranef(fit)$cluster_id[[1]]

  # Normality of residuals (subsample if n > 5000 for shapiro.test limit)
  sub_resids <- if (length(resids) > 4000) sample(resids, 4000) else resids
  shapiro_resids <- shapiro.test(sub_resids)$p.value

  # Normality of random intercepts
  shapiro_ranef <- if (length(ran_efs) >= 3 && length(ran_efs) <= 5000) {
    shapiro.test(ran_efs)$p.value
  } else {
    NA
  }

  return(list(
    residual_mean = mean(resids),
    residual_sd = sd(resids),
    residual_shapiro_p = as.numeric(shapiro_resids),
    ranef_shapiro_p = as.numeric(shapiro_ranef),
    ranef_variance = var(ran_efs),
    n_ranef = length(ran_efs)
  ))
}
