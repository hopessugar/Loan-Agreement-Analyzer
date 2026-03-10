import os
import json
import re
import requests
from dotenv import load_dotenv

load_dotenv()

# ── HUGGINGFACE ROUTER + MISTRAL ────────────────────────────────────
# Uses OpenAI-compatible chat completions on router.huggingface.co
HF_TOKEN = os.getenv("HF_TOKEN")

HF_BASE_URL = "https://router.huggingface.co/v1"
HF_MODEL    = "meta-llama/Llama-3.1-8B-Instruct"


def call_llm(prompt: str, max_tokens: int = 2000) -> str:
    """
    Calls Mistral-7B-Instruct via HuggingFace router using the
    OpenAI-compatible `/completions` endpoint.
    Returns the raw text response string from the first choice.
    """
    if not HF_TOKEN:
        raise Exception(
            "HF_TOKEN not found in .env file. "
            "Create a Hugging Face access token and set HF_TOKEN."
        )

    url = f"{HF_BASE_URL}/chat/completions"

    payload = {
        "model": HF_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.1,
    }

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=90,
        )

        print(f"HuggingFace router status: {response.status_code}")

        if response.status_code != 200:
            print(f"HuggingFace router error: {response.text[:500]}")
            raise Exception(
                f"HuggingFace router API error {response.status_code}: {response.text[:200]}"
            )

        result = response.json()
        choices = result.get("choices") or []
        if not choices:
            print("HuggingFace router returned no choices")
            return ""

        # `/chat/completions` returns text in choices[0].message.content
        message = choices[0].get("message") or {}
        text = message.get("content", "") or ""
        print(f"HF router generated length: {len(text)} chars")
        return text

    except requests.exceptions.Timeout:
        raise Exception("Request timed out. Try again.")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error: {str(e)}")


def extract_json_from_response(raw: str) -> dict:
    """
    Parses JSON from LLM response.
    Handles markdown fences and extracts the JSON object.
    """
    if not raw or not raw.strip():
        print("ERROR: Empty response from LLM")
        return {}

    # Strip markdown code fences
    fenced = re.search(r'```(?:json)?\s*([\s\S]*?)```', raw)
    if fenced:
        raw = fenced.group(1).strip()

    # Find the JSON object
    json_match = re.search(r'\{[\s\S]*\}', raw)
    if json_match:
        raw = json_match.group(0).strip()

    # First, try strict JSON parsing.
    try:
        parsed = json.loads(raw)
        print(f"Parsed JSON with {len(parsed)} keys")
        return parsed
    except json.JSONDecodeError as e:
        print(f"JSON parse failed: {e}")
        print(f"Raw text was: {raw[:300]}")

    # Fallback: best-effort recovery of top-level entity blocks of the form
    # "entity_name": { ... } so that we can still work with partial JSON.
    recovered: dict[str, dict] = {}
    for match in re.finditer(r'"([^"]+)"\s*:\s*\{([\s\S]*?)\}', raw):
        key = match.group(1)
        obj_str = "{" + match.group(2) + "}"
        try:
            recovered[key] = json.loads(obj_str)
        except json.JSONDecodeError:
            continue

    if recovered:
        print(f"Recovered {len(recovered)} top-level entities from malformed JSON")
        return recovered

    return {}


def run_extraction(prompt: str) -> dict:
    raw = call_llm(prompt, max_tokens=2000)
    print("=== FULL LLM RESPONSE ===")
    print(raw)
    print("=== END RESPONSE ===")
    return extract_json_from_response(raw)


def run_summary(prompt: str) -> str:
    return call_llm(prompt, max_tokens=500)