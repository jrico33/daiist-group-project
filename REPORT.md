# Group Assignment Report

- **Team** (Blackboard group name):
- **Section**: [BBADBA 5A | BBADBA 5B | PPLEDBA 5A]
- **App URL** (on Render):
- **Final commit** (tag `final`):

*At most about 3,000 words, tables excluded. Members and who did what go in CONTRIBUTIONS.md.*

## Business case

*Provisional draft (22 Nov 2026): the team must confirm or change it, and replace every assumption marked [A] with real figures.*

**Users.** The operations team of a shopping centre (property or centre manager and technical-services coordinator). Tenants, security staff and visitors send photos of problems: leaks, broken glass, electrical faults, waste, graffiti, fire-safety issues.

**Decision.** For each incident photo: what is wrong, how urgent it is, which team must act, and by when. A work order is drafted automatically. Uncertain or serious cases go to a person before anything is sent.

**Baseline (today).** A person opens each report, looks at the photo, classifies it and forwards it by email to the right team. [A] About 4 minutes per report, and about 10% of reports are routed to the wrong team or given the wrong priority.

**Success metric.** (1) Share of reports with the correct category and team against a person's labels in `eval/cases.csv`, compared with the baseline; (2) share of serious incidents (severity 4-5) that are never missed or delayed; (3) minutes of staff time per report.

**Value in euros.** [A] A medium centre receives about 40 reports a day, about 14,600 a year. If the product handles 70% automatically, with 1 minute of review instead of 4 minutes of manual work, it saves about 2.1 minutes per report on average, which is about 510 staff hours a year. At a loaded cost of 30 EUR per hour that is about 15,000 EUR a year per centre, before API costs (to be measured in the Evaluation section).

## Architecture

```
photo (JPG or PNG)
   |
   v
[A. Vision: Gemini]   ->  category, severity 1-5, confidence, one-sentence description
   |
   v
[B. Agent: Gemini + tools]   calls lookup_sla(category, severity)  ->  team, deadline in hours
   |                         calls lookup_contact(team)             ->  team mailbox
   v
drafted work order  +  review rule (a person sees uncertain or serious cases)
```

**One request.** The user uploads a photo in the App tab. The pipeline computes simple image features (brightness, contrast, size) for the drift check, then sends the photo to component A, which returns a category, a severity, a confidence and a description as structured JSON. Component B receives only that output, not the photo: it calls `lookup_sla` for the responsible team and the deadline, then `lookup_contact` for the team mailbox, and writes a short work order. The review rule sends the case to a person if the confidence is below 0.7, the severity is 4 or more, the category is fire safety or unclear, or B made no tool calls. The input summary, features, both outputs, versions, latency, tokens, cost and the user's thumbs up or down are logged.

**Models and why.** Both components use Gemini through its REST API (the model name is in `pipeline.py` and can be changed with `GEMINI_MODEL`). The course allows a free Gemini key, one API offers vision and function calling, and nothing heavy has to run on Render's 512 MB free service. The tools are plain Python functions over fictional teams, deadlines and mailboxes [A: replace them with the real policy of the centre].

**Reused from assignments 1-3.** Nothing so far. [TODO: the team states any reused code, whose it was and where it is.]

## Data

*Where each component's data comes from, with links, licences and sizes. Confirm that there is no personal data in your inputs or logs.*

**Photos for cases c29 to c40** (`eval/inputs/c29.jpeg` to `c40.jpeg`, taken by Juan Jacobo). These are our own photos, taken with a phone on 22 November 2026 at home, so no third-party source or licence is involved. They were resized to about 1,000 pixels wide (72 to 340 KB each, about 2.6 MB in total) and the location metadata was removed. They are 12 of the 40 evaluation cases:

- c29 to c34 (kind `review`): photos a person should look at before anything is sent, because they are hard to read: motion blur, an extreme close-up of a rug, a flat white wall, an almost black frame, a view through a glass door with a glove and a shoe, and a rubbish bag with its reflection in the glass.
- c35 to c40 (kind `out_of_scope`): everyday objects that are not a clear incident: a glass bottle, a kitchen oven, a shoe and a remote control on a carpet, a phone charger and cable on the floor, a padel racket with shoes, and a sweet on a tablecloth.

**Photos for cases c15 to c28** (`eval/inputs/c15.jpg` to `c28.jpg`, chosen and labelled by Máximo). These come from Wikimedia Commons, all under licences that allow reuse: public domain, CC0 or CC BY (no ShareAlike or NonCommercial licences). They were chosen on 25 November 2026 to look like phone photos of a shopping centre, and photos with people, readable number plates or derelict buildings were left out. We changed them only by resizing them to at most 1,024 pixels wide (56 to 276 KB each, about 2.2 MB in total) and removing all metadata. They are 14 of the 40 evaluation cases:

- c15 to c18 (kind `normal`): one clear problem each: an extinguisher left on the floor, a water stain on a ceiling tile, a hole in a glass block wall and graffiti on a roller shutter.
- c19 to c28 (kind `hard`): photos that can mislead the product: the problem is small in the frame (an extinguisher on the floor of a wide entrance, a cigarette butt, a thin crack in a mirror), the photo is in poor conditions (a sign at night, litter among leaves outdoors), the problem is already handled (a wet floor cone), no category fits (a vending machine out of order), or two categories are plausible (a hanging bulb in front of graffiti, tiles removed by a burst pipe, peeling paint with water stains).

| Case | Source (Wikimedia Commons) | Author | Licence |
|---|---|---|---|
| c15 | [Extintor con cártel](https://commons.wikimedia.org/wiki/File:Extintor_con_c%C3%A1rtel.jpg) | Panxitofeliz | CC BY 2.5 es |
| c16 | [Ceiling water damage](https://commons.wikimedia.org/wiki/File:Ceiling_water_damage.jpg) | Atomicdragon136 | CC BY 3.0 |
| c17 | [Broken glass brick (4873065758)](https://commons.wikimedia.org/wiki/File:Broken_glass_brick_%284873065758%29.jpg) | Yannick Bammert | CC BY 2.0 |
| c18 | [Garage door graffiti-vandalism](https://commons.wikimedia.org/wiki/File:Garage_door_graffiti-vandalism.jpg) | Francki | Public domain |
| c19 | [Estação Sul e Sueste 03](https://commons.wikimedia.org/wiki/File:Esta%C3%A7%C3%A3o_Sul_e_Sueste_03.jpg) | DiogoBaptista | CC0 |
| c20 | [Stickers on a Sign (9698436958)](https://commons.wikimedia.org/wiki/File:Stickers_on_a_Sign_%289698436958%29.jpg) | Paul Sableman | CC BY 2.0 |
| c21 | [Cigarette Butt Litter](https://commons.wikimedia.org/wiki/File:Cigarette_Butt_Litter.jpg) | Qwertyxp2000 | CC BY 4.0 |
| c22 | [Orange wet floor caution tent in use in a bathroom 1](https://commons.wikimedia.org/wiki/File:Orange_wet_floor_caution_tent_in_use_in_a_bathroom_1.jpg) | Ser Amantio di Nicolao | CC0 |
| c23 | [Out of order Coca-Cola vending machine, Syracuse, NY](https://commons.wikimedia.org/wiki/File:Out_of_order_Coca-Cola_vending_machine,_Syracuse,_NY.jpg) | Michael Scialdone | CC BY 2.0 |
| c24 | [FastFries](https://commons.wikimedia.org/wiki/File:FastFries.jpg) | Jasmin Sessler | CC BY 4.0 |
| c25 | [Rohrbruch 001](https://commons.wikimedia.org/wiki/File:Rohrbruch_001.jpg) | Pictureme | CC0 |
| c26 | [CFL (3654586485)](https://commons.wikimedia.org/wiki/File:CFL_%283654586485%29.jpg) | Paul Keller | CC BY 2.0 |
| c27 | [Gebrochener Spiegel, Austria](https://commons.wikimedia.org/wiki/File:Gebrochener_Spiegel,_Austria.jpg) | Naturpuur | CC BY 4.0 |
| c28 | [Ceiling sheetrock damaged by water so paint was peeling](https://commons.wikimedia.org/wiki/File:Ceiling_sheetrock_damaged_by_water_so_paint_was_peeling.jpg) | Tomwsulcer | CC0 |

**Personal data.** No person appears in c15 to c28, and they show no names, documents or readable number plates; one shows a house number on a shutter (c18) and some show brand names (a vending machine, a food wrapper). No person is in the foreground of c29 to c40. One photo (c29) shows a laptop screen whose wallpaper has two small, blurred figures, not identifiable; the team decided to keep it. Some photos show product brand names (an oven, a remote control, a racket, shoes) and no names, number plates or documents. The other members' photos and the reference and shifted sets are described by their authors [TODO].

## Evaluation

### Components

Test data: the 40 cases of `eval/cases.csv` (18 normal, 10 hard, 6 review, 6 out of scope). They are also the end-to-end set: nothing was held out, and nothing was tuned on them. Default model: `gemini-3.5-flash-lite` (the 2.5 models are closed to new keys). All numbers come from `eval/eval_run_flash_lite.txt` (default) and `eval/eval_run_flash.txt` (`gemini-3.8-flash`).

**Component A (vision), 40 cases.** Accuracy 62.5%, macro-F1 0.581. Severity within ±1: 100.0% of 2 cases. **Limitation: only 2 of 40 cases have an expected severity** (c38, c40), so this says nothing about severity in general, and the review rule and deadlines both depend on severity.

**Component B (agent) alone, 40 cases.** B is fed the human-correct category, the expected severity (3 when there is none) and A's description. Tools used correctly 95.0%, reply consistent with the tools 95.0%, judge pass 92.5%. The judge fails are c12, c29 and c31; the tool and reply checks fail on c29 and c31. In these three cases A's description ("no visible damage") contradicts the correct category, so they partly reflect how the test is built: B followed the description in c29 and c31.

### End to end

Two examples: c16 (normal), a stained ceiling tile, expected `water_leak`; c26 (hard), a hanging bulb in front of graffiti, expected `electrical`. Normal and hard cases are correct if the category matches (and the severity is within ±1 when given); review cases if a person sees them; out-of-scope cases if A answers `not_an_issue` or `other_or_unclear`, or a person sees them.

| Kind | Cases | Product correct | Sent to review |
|---|---|---|---|
| normal | 18 | 66.7% | 11.1% |
| hard | 10 | 60.0% | 0.0% |
| review | 6 | 16.7% | 16.7% |
| out_of_scope | 6 | 50.0% | 0.0% |
| **All** | **40** | **55.0%** | **7.5%** |

**The product is below the baseline: 55.0% against 90.0% correct, on the same 40 cases.** The baseline is what the case authors wrote that staff would do (36 "correct", 4 "wrong"), not measured staff performance, so 90.0% may flatter people. For c38 and c40 the expected label is a real category but the kind is out of scope: A gave the expected category and the case still counts as failed.

**Review rule.** It sends 7.5% of cases to a person, about 3 a day at 40 reports a day: 1 of 6 review cases (17%) and 2 of 18 normal cases (11%). The confidence threshold of 0.7 never fired, because A's lowest confidence was 0.85: every case sent was for severity or category.

**Judge.** Rubric: the work order matches A's result, takes team, mailbox and deadline from the tools, invents nothing, and is short and clear; it never sees the photo. The judge is `gemini-3.8-flash` for both runs, so it grades its own output in the 3.8 run. The intended check on that is agreement with human labels, but Gonzalo Angulo's 40 labels are for the flash-lite work orders, so the 3.8 judge result has no human check.

Labelling rule: pass = the work order is consistent with A's output and actionable; fail = it contradicts itself or doesn't say what to do (c01, c13, c30). Claude proposed each label with a reason, without seeing the judge's verdicts, and Gonzalo Angulo confirmed all 40.

The judge passed 100.0% of the work orders; the labels pass 37 of 40. **Agreement 92%, Cohen's kappa 0.00**: the judge agrees only because it passes everything, and it caught none of the 3 human fails. Its end-to-end pass rate is therefore not evidence of quality (it did fail 3 of B-alone's replies, so it can fail one).

**Model comparison** (same 40 cases, prompts, rule and judge):

| | gemini-3.5-flash-lite | gemini-3.8-flash |
|---|---|---|
| A accuracy / macro-F1 | 62.5% / 0.581 | 75.0% / 0.758 |
| Product correct (baseline 90.0%) | 55.0% | 72.5% |
| by kind: normal / hard / review / out of scope | 66.7 / 60.0 / 16.7 / 50.0% | 83.3 / 70.0 / 33.3 / 83.3% |
| Sent to review | 7.5% | 15.0% |
| Serious cases not sent to a person | 2 of 2 | 1 of 2 |
| Judge pass, end to end (see kappa above) | 100.0% | 100.0% (grades itself) |
| B alone: tools / reply / judge | 95.0 / 95.0 / 92.5% | 100.0 / 100.0 / 100.0% (grades itself) |
| Mean cost per request | €0.00088 | €0.00382 |
| Cost per month at 40/day | €1.06 | €4.58 |
| Latency, median / worst | 4.2 s / 5.1 s | 15.0 s / 21.4 s |

**Which to keep:** on these numbers `gemini-3.8-flash`, because it is right on 7 more cases (29 against 22) and loses none that flash-lite gets right, for €3.52 more a month and about 11 s more per request; neither beats the baseline. The default in `pipeline.py` is still flash-lite until the team decides.

### Cost and latency

Per request, default model (40 cases):

| | Tokens (mean) | Cost (mean) | Median | Worst case |
|---|---|---|---|---|
| A (vision) | 1,272 | €0.00046 | | |
| B (agent) | 848 | €0.00042 | | |
| Total | 2,120 | €0.00088 | €0.00098, 2,306 tokens, 4.2 s | €0.00104, 2,359 tokens, 5.1 s |

Per month at 40 reports a day (30 days): **€1.06**. With `gemini-3.8-flash`: 2,902 tokens (A 1,510, B 1,391), €0.00382 (A €0.00184, B €0.00198), median €0.00410, 3,190 tokens and 15.0 s, worst €0.00592, 3,711 tokens and 21.4 s, €4.58 a month.

Prices are Google's paid-tier prices on 25 Nov 2026, converted at the ECB rate of that day (1 EUR = 1.0935 USD; see `pipeline.py`); the 3.8 price is valid through 31 Dec 2026. With a free key the real cost is zero. Latency is measured for the whole chain, not per component, from one laptop. In the first 3.8 pass two cases ended in a read timeout (90 s limit) and succeeded on retry; the worst case above does not include them. The judge's calls (€0.1237 for the default run, €0.1176 for 3.8) are not part of the product's cost.

**How to rerun:** `uv run python main.py evaluate` (for the other model, put `GEMINI_MODEL=gemini-3.8-flash` in front). With the cache in `logs/eval_cache.json`, only changed or new cases cost API calls. The cache is not in git, so the first run on another computer calls the API for everything.

## Operations

*What you log. The quality signal and the drift check you monitor, the reference set, and the alert threshold with its justification. The drift demo: what you shifted, and the result with the alert firing (screenshot or numbers). The rate of false alarms on normal inputs.*

## Failures

18 of 40 cases failed with the default model.

1. **A: fire-safety problem missed with high confidence, 2 cases (c15, c19).** Both `fire_safety` cases were classified `not_an_issue`, with confidence 0.99 and 0.95 and severity 1, so no part of the review rule catches them and nobody sees them. These are the only two serious cases in the set.
   - c15: an extinguisher on the floor under its sign; A described exactly that and saw no problem.
   - c19: a small extinguisher in a wide entrance shot; A read it as well-kept equipment.
2. **A: wrong category, 8 other cases.**
   - Missed problem, closed as `not_an_issue`: c05 (bracket damage not seen), c06 (blocked sink read as a cloth soaking), c12 (leak not seen).
   - Wrong incident type: c07 (spilled glass read as a leak), c13 (fallen flower read as broken structure), c22 (wet-floor cone read as a leak), c23 (vending machine read as structural damage), c25 (missing tiles seen, the burst pipe behind them not).
3. **Review rule: not sent to a person, 5 cases.** c29 and c31 (nothing visible, closed as `not_an_issue` at 0.99 and 0.95), c30 (carpet thread, 0.85), c33 (items seen through a glass door, 0.85), c34 (rubbish bag with reflection, category right at 0.95). A's confidence is too high for a 0.7 threshold.
4. **A: out-of-scope photo taken as an incident, 3 cases.** c37 (a shoe and a remote control read as waste); c38 and c40 (A gave the expected category, so these two are a conflict between the label and the kind).

No case failed in the hand-off from A to B, and B's end-to-end tool use and replies passed the code checks in every case.

**Weakness of component B** (found while labelling, not by the judge): when A's category doesn't match its own description (c13, c30), B writes a mismatched title and a non-actionable "appropriate action" instruction. c01 also never says what to clean.

With `gemini-3.8-flash` 11 cases fail, all of them also failures of flash-lite: A wrong category c05, c06, c12, c19, c22, c25; not sent to a person c29, c31, c33, c34; out of scope c40. It catches c15 but not c19.

**Fix first:** stop `not_an_issue` answers from closing a report unseen, since 7 of A's 15 wrong categories are `not_an_issue`.

### Numbers for the Decision section (for Eduardo)

Default `gemini-3.5-flash-lite`, with `gemini-3.8-flash` in brackets.

- **Serious incidents missed (fire_safety or severity 4-5): 2 of 2 (1 of 2).** c15 and c19 were called `not_an_issue` at 0.95 or more, so the review rule doesn't catch them. Only two serious cases exist in the set, too few for a rate.
- **Accuracy against the baseline:** product 55.0% (72.5%), baseline 90.0%. Component A 62.5% (75.0%).
- **Sent to review:** 7.5%, about 3 a day at 40 reports a day (15.0%, about 6).
- **Review threshold.** Options below; they are measured on the same 40 cases, so confirm a chosen one on new photos. "Wrong" is A's wrong category, all kinds.

| Rule | Sent (per day) | Wrong caught | Review cases sent | Serious caught |
|---|---|---|---|---|
| Current, confidence < 0.7 | 7.5% (3) [15.0% (6)] | 0 of 15 [1 of 10] | 1 of 6 [2 of 6] | 0 of 2 [1 of 2] |
| confidence < 0.9 | 17.5% (7) [45.0% (18)] | 3 of 15 [5 of 10] | 3 of 6 [3 of 6] | 0 of 2 [1 of 2] |
| confidence < 0.95 | 22.5% (9) [50.0% (20)] | 4 of 15 [5 of 10] | 3 of 6 [3 of 6] | 0 of 2 [1 of 2] |
| confidence < 0.99 | 82.5% (33) [95.0% (38)] | 12 of 15 [10 of 10] | 5 of 6 [6 of 6] | 1 of 2 [2 of 2] |
| Current + every `not_an_issue` | 32.5% (13) [40.0% (16)] | 7 of 15 [7 of 10] | 3 of 6 [4 of 6] | 2 of 2 [2 of 2] |

- **Cost and latency:** €0.00088 per request, €1.06 a month, median 4.2 s, worst 5.1 s (€0.00382, €4.58, 15.0 s, 21.4 s).
- **Judge:** agreement 92% on 40 labels, kappa 0.00; it caught none of the 3 human fails, so don't use its pass rate as evidence.
- **Model we recommend keeping:** `gemini-3.8-flash` on these numbers, with the `not_an_issue` review rule. If the team switches, change the default in `pipeline.py` and rerun the drift reference with it. No option shown beats the baseline on correct answers.

## Decision

*Which cases go to a person: the rule, and how many cases a day that would be. Go / no-go / go with conditions: the conditions, and the evidence behind them.*

## Bonus: reinforcement learning

*Delete this section if you did not do it. The loop (feedback → reward → update → behaviour), the reward and what it could reward by accident, the exploration strategy and its cost, the evidence from real logs (and which part was simulated), the risks.*

## How to run it

Keys: `GEMINI_API_KEY` (required) and `GEMINI_MODEL` (optional). There is no download step and no local model: `uv sync`, then `uv run python app.py`. `main.py evaluate` makes about 9 Gemini calls per case and caches the answers in `logs/eval_cache.json`. [TODO: measure how long the first evaluation run takes and write it here.]

## AI use

*What you used and how, or "none".*

Claude (Anthropic) was used on 22 Nov 2026 to propose the provisional business case and to write the first version of `pipeline.py`, the app screen and the configuration. The team reviews and owns all of it.

On 25 Nov 2026 Claude searched Wikimedia Commons for candidate photos for cases c15 to c28, resized them, removed their metadata and helped word the `notes` and `baseline` texts. Máximo chose the 14 photos and decided the description, expected category and baseline of each one.

On 25 Nov 2026 Claude Code ran the evaluation, updated the default model, prices and judge in `pipeline.py` and `evaluate.py`, proposed the human labels that Gonzalo Angulo confirmed (see End to end), and drafted the Evaluation and Failures sections from the runs' numbers.
