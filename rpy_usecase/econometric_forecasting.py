import pandas as pd
import rpy2.robjects as ro
from rpy2.robjects import pandas2ri
from rpy2.robjects.conversion import localconverter

ro.r('''
    library(forecast)
    
    forecast_series <- function(values, freq, horizon) {
        ts_data <- ts(values, frequency = freq)
        fit <- auto.arima(ts_data, seasonal = TRUE, stepwise = FALSE)
        fc <- forecast(fit, h = horizon)
        
        data.frame(
            point_forecast = as.numeric(fc$mean),
            lower_95 = as.numeric(fc$lower[, 2]),
            upper_95 = as.numeric(fc$upper[, 2])
        )
    }
''')

def run_r_forecast(series: pd.Series, freq: int = 12, horizon: int = 6) -> pd.DataFrame:
    r_func = ro.globalenv['forecast_series']
    with localconverter(ro.default_converter + pandas2ri.converter):
        r_vec = ro.FloatVector(series.dropna().tolist())
        return ro.conversion.rpy2py(r_func(r_vec, freq, horizon))

