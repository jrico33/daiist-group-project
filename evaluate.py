"""
Evaluation of the incident-triage product. `uv run python main.py evaluate`

Conventions for eval/cases.csv (details in TEAM_TODO.md):
  input     path of a photo under eval/inputs/, e.g. eval/inputs/c01.jpg
  expected  the correct category, optionally with the severity: "water_leak|4".
            For `out_of_scope` cases use "not_an_issue".
  baseline  what a person does today with this case, starting with "correct" or
            "wrong" and then a note: "wrong: sent to cleaning, it was a leak".

What it reports (copy the numbers into REPORT.md; eval/results.csv is written):
  1. Component A (vision) alone: accuracy, macro-F1, severity within +-1.
  2. Component B (agent) alone, fed with the human-correct output of A: did it use
     its tools correctly, is the reply consistent with them, and what an LLM judge says.
  3. End to end against the baseline, with the cases that failed grouped by cause.
  4. The review rule, cost per request and per month, latency.
  5. The judge's agreement with eval/human_labels.csv (id,label,comment; label pass/fail).

Model outputs are cached in logs/eval_cache.json (git-ignored), so re-running costs
nothing for cases that did not change. Delete that file to start from scratch.
"""

import csv
import hashlib
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

import env
import pipeline

ROOT = Path(__file__).resolve().parent
CASES = ROOT / "eval" / "cases.csv"
RESULTS = ROOT / "eval" / "results.csv"
HUMAN_LABELS = ROOT / "eval" / "human_labels.csv"
CACHE_FILE = ROOT / "logs" / "eval_cache.json"

# Same assumptions as the business case in REPORT.md: change both together.
REPORTS_PER_DAY = 40
DAYS_PER_MONTH = 30

_cache: dict = json.loads(CACHE_FILE.read_text()) if CACHE_FILE.is_file() else {}


def cached(key: str, compute):
    if key not in _cache:
        _cache[key] = compute()
        CACHE_FILE.parent.mkdir(exist_ok=True)
        CACHE_FILE.write_text(json.dumps(_cache))
    return _cache[key]


def fingerprint(raw_input: str) -> str:
    path = Path(raw_input.strip())
    path = path if path.is_absolute() else ROOT / path
    data = path.read_bytes() if path.is_file() else raw_input.encode("utf-8")
    return hashlib.sha256(data).hexdigest()[:16]


def parse_expected(text: str) -> tuple[str, int | None]:
    category, _, severity = (text or "").partition("|")
    return category.strip(), int(severity) if severity.strip().isdigit() else None


# --- Running the product ----------------------------------------------------------

def run_case(case: dict) -> dict:
    key = f"run|{fingerprint(case['input'])}|{json.dumps(pipeline.VERSIONS, sort_keys=True)}"

    def compute():
        started = time.perf_counter()
        result = pipeline.run(case["input"])
        return {"result": result, "latency_s": round(time.perf_counter() - started, 3)}

    return cached(key, compute)


def run_b_alone(case: dict, description: str) -> tuple[dict, dict]:
    """Component B fed with the human-correct output of A, so A's mistakes do not count against B."""
    category, severity = parse_expected(case["expected"])
    a_true = {"category": category, "severity": severity or 3, "confidence": 1.0, "description": description}
    key = f"b|{fingerprint(case['input'])}|{category}|{a_true['severity']}|{pipeline.VERSIONS['component_b']}"
    return a_true, cached(key, lambda: pipeline.component_b(a_true))


# --- Checks that code can do ------------------------------------------------------

def tools_ok(a: dict, tool_calls: list[dict]) -> bool:
    """Did B call the tools with A's output, and pass the team from the first to the second?"""
    if a["category"] == "not_an_issue":
        return not tool_calls
    sla = next((c for c in tool_calls if c["tool"] == "lookup_sla"), None)
    contact = next((c for c in tool_calls if c["tool"] == "lookup_contact"), None)
    if not sla or not contact:
        return False
    if sla["args"].get("category") != a["category"] or int(sla["args"].get("severity", -1)) != a["severity"]:
        return False
    return contact["args"].get("team") == sla["result"].get("team")


def reply_ok(a: dict, reply: str, tool_calls: list[dict]) -> bool:
    """Is the reply consistent with the tool results (team and deadline stated)?"""
    text = reply.lower()
    if a["category"] == "not_an_issue":
        return "no work order" in text or "not needed" in text or "no action" in text
    sla = next((c for c in tool_calls if c["tool"] == "lookup_sla"), None)
    if not sla or "team" not in sla["result"]:
        return False
    return sla["result"]["team"].lower() in text and str(sla["result"]["response_hours"]) in text


def is_correct(case: dict, result: dict) -> bool | None:
    """End-to-end correctness, by kind of case."""
    category, severity = parse_expected(case["expected"])
    a = result["outputs"]["component_a"]
    kind = case["kind"].strip().lower()
    if kind == "review":
        return bool(result["review"])  # the right outcome is that a person sees it
    if kind == "out_of_scope":
        return a["category"] in ("not_an_issue", "other_or_unclear") or bool(result["review"])
    ok = a["category"] == category
    if severity is not None:
        ok = ok and abs(a["severity"] - severity) <= 1
    return ok


def failure_cause(case: dict, result: dict, tool_ok: bool, reply_consistent: bool) -> str:
    category, severity = parse_expected(case["expected"])
    a = result["outputs"]["component_a"]
    kind = case["kind"].strip().lower()
    if kind == "review":
        return "review rule: case was not sent to a person"
    if kind == "out_of_scope":
        return "A: out-of-scope photo taken as a real incident"
    if a["category"] != category:
        return "A: wrong category"
    if severity is not None and abs(a["severity"] - severity) > 1:
        return "A: severity off by more than 1"
    if not tool_ok:
        return "hand-off A to B: wrong tool use"
    if not reply_consistent:
        return "B: reply inconsistent with the tools"
    return "other"


# --- LLM judge --------------------------------------------------------------------

# Fixed, so that every model under test is graded by the same judge.
JUDGE_MODEL = "gemini-3.8-flash"
# eval/human_labels.csv labels the work orders written by this model; they say nothing about another model's.
LABELLED_MODEL = "gemini-3.5-flash-lite"

JUDGE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "verdict": {"type": "STRING", "format": "enum", "enum": ["pass", "fail"]},
        "reason": {"type": "STRING"},
    },
    "required": ["verdict", "reason"],
}

JUDGE_PROMPT = """You grade a work order drafted for a shopping centre's operations team.
Rubric. Pass only if all of these hold: (1) the work order matches the classifier result
below (category and urgency); (2) the team, mailbox and deadline come from the tool results
below and are stated correctly; (3) it invents nothing (no names, no facts that are not in
the inputs); (4) it is short and clear enough to act on. If the category is not_an_issue,
pass only if it says that no work order is needed.

Classifier result: {a}
Tool results: {tools}
Work order to grade: {reply}"""


def judge(case_id: str, a: dict, reply: str, tool_calls: list[dict]) -> dict:
    key = f"judge|{JUDGE_MODEL}|{case_id}|{hashlib.sha256(reply.encode()).hexdigest()[:16]}|{json.dumps(a, sort_keys=True)}"

    def compute():
        visible = {k: a[k] for k in ("category", "severity", "confidence", "description")}
        prompt = JUDGE_PROMPT.format(a=json.dumps(visible), tools=json.dumps(tool_calls), reply=reply)
        response = pipeline._gemini({
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0, "responseMimeType": "application/json", "responseSchema": JUDGE_SCHEMA},
        }, model=JUDGE_MODEL)
        out = json.loads(response["candidates"][0]["content"]["parts"][0]["text"])
        prompt_tokens, output_tokens = pipeline._usage(response)
        out["cost_eur"] = pipeline._cost(prompt_tokens, output_tokens, model=JUDGE_MODEL)
        return out

    return cached(key, compute)


def judge_agreement(verdicts: dict[str, str]) -> tuple[int, float, float] | None:
    """(labels compared, raw agreement, Cohen's kappa) between the judge and eval/human_labels.csv."""
    if not HUMAN_LABELS.is_file():
        return None
    labels = pd.read_csv(HUMAN_LABELS, dtype=str).dropna(subset=["id", "label"]).drop_duplicates("id")
    human = dict(zip(labels["id"].str.strip(), labels["label"].str.strip().str.lower()))
    pairs = [(human[i], v) for i, v in verdicts.items() if i in human]
    if not pairs:
        return None
    n = len(pairs)
    observed = sum(h == j for h, j in pairs) / n
    chance = sum((sum(h == c for h, _ in pairs) / n) * (sum(j == c for _, j in pairs) / n) for c in ("pass", "fail"))
    kappa = (observed - chance) / (1 - chance) if chance < 1 else float("nan")
    return n, observed, kappa


def macro_f1(truth: list[str], predicted: list[str]) -> float:
    scores = []
    for label in sorted(set(truth)):
        tp = sum(t == label and p == label for t, p in zip(truth, predicted))
        fp = sum(t != label and p == label for t, p in zip(truth, predicted))
        fn = sum(t == label and p != label for t, p in zip(truth, predicted))
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        scores.append(2 * precision * recall / (precision + recall) if precision + recall else 0.0)
    return float(np.mean(scores)) if scores else float("nan")


def heading(text: str) -> None:
    print(f"\n=== {text} ".ljust(78, "="))


def main() -> None:
    env.load_env()
    with CASES.open(newline="", encoding="utf-8") as f:
        cases = [r for r in csv.DictReader(f) if (r.get("input") or "").strip()]
    rows, judge_cost = [], 0.0
    for i, case in enumerate(cases, 1):
        print(f"  {i}/{len(cases)}", end="\r", flush=True)
        kind = case["kind"].strip().lower()
        category, severity = parse_expected(case["expected"])
        row = {"id": case["id"], "kind": kind, "expected": case["expected"]}
        try:
            run = run_case(case)
            result = run["result"]
            a, b = result["outputs"]["component_a"], result["outputs"]["component_b"]
            tool_ok, reply_consistent = tools_ok(a, b["tool_calls"]), reply_ok(a, b["reply"], b["tool_calls"])
            correct = is_correct(case, result)
            verdict = judge(case["id"], a, b["reply"], b["tool_calls"])
            judge_cost += verdict["cost_eur"]

            a_true, b_alone = run_b_alone(case, a["description"])
            alone_tools = tools_ok(a_true, b_alone["tool_calls"])
            alone_reply = reply_ok(a_true, b_alone["reply"], b_alone["tool_calls"])
            alone_verdict = judge(case["id"] + "-alone", a_true, b_alone["reply"], b_alone["tool_calls"])
            judge_cost += alone_verdict["cost_eur"]

            row |= {
                "category": a["category"], "severity": a["severity"], "confidence": a["confidence"],
                "review": result["review"], "correct": correct,
                "cause": "" if correct else failure_cause(case, result, tool_ok, reply_consistent),
                "tools_ok": tool_ok, "reply_ok": reply_consistent, "judge": verdict["verdict"],
                "b_alone_tools_ok": alone_tools, "b_alone_reply_ok": alone_reply, "b_alone_judge": alone_verdict["verdict"],
                "tokens_a": a["tokens"], "tokens_b": b["tokens"],
                "latency_s": run["latency_s"], "tokens": result["tokens"], "cost_eur": result["cost_eur"],
                "cost_a_eur": a.get("cost_eur", 0.0), "cost_b_eur": b.get("cost_eur", 0.0),
                "baseline_correct": case["baseline"].strip().lower().startswith("correct")
                if case["baseline"].strip().lower().startswith(("correct", "wrong")) else None,
                "outputs": json.dumps(result["outputs"], ensure_ascii=False),
            }
        except Exception as error:  # noqa: BLE001 - a failing case is a finding, not a crash
            row |= {"correct": False, "cause": f"error: {type(error).__name__}: {str(error)[:80]}", "review": True}
        rows.append(row)

    results = pd.DataFrame(rows)
    results.to_csv(RESULTS, index=False)
    print(f"Wrote {RESULTS.relative_to(ROOT)} ({len(results)} cases).")
    done = results[results["cause"].fillna("").str.startswith("error") == False]  # noqa: E712
    if done.empty:
        print("No case ran successfully: check GEMINI_API_KEY and the errors in the `cause` column.")
        return

    print(f"model under test: {pipeline.MODEL}   judge: {JUDGE_MODEL}")
    heading("1. Component A (vision) alone")
    truth = [parse_expected(e)[0] for e in done["expected"]]
    predicted = done["category"].tolist()
    print(f"cases {len(done)}   accuracy {np.mean([t == p for t, p in zip(truth, predicted)]):.1%}   macro-F1 {macro_f1(truth, predicted):.3f}")
    with_severity = [(parse_expected(e)[1], s) for e, s in zip(done["expected"], done["severity"]) if parse_expected(e)[1] is not None]
    if with_severity:
        print(f"severity within +-1: {np.mean([abs(t - s) <= 1 for t, s in with_severity]):.1%} of {len(with_severity)} cases with an expected severity")
    print("(these cases are also the end-to-end set: say so in REPORT.md, or hold some out)")

    heading("2. Component B (agent) alone, given the human-correct output of A")
    print(f"tools used correctly {done['b_alone_tools_ok'].mean():.1%}   reply consistent with tools {done['b_alone_reply_ok'].mean():.1%}   judge pass {(done['b_alone_judge'] == 'pass').mean():.1%}")

    heading("3. End to end against the baseline")
    by_kind = done.groupby("kind").agg(
        cases=("id", "count"), correct=("correct", "mean"), sent_to_review=("review", "mean"),
        median_latency_s=("latency_s", "median"), mean_cost_eur=("cost_eur", "mean"),
    )
    print(by_kind.round(3).to_string())
    print(f"\nproduct correct {done['correct'].mean():.1%} of {len(done)}")
    known = done.dropna(subset=["baseline_correct"])
    if len(known):
        print(f"baseline correct {known['baseline_correct'].astype(bool).mean():.1%} of {len(known)} cases with a baseline verdict")
    else:
        print("baseline: start the `baseline` column of cases.csv with 'correct' or 'wrong' to compare")
    failed = done[done["correct"] == False]  # noqa: E712
    print("\nFailures by cause:")
    print(failed["cause"].value_counts().to_string() if len(failed) else "  none")

    heading("4. Review rule, cost and latency")
    need = done[done["kind"] == "review"]
    normal = done[done["kind"] == "normal"]
    if len(need):
        print(f"review cases sent to a person: {need['review'].mean():.0%} of {len(need)}")
    if len(normal):
        print(f"normal cases sent to a person: {normal['review'].mean():.0%} of {len(normal)}")
    print(f"at {REPORTS_PER_DAY} reports a day, about {done['review'].mean() * REPORTS_PER_DAY:.0f} go to a person each day (all cases mixed)")
    print(f"cost per request: €{done['cost_eur'].mean():.5f} (A €{done['cost_a_eur'].mean():.5f}, B €{done['cost_b_eur'].mean():.5f}), "
          f"{done['tokens'].mean():.0f} tokens, median {done['latency_s'].median():.1f} s")
    print(f"tokens per request: A {done['tokens_a'].mean():.0f}, B {done['tokens_b'].mean():.0f}")
    print(f"latency: median {done['latency_s'].median():.1f} s, worst case {done['latency_s'].max():.1f} s ({done.loc[done['latency_s'].idxmax(), 'id']}); "
          f"cost: median €{done['cost_eur'].median():.5f}, worst case €{done['cost_eur'].max():.5f}; "
          f"tokens: median {done['tokens'].median():.0f}, worst case {done['tokens'].max():.0f}")
    print(f"end-to-end judge pass {(done['judge'] == 'pass').mean():.1%}   (judge: {JUDGE_MODEL})")
    print(f"sent to a person: {done['review'].mean():.1%} of {len(done)}")
    serious = done[[c == "fire_safety" or (s or 0) >= 4 for c, s in map(parse_expected, done["expected"])]]
    print(f"serious cases (expected fire_safety or severity 4-5): {len(serious)}, not sent to a person: "
          f"{int((~serious['review'].astype(bool)).sum())}, wrong category: {sum(parse_expected(e)[0] != c for e, c in zip(serious['expected'], serious['category']))}")
    print("review rule variants (wrong category = A's category differs from the expected one, all kinds):")
    wrong = done["category"] != done["expected"].map(lambda e: parse_expected(e)[0])
    variants = {f"confidence below {t}": done["review"].astype(bool) | (done["confidence"] < t) for t in (0.7, 0.8, 0.9, 0.95, 0.99)}
    variants["current rule + every not_an_issue"] = done["review"].astype(bool) | (done["category"] == "not_an_issue")
    for name, sent in variants.items():
        is_serious = done["id"].isin(serious["id"])
        print(f"  {name}: sent {sent.mean():.1%} ({sent.mean() * REPORTS_PER_DAY:.0f}/day), wrong category caught {int((sent & wrong).sum())} of {int(wrong.sum())}, "
              f"review cases sent {int((sent & (done['kind'] == 'review')).sum())} of {len(need)}, serious caught {int((sent & is_serious).sum())} of {len(serious)}")
    print(f"per month at {REPORTS_PER_DAY}/day: €{done['cost_eur'].mean() * REPORTS_PER_DAY * DAYS_PER_MONTH:.2f}")
    print(f"(judge calls for this evaluation cost €{judge_cost:.4f}, not part of the product's cost)")

    heading("5. LLM judge against your labels")
    verdicts = dict(zip(done["id"], done["judge"]))
    stats = judge_agreement(verdicts) if pipeline.MODEL == LABELLED_MODEL else None
    if pipeline.MODEL != LABELLED_MODEL:
        print(f"not computed: the labels are for {LABELLED_MODEL}'s work orders")
        return
    if stats is None:
        print("no overlap with eval/human_labels.csv: label at least 20 cases (id,label,comment; label pass/fail)")
    else:
        n, observed, kappa = stats
        print(f"{n} labelled cases: agreement {observed:.0%}, Cohen's kappa {kappa:.2f}; {sum(1 for i, v in verdicts.items() if v == 'fail')} judge fails" + ("" if n >= 20 else "  (fewer than the 20 required)"))


if __name__ == "__main__":
    main()
