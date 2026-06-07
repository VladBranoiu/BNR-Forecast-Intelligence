from typing import Any, Dict, Optional

from src.curs_bnr.ml.train_models import train_models


def retrain_model(existing_model: Any = None, data: Optional[Any] = None) -> Dict[str, Any]:
    """Reantrenează un model existent cu date noi."""
    return train_models(data=data)
