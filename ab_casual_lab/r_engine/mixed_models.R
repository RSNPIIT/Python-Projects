# ==============================================================================
# Pure R Mixed-Effects Engine for Clustered A/B Testing & Causal Inference
# Library: lme4, lmerTest (Satterthwaite DF approximation), nlme (fallback)
# ==============================================================================

suppressPackageStartupMessages({
  has_lmer <- requireNamespace("lmerTest", quietly = TRUE) && requireNamespace("lme4", quietly = TRUE)
  has_json <- requireNamespace("jsonlite", quietly = TRUE)
  if (has_lmer) {
    library(lme4)
    library(lmerTest)
  } else {
    library(nlme)
  }
})

#' Fit Linear Mixed-Effects Model for Clustered Experiment Data
#'
#' @param df Data frame containing response, treatment, cluster, and optional covariates
#' @param formula_str Character formula, e.g. "outcome ~ treatment + (1 | cluster_id)"
#' @param REML Logical, whether to use Restricted Maximum Likelihood (default TRUE)
#' @return A structured list of fixed effects, random variances, ICC, and diagnostics
fit_mixed_model <- function(df, formula_str = "outcome ~ treatment + (1 | cluster_id)", REML = TRUE) {
  # Clean and factorize cluster column if needed
  if ("cluster_id" %in% names(df)) {
    df$cluster_id <- as.factor(df$cluster_id)
  }

  model_formula <- as.formula(formula_str)

  if (has_lmer) {
    # --------------------------------------------------------------------------
    # Preferred Engine: lmerTest (Satterthwaite approximations for exact p-values)
    # --------------------------------------------------------------------------
    fit <- lmerTest::lmer(model_formula, data = df, REML = REML)
    s <- summary(fit)

    # Extract fixed effects table
    coef_mat <- s$coefficients
    fixed_effects <- list()
    for (rowname in rownames(coef_mat)) {
      est <- coef_mat[rowname, "Estimate"]
      se <- coef_mat[rowname, "Std. Error"]
      df_val <- if ("df" %in% colnames(coef_mat)) coef_mat[rowname, "df"] else NA
      t_val <- coef_mat[rowname, "t value"]
      p_val <- if ("Pr(>|t|)" %in% colnames(coef_mat)) coef_mat[rowname, "Pr(>|t|)"] else 2 * (1 - pnorm(abs(t_val)))

      ci_lower <- est - 1.96 * se
      ci_upper <- est + 1.96 * se

      fixed_effects[[rowname]] <- list(
        term = rowname,
        estimate = as.numeric(est),
        std_error = as.numeric(se),
        df = as.numeric(df_val),
        statistic = as.numeric(t_val),
        p_value = as.numeric(p_val),
        ci_lower = as.numeric(ci_lower),
        ci_upper = as.numeric(ci_upper)
      )
    }

    # Extract variance components
    vc <- lme4::VarCorr(fit)
    var_df <- as.data.frame(vc)
    sigma_cluster_sq <- 0
    sigma_residual_sq <- 0

    for (i in seq_len(nrow(var_df))) {
      grp <- var_df$grp[i]
      var_val <- var_df$vcov[i]
      if (grp == "Residual") {
        sigma_residual_sq <- var_val
      } else {
        sigma_cluster_sq <- var_val
      }
    }

    total_var <- sigma_cluster_sq + sigma_residual_sq
    icc <- if (total_var > 0) sigma_cluster_sq / total_var else 0.0
    is_singular <- lme4::isSingular(fit, tol = 1e-4)

    aic_val <- AIC(fit)
    bic_val <- BIC(fit)
    log_lik <- as.numeric(logLik(fit))
    n_obs <- nobs(fit)
    n_clusters <- length(unique(df$cluster_id))

    return(list(
      engine = "lmerTest (lme4)",
      converged = TRUE,
      is_singular = as.logical(is_singular),
      n_obs = as.integer(n_obs),
      n_clusters = as.integer(n_clusters),
      sigma_cluster = as.numeric(sqrt(sigma_cluster_sq)),
      sigma_residual = as.numeric(sqrt(sigma_residual_sq)),
      sigma_cluster_sq = as.numeric(sigma_cluster_sq),
      sigma_residual_sq = as.numeric(sigma_residual_sq),
      icc = as.numeric(icc),
      aic = as.numeric(aic_val),
      bic = as.numeric(bic_val),
      log_lik = as.numeric(log_lik),
      fixed_effects = fixed_effects
    ))

  } else {
    # --------------------------------------------------------------------------
    # Fallback Engine: nlme::lme
    # --------------------------------------------------------------------------
    fit <- nlme::lme(outcome ~ treatment, random = ~ 1 | cluster_id, data = df, method = if (REML) "REML" else "ML")
    s <- summary(fit)
    tTable <- s$tTable

    fixed_effects <- list()
    for (rowname in rownames(tTable)) {
      est <- tTable[rowname, "Value"]
      se <- tTable[rowname, "Std.Error"]
      df_val <- tTable[rowname, "DF"]
      t_val <- tTable[rowname, "t-value"]
      p_val <- tTable[rowname, "p-value"]

      fixed_effects[[rowname]] <- list(
        term = rowname,
        estimate = as.numeric(est),
        std_error = as.numeric(se),
        df = as.numeric(df_val),
        statistic = as.numeric(t_val),
        p_value = as.numeric(p_val),
        ci_lower = as.numeric(est - 1.96 * se),
        ci_upper = as.numeric(est + 1.96 * se)
      )
    }

    vc <- nlme::VarCorr(fit)
    sigma_cluster <- as.numeric(vc[1, "StdDev"])
    sigma_residual <- as.numeric(vc[2, "StdDev"])
    sigma_cluster_sq <- sigma_cluster^2
    sigma_residual_sq <- sigma_residual^2
    total_var <- sigma_cluster_sq + sigma_residual_sq
    icc <- if (total_var > 0) sigma_cluster_sq / total_var else 0.0

    return(list(
      engine = "nlme::lme",
      converged = TRUE,
      is_singular = FALSE,
      n_obs = as.integer(nrow(df)),
      n_clusters = as.integer(length(unique(df$cluster_id))),
      sigma_cluster = as.numeric(sigma_cluster),
      sigma_residual = as.numeric(sigma_residual),
      sigma_cluster_sq = as.numeric(sigma_cluster_sq),
      sigma_residual_sq = as.numeric(sigma_residual_sq),
      icc = as.numeric(icc),
      aic = as.numeric(AIC(fit)),
      bic = as.numeric(BIC(fit)),
      log_lik = as.numeric(logLik(fit)),
      fixed_effects = fixed_effects
    ))
  }
}

# ==============================================================================
# CLI Entrypoint for Subprocess Bridge Fallback
# ==============================================================================
if (!interactive() && exists("commandArgs")) {
  args <- commandArgs(trailingOnly = TRUE)
  if (length(args) >= 1) {
    if (!requireNamespace("jsonlite", quietly = TRUE)) {
      stop("jsonlite is required for CLI JSON execution.")
    }

    input_file <- args[1]
    formula_arg <- if (length(args) >= 2) args[2] else "outcome ~ treatment + (1 | cluster_id)"

    data_payload <- jsonlite::fromJSON(input_file)
    df <- as.data.frame(data_payload)
    res <- fit_mixed_model(df, formula_str = formula_arg)

    if (length(args) >= 3) {
      jsonlite::write_json(res, args[3], auto_unbox = TRUE, pretty = TRUE)
    } else {
      cat(jsonlite::toJSON(res, auto_unbox = TRUE, pretty = TRUE))
    }
  }
}
