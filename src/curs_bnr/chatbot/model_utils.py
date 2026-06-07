"""Utilitare pentru executarea apelurilor către tool-urile locale ale chatbot-ului și
integrarea opțională cu un LLM (Gemini).

Păstrează fallback local (`run_local_chatbot`) și adaugă `run_llm_chatbot` + `run_chatbot`.
"""
from typing import Any, Dict
import json
import os
import re
import html
from dotenv import load_dotenv

from . import tool_registry

load_dotenv()
load_dotenv(".env.example", override=False)


def execute_tool_call(tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
    """Execută un tool local după nume și parametri.

    Returnează dict-ul standard al tool-ului sau un dict de eroare dacă tool-ul
    nu există sau argumentele sunt invalide.
    """
    if tool_name not in tool_registry.TOOL_REGISTRY:
        return {"success": False, "data": None, "message": "Tool necunoscut."}

    func = tool_registry.TOOL_REGISTRY[tool_name]
    try:
        if not tool_args:
            result = func()
        else:
            result = func(**tool_args)
    except TypeError as err:
        return {"success": False, "data": None, "message": f"Argumente invalide: {err}"}
    except Exception as err:  # pragma: no cover - defensive
        return {"success": False, "data": None, "message": f"Eroare la execuția tool-ului: {err}"}

    return result if isinstance(result, dict) else {"success": True, "data": result, "message": "OK"}


def _format_number(value: object, ndigits: int = 4) -> str:
    try:
        return f"{float(value):.{ndigits}f}"
    except (TypeError, ValueError):
        return str(value) if value is not None else "0.0000"


def format_forecast_response(data: dict) -> str:
    """Formatează răspunsul pentru ultima prognoză în limbaj natural."""
    if not isinstance(data, dict) or not data:
        return "Nu există încă o prognoză salvată. Rulează mai întâi reantrenarea modelelor."

    forecast_date = data.get("forecast_date")
    model_name = data.get("model_name")
    predicted_value = data.get("predicted_value")
    if forecast_date is None or model_name is None or predicted_value is None:
        return "Nu există încă o prognoză salvată. Rulează mai întâi reantrenarea modelelor."

    base_text = (
        f"Ultima prognoză disponibilă este pentru data de {forecast_date}. "
        f"Modelul folosit este {model_name}, iar valoarea estimată este {_format_number(predicted_value)} RON."
    )
    lower_bound = data.get("lower_bound")
    upper_bound = data.get("upper_bound")
    if lower_bound is not None and upper_bound is not None:
        interval_text = (
            f" Intervalul estimat este între {_format_number(lower_bound)} și {_format_number(upper_bound)} RON."
        )
        return base_text + interval_text

    return base_text


def format_latest_rate_response(data: dict) -> str:
    """Formatează răspunsul pentru cursul valutar într-un text natural."""
    if not isinstance(data, dict) or not data:
        return (
            "Nu există cursuri salvate pentru valuta selectată. Rulează mai întâi actualizarea datelor BNR."
        )

    currency = data.get("currency_code", "USD")
    value = data.get("value")
    rate_date = data.get("rate_date")
    if value is None or rate_date is None:
        return (
            "Nu există cursuri salvate pentru valuta selectată. Rulează mai întâi actualizarea datelor BNR."
        )

    return (
        f"Ultimul curs disponibil pentru {currency}/RON este {_format_number(value)}, "
        f"înregistrat la data {rate_date}."
    )


def format_model_metrics_response(data: object) -> str:
    """Formatează răspunsul pentru metricile modelului în limbaj natural."""
    if not data:
        return "Nu există încă rulări de antrenare. Rulează mai întâi reantrenarea modelelor."

    if isinstance(data, dict):
        winner_model = data.get("winner_model")
        winner_mae = data.get("winner_mae")
        if winner_model and winner_mae is not None:
            return (
                f"Modelul câștigător este {winner_model}, cu un MAE de {_format_number(winner_mae)}."
            )
        return "Nu există încă rulări de antrenare. Rulează mai întâi reantrenarea modelelor."

    if isinstance(data, list):
        models = []
        for item in data:
            if isinstance(item, dict):
                model_name = item.get("model_name") or item.get("winner_model")
                mae = item.get("mae")
                if model_name and mae is not None:
                    models.append((model_name, mae))
        if models:
            models.sort(key=lambda pair: pair[1])
            model_text = ", ".join(
                f"{name} - MAE {_format_number(mae)}" for name, mae in models
            )
            winner = models[0][0]
            return (
                f"Modelele au fost evaluate astfel: {model_text}. Modelul câștigător este {winner}."
            )
        return "Nu există încă rulări de antrenare. Rulează mai întâi reantrenarea modelelor."

    return "Nu există încă rulări de antrenare. Rulează mai întâi reantrenarea modelelor."


def format_operation_response(data: dict) -> str:
    """Formatează răspunsul pentru operații de scraping sau reantrenare."""
    if not isinstance(data, dict):
        return "Operația nu a reușit din cauza unui răspuns neașteptat."

    success = data.get("success") is True
    message = data.get("message") or ""
    if not success:
        error_text = message if message else "A apărut o eroare la procesare."
        return f"Operația nu a reușit: {error_text}"

    if data.get("records_count") is not None:
        currency = data.get("currency_code") or "USD"
        records_count = data.get("records_count")
        return (
            f"Actualizarea datelor BNR s-a finalizat cu succes. "
            f"Au fost salvate {records_count} înregistrări pentru valuta {currency}."
        )

    if data.get("winner_model") or data.get("winner_mae") is not None:
        winner_model = data.get("winner_model") or "modelul câștigător"
        winner_mae = data.get("winner_mae")
        if winner_mae is not None:
            return (
                f"Reantrenarea modelelor s-a finalizat cu succes. "
                f"Modelul câștigător este {winner_model}, cu MAE {_format_number(winner_mae)}."
            )

    return message or "Operația s-a finalizat cu succes."


def run_local_chatbot(user_message: str) -> str:
    """Răspuns local/fallback pentru chatbot bazat pe cuvinte-cheie.

    Nu folosește LLM; apelează tool-urile locale definite.
    """
    text = (user_message or "").lower()
    if any(k in text for k in ["prognoz", "forecast", "maine", "mâine", "viitor"]):
        res = execute_tool_call("get_forecast_summary", {})
        if res.get("success"):
            return format_forecast_response(res.get("data", {}))
        return f"Nu am putut obține prognoza: {res.get('message')}"

    if any(k in text for k in ["curs", "valoare", "azi", "actual"]):
        res = execute_tool_call("get_latest_exchange_rate", {"currency_code": "USD"})
        if res.get("success"):
            return format_latest_rate_response(res.get("data", {}))
        return f"Nu am putut obține cursul: {res.get('message')}"

    if any(k in text for k in ["model", "eroare", "performanță", "compar"]):
        res = execute_tool_call("get_model_metrics", {})
        if res.get("success"):
            return format_model_metrics_response(res.get("data"))
        return f"Nu am găsit metrici: {res.get('message')}"

    if any(k in text for k in ["actualizează", "scrape", "date noi"]):
        res = execute_tool_call("trigger_scrape", {"currency_code": "USD", "start_date": "22/02/2020"})
        return format_operation_response(res)

    if any(k in text for k in ["reantreneaz", "antreneaz"]):
        res = execute_tool_call("trigger_retraining", {"currency_code": "USD"})
        return format_operation_response(res)

    return (
        "Acesta este un modul local de testare. Formulează o întrebare despre "
        "prognoză, curs sau reantrenare pentru a verifica tool-urile locale."
    )


def _build_tools_schema_for_model() -> list[dict]:
    """Construiește schema OpenRouter compatibilă cu tool calling."""
    return tool_registry.get_openrouter_tools_schema()


def _is_valid_key(value: str | None) -> bool:
    if not value:
        return False
    normalized = value.strip().lower()
    if not normalized:
        return False
    if normalized.startswith("your_") or "example" in normalized or "replace" in normalized:
        return False
    return True


def _get_openrouter_config() -> tuple[str | None, str, str]:
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    api_base = os.getenv("OPENROUTER_API_BASE") or os.getenv("OPENAI_API_BASE") or "https://openrouter.ai/api/v1"
    model_name = os.getenv("OPENROUTER_MODEL") or os.getenv("OPENAI_MODEL") or "openai/gpt-4o-mini"
    return api_key, api_base, model_name


def get_openrouter_config() -> dict:
    """Returnează configurația OpenRouter/OpenAI folosită pentru LLM."""
    api_key, api_base, model_name = _get_openrouter_config()
    return {
        "api_key": api_key,
        "api_base": api_base,
        "model": model_name,
    }


def _get_llm_provider() -> str:
    if _is_valid_key(os.getenv("OPENROUTER_API_KEY")):
        return "openrouter"
    if _is_valid_key(os.getenv("OPENAI_API_KEY")):
        return "openrouter"
    if _is_valid_key(os.getenv("GEMINI_API_KEY")):
        return "gemini"
    raise RuntimeError("Nicio cheie LLM configurată. Setează OPENROUTER_API_KEY sau OPENAI_API_KEY.")


def get_llm_provider() -> str:
    try:
        return _get_llm_provider()
    except RuntimeError:
        return ""


def is_llm_available() -> bool:
    api_key = os.getenv("OPENROUTER_API_KEY")
    return _is_valid_key(api_key)


def _build_system_instruction() -> str:
    return (
        "Ești un asistent specializat în cursuri valutare BNR. Răspunde în limba română. "
        "Folosește tool-urile când utilizatorul cere cursuri, prognoze, comparații de modele, actualizare date sau reantrenare. "
        "Nu inventa valori. Dacă lipsesc datele, spune clar că trebuie făcut scraping sau reantrenare."
    )


def _run_gemini_llm_chatbot(user_message: str, verbose: bool = False) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY lipsește")

    try:
        import google.generativeai as genai
    except Exception as exc:
        raise RuntimeError(f"Biblioteca google.generativeai nu este disponibilă: {exc}")

    genai.configure(api_key=api_key)
    messages = [
        {"role": "system", "content": _build_system_instruction()},
        {"role": "user", "content": user_message},
    ]

    for step in range(5):
        if verbose:
            print(f"LLM step {step+1}")
        try:
            response = genai.chat.create(model="chat-bison-001", messages=messages)
            content = None
            if hasattr(response, "last"):
                content = getattr(response, "last").content
            elif isinstance(response, dict):
                candidates = response.get("candidates") or []
                if candidates:
                    content = candidates[0].get("content") if isinstance(candidates[0], dict) else None
            else:
                content = str(response)
        except Exception as err:
            raise RuntimeError(f"Eroare la apel LLM Gemini: {err}")

        if not content:
            raise RuntimeError("Răspuns LLM Gemini gol")

        stripped = content.strip()
        try:
            payload = json.loads(stripped)
        except Exception:
            return stripped

        tool_name = payload.get("tool")
        tool_args = payload.get("args") or {}
        if not tool_name:
            return content

        tool_result = execute_tool_call(tool_name, tool_args)
        messages.append({"role": "assistant", "content": json.dumps(payload)})
        messages.append({"role": "tool", "name": tool_name, "content": json.dumps(tool_result)})

    return "Am executat tool-urile solicitate; vezi rezultatul anterior."


def _run_openrouter_chatbot(user_message: str, verbose: bool = False) -> str:
    api_key, api_base, model_name = _get_openrouter_config()
    if not _is_valid_key(api_key):
        raise RuntimeError("OPENROUTER_API_KEY sau OPENAI_API_KEY validă lipsește")

    try:
        from openai import OpenAI
    except Exception as exc:
        raise RuntimeError(f"Biblioteca openai nu este disponibilă: {exc}")

    client = OpenAI(api_key=api_key, base_url=api_base)
    messages = [
        {"role": "system", "content": _build_system_instruction()},
        {"role": "user", "content": user_message},
    ]
    tools_schema = tool_registry.get_openrouter_tools_schema()

    for step in range(5):
        if verbose:
            print(f"LLM step {step+1}")
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                tools=tools_schema,
                tool_choice="auto",
                temperature=0.2,
            )
        except Exception as err:
            raise RuntimeError(f"Eroare la apel LLM OpenRouter: {err}")

        content = None
        tool_calls = None
        if hasattr(response, "choices") and response.choices:
            first_choice = response.choices[0]
            message = getattr(first_choice, "message", None)
            if message is not None:
                content = getattr(message, "content", None)
                tool_calls = getattr(message, "tool_calls", None)
            elif isinstance(first_choice, dict):
                message = first_choice.get("message", {})
                content = message.get("content")
                tool_calls = message.get("tool_calls")
        elif isinstance(response, dict):
            choices = response.get("choices") or []
            if choices:
                first_choice = choices[0]
                message = first_choice.get("message", {})
                content = message.get("content")
                tool_calls = message.get("tool_calls")

        if content is None:
            content = str(response)

        if tool_calls:
            if isinstance(tool_calls, dict):
                tool_calls = [tool_calls]
            if not isinstance(tool_calls, list):
                tool_calls = list(tool_calls)
            if tool_calls:
                tool_call = tool_calls[0]
                tool_name = None
                tool_args = {}
                tool_call_id = None
                if isinstance(tool_call, dict):
                    tool_name = tool_call.get("name")
                    tool_args = tool_call.get("arguments") or {}
                    tool_call_id = tool_call.get("id")
                else:
                    tool_name = getattr(tool_call, "name", None)
                    tool_args = getattr(tool_call, "arguments", {})
                    tool_call_id = getattr(tool_call, "id", None)

                if isinstance(tool_args, str):
                    try:
                        tool_args = json.loads(tool_args)
                    except Exception:
                        tool_args = {}

                if not tool_name:
                    return content or "Răspuns LLM neclar." 

                tool_result = execute_tool_call(tool_name, tool_args or {})
                messages.append({"role": "assistant", "content": content or ""})
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "name": tool_name,
                        "content": json.dumps(tool_result, ensure_ascii=False),
                    }
                )
                continue

        return content or "Nu am primit răspuns de la model."

    return content or "Nu am primit răspuns final de la model."


def run_openrouter_chatbot(user_message: str, verbose: bool = False) -> str:
    """Rulează un dialog direct prin OpenRouter folosind tool calling."""
    return _run_openrouter_chatbot(user_message, verbose=verbose)


def run_llm_chatbot(user_message: str, verbose: bool = False) -> str:
    """Încearcă să ruleze un dialog folosind un LLM și tool-calling."""
    if is_llm_available():
        return _run_openrouter_chatbot(user_message, verbose=verbose)

    if _is_valid_key(os.getenv("GEMINI_API_KEY")):
        return _run_gemini_llm_chatbot(user_message, verbose=verbose)

    raise RuntimeError("Nicio cheie LLM validă disponibilă pentru execuție.")


def _sanitize_chatbot_text(text: str) -> str:
    """Elimină tag-urile HTML și asigură că textul returnat este sigur pentru afișare."""
    if not isinstance(text, str):
        text = str(text)
    cleaned = re.sub(r"<\/?[^>]+>", "", text)
    return html.unescape(cleaned).strip()


def _is_raw_llm_response(text: str) -> bool:
    """Detectează dacă răspunsul LLM pare a fi un obiect brut sau un JSON/dicționar neformatat."""
    if not isinstance(text, str):
        return True

    if any(token in text for token in ("ChatCompletion(", "CompletionUsage(", "tool_calls", "'tool'", '"tool"')):
        return True

    stripped = text.strip()
    if (stripped.startswith("{") and stripped.endswith("}")) or (
        stripped.startswith("[") and stripped.endswith("]")
    ):
        return True

    return False


def run_chatbot(user_message: str, use_llm: bool = True) -> str:
    """Interfață unificată pentru apelul chatbot.

    - Dacă `use_llm` este True și există o cheie OpenRouter/LLM disponibilă, încearcă `run_llm_chatbot`.
    - Altfel, folosește `run_local_chatbot`.
    - Orice eroare sau răspuns brut din LLM duce la fallback local.
    """
    if use_llm and is_llm_available():
        try:
            response = run_llm_chatbot(user_message)
            if _is_raw_llm_response(response):
                return _sanitize_chatbot_text(f"(LLM fallback) {run_local_chatbot(user_message)}")
            return _sanitize_chatbot_text(response)
        except Exception:
            return _sanitize_chatbot_text(f"(LLM fallback) {run_local_chatbot(user_message)}")

    return _sanitize_chatbot_text(run_local_chatbot(user_message))

