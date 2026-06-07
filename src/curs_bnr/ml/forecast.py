from typing import Any, Dict, List

import numpy as np


def generate_forecast(model: Any, horizon: int) -> Dict[str, Any]:
    """Generează date de prognoză pentru orizontul specificat."""
    if horizon < 1:
        raise ValueError("Orizontul de prognoză trebuie să fie cel puțin 1.")

    if hasattr(model, "get_forecast"):
        forecast_obj = model.get_forecast(steps=horizon)
        predicted = np.asarray(forecast_obj.predicted_mean, dtype=float)
        conf_int = forecast_obj.conf_int(alpha=0.05)
        lower = np.asarray(conf_int.iloc[:, 0], dtype=float)
        upper = np.asarray(conf_int.iloc[:, 1], dtype=float)
    else:
        predicted = np.asarray(model.forecast(steps=horizon), dtype=float)
        residuals = getattr(model, "resid", None)
        sigma = float(np.std(residuals)) if residuals is not None else 0.0
        lower = predicted - 2.0 * sigma
        upper = predicted + 2.0 * sigma

    forecast: List[Dict[str, float]] = []
    for idx, value in enumerate(predicted):
        forecast.append(
            {
                "step": idx + 1,
                "predicted": float(value),
                "lower": float(lower[idx]),
                "upper": float(upper[idx]),
            }
        )

    return {"forecast": forecast, "horizon": horizon}
