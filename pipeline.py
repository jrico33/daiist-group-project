"""
Retail-property incident triage (provisional business case, see REPORT.md).

A photo of a problem in a shopping centre goes through two connected components:

  A. Vision (Gemini): what is the problem, how severe, how sure is the model.
  B. Agentic LLM (Gemini with tools): reads A's output, looks up the response
     time and responsible team (tools) and drafts the work order.

Only the standard library is used for the API calls, so uv.lock does not change.
`run()` keeps the contract the rest of the template relies on (see the template's
docstring in git history): input_summary, features, outputs, versions, review,
tokens, cost_eur.
"""

import base64
import json
import mimetypes
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image, ImageStat

ROOT = Path(__file__).resolve().parent

MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite")  # 2.5 models: closed to new keys
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

VERSIONS = {
    "component_a": f"{MODEL}-vision-prompt-v1",
    "component_b": f"{MODEL}-agent-prompt-v1",
}

# Paid-tier standard prices per million tokens (output includes thinking tokens), in USD from
# https://ai.google.dev/gemini-api/docs/pricing, converted at the ECB reference rate of
# 25 Nov 2026: 1 EUR = 1.0935 USD (https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml).
USD_PER_EUR = 1.0935
PRICES_EUR_PER_M = {  # model: (input, output)
    "gemini-3.5-flash-lite": (0.30 / USD_PER_EUR, 2.50 / USD_PER_EUR),
    "gemini-3.8-flash": (0.75 / USD_PER_EUR, 3.75 / USD_PER_EUR),  # price valid through 31 Dec 2026
}
# A model that is not in the table is priced as the most expensive one, so its cost is not understated.
FALLBACK_PRICE = max(PRICES_EUR_PER_M.values())

# Review rule (justified in REPORT.md, Decision, with the evaluation numbers).
REVIEW_BELOW_CONFIDENCE = 0.7
REVIEW_FROM_SEVERITY = 4
# not_an_issue is reviewed too: in the evaluation, 7 of A's 15 wrong categories were not_an_issue,
# including both serious fire-safety cases (c15, c19), all at confidence 0.85 or more.
ALWAYS_REVIEW = {"fire_safety", "other_or_unclear", "not_an_issue"}

CATEGORIES = [
    "water_leak",
    "electrical",
    "broken_glass_or_structure",
    "cleanliness_or_waste",
    "signage_or_graffiti",
    "fire_safety",
    "other_or_unclear",
    "not_an_issue",
]

# --- Illustrative business data used by component B's tools. Fictional: replace with your assumptions.
TEAMS = {
    "water_leak": "Technical services",
    "electrical": "Technical services",
    "broken_glass_or_structure": "Technical services",
    "cleanliness_or_waste": "Cleaning contractor",
    "signage_or_graffiti": "Marketing and signage",
    "fire_safety": "Security and safety",
    "other_or_unclear": "Property manager",
}
RESPONSE_HOURS = {1: 72, 2: 48, 3: 24, 4: 8, 5: 2}


class MissingKey(RuntimeError):
    pass


# --- Gemini REST helper ----------------------------------------------------------

def _gemini(body: dict, model: str = MODEL) -> dict:
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        raise MissingKey("GEMINI_API_KEY is not set (see .env.example).")
    request = urllib.request.Request(
        API_URL.format(model=model),
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-goog-api-key": key},
    )
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            if error.code in (429, 500, 503) and attempt < 3:
                time.sleep(2 * (attempt + 1))
                continue
            raise RuntimeError(f"Gemini API error {error.code}: {error.read().decode('utf-8', 'replace')[:300]}") from error
    raise RuntimeError("Gemini API did not answer.")


def _usage(response: dict) -> tuple[int, int]:
    usage = response.get("usageMetadata", {})
    prompt = int(usage.get("promptTokenCount", 0))
    output = int(usage.get("candidatesTokenCount", 0)) + int(usage.get("thoughtsTokenCount", 0))
    return prompt, output


def _cost(prompt_tokens: int, output_tokens: int, model: str = MODEL) -> float:
    price_in, price_out = PRICES_EUR_PER_M.get(model, FALLBACK_PRICE)
    return (prompt_tokens * price_in + output_tokens * price_out) / 1_000_000


# --- Input -------------------------------------------------------------------------

def image_path(raw_input: str) -> Path:
    path = Path(str(raw_input).strip())
    if not path.is_absolute():
        path = ROOT / path
    if not path.is_file():
        raise ValueError("The input must be a photo (an image file).")
    return path


def input_features(path: Path) -> dict[str, float]:
    """Numbers that describe the photo, for the drift check."""
    with Image.open(path) as image:
        gray = image.convert("L")
        stat = ImageStat.Stat(gray)
        width, height = image.size
    return {
        "brightness": round(stat.mean[0], 2),
        "contrast": round(stat.stddev[0], 2),
        "megapixels": round(width * height / 1e6, 3),
        "aspect_ratio": round(width / height, 3),
    }


# --- Component A: vision -----------------------------------------------------------

PROMPT_A = (
    "You triage maintenance and safety reports for a shopping centre. Look at the photo and "
    "classify the problem. Categories: " + ", ".join(CATEGORIES) + ". Use not_an_issue when the "
    "photo shows no problem and other_or_unclear when you cannot tell. Severity is 1 (cosmetic) "
    "to 5 (immediate danger to people or property). Confidence is your honest probability, "
    "between 0 and 1, that the category is right. In `description` write one factual sentence "
    "about the problem and never describe or identify people."
)

SCHEMA_A = {
    "type": "OBJECT",
    "properties": {
        "category": {"type": "STRING", "format": "enum", "enum": CATEGORIES},
        "severity": {"type": "INTEGER"},
        "confidence": {"type": "NUMBER"},
        "description": {"type": "STRING"},
    },
    "required": ["category", "severity", "confidence", "description"],
}


def component_a(path: Path) -> dict:
    mime = mimetypes.guess_type(path.name)[0] or "image/jpeg"
    body = {
        "contents": [{"parts": [
            {"text": PROMPT_A},
            {"inline_data": {"mime_type": mime, "data": base64.b64encode(path.read_bytes()).decode("ascii")}},
        ]}],
        "generationConfig": {
            "temperature": 0,
            "responseMimeType": "application/json",
            "responseSchema": SCHEMA_A,
        },
    }
    response = _gemini(body)
    text = response["candidates"][0]["content"]["parts"][0]["text"]
    result = json.loads(text)
    result["category"] = result["category"] if result["category"] in CATEGORIES else "other_or_unclear"
    result["severity"] = min(5, max(1, int(result["severity"])))
    result["confidence"] = round(min(1.0, max(0.0, float(result["confidence"]))), 3)
    prompt_tokens, output_tokens = _usage(response)
    result["tokens"] = prompt_tokens + output_tokens
    result["cost_eur"] = _cost(prompt_tokens, output_tokens)
    return result


# --- Component B: agent with tools -------------------------------------------------

def lookup_sla(category: str, severity: int) -> dict:
    team = TEAMS.get(category)
    if team is None:
        return {"error": f"unknown category {category}"}
    severity = min(5, max(1, int(severity)))
    return {"team": team, "response_hours": RESPONSE_HOURS[severity]}


def lookup_contact(team: str) -> dict:
    # Fictional contacts: no personal data, only team mailboxes.
    return {"mailbox": team.lower().replace(" ", "-") + "@example-centre.test"}


TOOLS = {"lookup_sla": lookup_sla, "lookup_contact": lookup_contact}

TOOL_DECLARATIONS = [{"functionDeclarations": [
    {
        "name": "lookup_sla",
        "description": "Responsible team and maximum response time in hours for an incident category and severity (1-5).",
        "parameters": {"type": "OBJECT", "properties": {
            "category": {"type": "STRING"}, "severity": {"type": "INTEGER"}}, "required": ["category", "severity"]},
    },
    {
        "name": "lookup_contact",
        "description": "Team mailbox to which a work order must be sent.",
        "parameters": {"type": "OBJECT", "properties": {"team": {"type": "STRING"}}, "required": ["team"]},
    },
]}]

SYSTEM_B = (
    "You are the operations assistant of a shopping centre. You receive the result of an image "
    "classifier (category, severity, confidence, description). If the category is not_an_issue, "
    "answer that no work order is needed. Otherwise call lookup_sla, then lookup_contact for the "
    "responsible team, and write a short work order: title, team, mailbox, deadline in hours, and "
    "two sentences of instructions. Use only what the tools return. Do not invent names or people."
)


def component_b(a: dict) -> dict:
    visible = {k: a[k] for k in ("category", "severity", "confidence", "description")}
    contents = [{"role": "user", "parts": [{"text": "Classifier result: " + json.dumps(visible)}]}]
    calls, prompt_tokens, output_tokens = [], 0, 0
    reply = ""
    for _ in range(5):
        response = _gemini({
            "systemInstruction": {"parts": [{"text": SYSTEM_B}]},
            "contents": contents,
            "tools": TOOL_DECLARATIONS,
            "generationConfig": {"temperature": 0},
        })
        p, o = _usage(response)
        prompt_tokens, output_tokens = prompt_tokens + p, output_tokens + o
        content = response["candidates"][0]["content"]
        contents.append(content)
        function_calls = [part["functionCall"] for part in content.get("parts", []) if "functionCall" in part]
        if not function_calls:
            reply = "".join(part.get("text", "") for part in content.get("parts", [])).strip()
            break
        parts = []
        for call in function_calls:
            tool = TOOLS.get(call["name"])
            args = call.get("args", {})
            result = tool(**args) if tool else {"error": "unknown tool"}
            calls.append({"tool": call["name"], "args": args, "result": result})
            parts.append({"functionResponse": {"name": call["name"], "response": result}})
        contents.append({"role": "user", "parts": parts})
    return {
        "reply": reply or "No work order could be produced; a person must handle this report.",
        "tool_calls": calls,
        "tokens": prompt_tokens + output_tokens,
        "cost_eur": _cost(prompt_tokens, output_tokens),
    }


# --- The chain ---------------------------------------------------------------------

def run(raw_input: str) -> dict:
    path = image_path(raw_input)
    features = input_features(path)
    a = component_a(path)
    b = component_b(a)
    features = features | {"confidence": a["confidence"], "severity": float(a["severity"])}
    review = (
        a["confidence"] < REVIEW_BELOW_CONFIDENCE
        or a["severity"] >= REVIEW_FROM_SEVERITY
        or a["category"] in ALWAYS_REVIEW
        or not b["tool_calls"] and a["category"] != "not_an_issue"
    )
    out_a = {k: a[k] for k in ("category", "severity", "confidence", "description", "tokens", "cost_eur")}
    out_b = {k: b[k] for k in ("reply", "tool_calls", "tokens", "cost_eur")}
    return {
        "input_summary": f"photo {path.name}: {a['category']}, severity {a['severity']}",
        "features": features,
        "outputs": {"component_a": out_a, "component_b": out_b},
        "versions": VERSIONS,
        "review": bool(review),
        "tokens": a["tokens"] + b["tokens"],
        "cost_eur": round(a["cost_eur"] + b["cost_eur"], 6),
    }
