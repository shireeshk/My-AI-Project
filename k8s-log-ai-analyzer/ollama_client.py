import requests


def ask_ollama(
    prompt: str,
    model: str = "llama3.2:1b",
    host: str = "http://localhost:11434",
):

    url = f"{host.rstrip('/')}/api/generate"

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
        },
    }

    response = requests.post(
        url,
        json=payload,
        timeout=300,
    )

    if not response.ok:
        try:
            error_payload = response.json()
        except ValueError:
            error_payload = {}

        detail = (
            error_payload.get("error")
            if isinstance(error_payload, dict)
            else None
        )
        if not isinstance(detail, str) or not detail.strip():
            detail = response.text.strip() or response.reason

        if (
            response.status_code == 404
            and "model" in detail.lower()
            and ("not found" in detail.lower() or "does not exist" in detail.lower())
        ):
            raise RuntimeError(
                f"Ollama model '{model}' is not available. "
                f"Run `ollama pull {model}` and try again. "
                f"Server response: {detail}"
            )

        if response.status_code == 404:
            detail = (
                f"{detail} Check that Ollama is running and that the "
                f"Ollama URL is the server base URL "
                f"(usually http://localhost:11434). Requested endpoint: {url}"
            )

        raise requests.HTTPError(
            f"Ollama request failed with HTTP {response.status_code}: {detail}",
            response=response,
        )

    return response.json().get("response", "")
