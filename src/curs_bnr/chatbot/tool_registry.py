"""Registru de tool-uri pentru chatbot.

Definește mapping-ul `TOOL_REGISTRY` și schema OpenRouter pentru tool calling.
"""
from typing import Callable, Dict, List

from . import tools


TOOL_REGISTRY: Dict[str, Callable] = {
    "get_latest_exchange_rate": tools.get_latest_exchange_rate,
    "get_forecast_summary": tools.get_forecast_summary,
    "get_model_metrics": tools.get_model_metrics,
    "trigger_scrape": tools.trigger_scrape,
    "trigger_retraining": tools.trigger_retraining,
}


def get_openrouter_tools_schema() -> List[dict]:
    """Returnează schema OpenAI/OpenRouter pentru tool-urile disponibile."""
    return [
        {
            "type": "function",
            "function": {
                "name": "get_latest_exchange_rate",
                "description": "Returnează cel mai recent curs valutar pentru o valută specificată.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "currency_code": {
                            "type": "string",
                            "description": "Codul valutar, de exemplu USD sau EUR.",
                        }
                    },
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_forecast_summary",
                "description": "Returnează ultima prognoză salvată în sistem.",
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_model_metrics",
                "description": "Returnează modelul câștigător și MAE-ul din ultima sesiune de antrenare.",
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "trigger_scrape",
                "description": "Declanșează scrapingul datelor BNR pentru o valută și o dată de început.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "currency_code": {
                            "type": "string",
                            "description": "Codul valutar, de exemplu USD.",
                        },
                        "start_date": {
                            "type": "string",
                            "description": "Data de început în format DD/MM/YYYY.",
                        },
                    },
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "trigger_retraining",
                "description": "Pornește procesul de reantrenare a modelului pentru o valută specifică.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "currency_code": {
                            "type": "string",
                            "description": "Codul valutar pentru reantrenare.",
                        }
                    },
                    "required": [],
                },
            },
        },
    ]
