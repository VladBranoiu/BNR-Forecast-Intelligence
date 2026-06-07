from typing import Any, Dict

import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error

from src.curs_bnr.ml.forecast import generate_forecast


def evaluate_models(model: Any, actual: Any) -> Dict[str, float]:
    """Evaluează performanța unui model pe un set de date de test."""
    if actual is None or len(actual) == 0:
        return {"mae": float("nan"), "rmse": float("nan"), "mape": float("nan")}

    forecast_info = generate_forecast(model, len(actual))
    predicted = [entry["predicted"] for entry in forecast_info["forecast"]]
    y_pred = np.asarray(predicted, dtype=float)
    y_true = np.asarray(actual, dtype=float).flatten()
    if y_true.shape != y_pred.shape:
        raise ValueError("Datele reale și predicțiile nu au aceeași formă.")

    mae = float(mean_absolute_error(y_true, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    if np.allclose(y_true, 0.0):
        mape = float("inf")
    else:
        mape = float(mean_absolute_percentage_error(y_true, y_pred) * 100)

    return {"mae": mae, "rmse": rmse, "mape": mape}
