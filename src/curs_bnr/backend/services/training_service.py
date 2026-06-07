from typing import Any, Dict, List

from src.curs_bnr.backend.database import read_training_runs, read_model_results_by_run_id
from src.curs_bnr.backend.schemas import TrainingRunResponse
from src.curs_bnr.ml.train_models import train_models


def fetch_training_runs(limit: int = 10) -> List[TrainingRunResponse]:
    """Returnează lista rulărilor de antrenare recente, inclusiv rezultatele modelelor."""
    rows = read_training_runs(limit)
    enriched_runs: list[Dict[str, Any]] = []
    for row in rows:
        results = read_model_results_by_run_id(row['id'])
        row['results'] = results
        row['winner_rmse'] = None
        row['winner_mape'] = None
        winner_model = row.get('winner_model')
        if winner_model and results:
            for result in results:
                if result.get('model_name') == winner_model:
                    row['winner_rmse'] = result.get('rmse')
                    row['winner_mape'] = result.get('mape')
                    break
        enriched_runs.append(row)
    return [TrainingRunResponse(**row) for row in enriched_runs]


def fetch_last_training_run() -> Dict[str, str]:
    """Returnează metadatele ultimei rulări de antrenare."""
    runs = fetch_training_runs(limit=1)
    if not runs:
        return {"run_id": "0", "status": "pending", "timestamp": ""}
    return runs[0].dict()


def perform_retraining(currency_code: str = "USD", horizon: int = 7) -> Dict[str, Any]:
    """Execută procesul de antrenare și salvare a prognozelor."""
    try:
        return train_models(currency_code=currency_code, forecast_horizon=horizon)
    except Exception as error:
        return {"success": False, "message": str(error)}


def start_retraining() -> Dict[str, str]:
    """Pornește un proces de reantrenare a modelului."""
    return perform_retraining()
