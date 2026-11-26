# Group Assignment Report

- **Team** (Blackboard group name): Group 6
- **Section**: BBADBA 5B
- **App URL** (on Render): https://retail-incident-triage.onrender.com
- **Final commit** (tag `final`): the commit tagged `final` on `main`, https://github.com/jrico33/daiist-group-project/tree/final

## Business case

**Users.** The operations team of a shopping centre (centre manager and technical-services coordinator). Tenants, security staff and visitors send photos of problems: leaks, broken glass, electrical faults, waste, graffiti, fire-safety issues.

**Decision.** For each photo: what is wrong, how urgent it is, which team must act and by when. The product drafts the work order; uncertain or serious cases go to a person first.

**Baseline (today).** A person opens each report, classifies the photo and emails the right team, which we estimate at about 4 minutes. On our 40 evaluation cases, the case authors judged that staff would decide correctly in 36 (90%); the 4 errors are hidden causes such as a leak behind tiles. That 90% is the baseline to beat. These are our estimates, not measurements from a real centre.

**Success metric.** (1) Share of reports with the correct category, against the baseline; (2) serious incidents (fire safety or severity 4-5) never missed; (3) minutes of staff time per report.

**Value in euros.** We assume 40 reports a day (14,600 a year) and 30 EUR an hour for a person.

- *Hoped for before measuring:* the product handles 70% of reports alone, with 1 minute of review instead of 4, saving about **15,000 EUR a year**.
- *What the evaluation supports:* the product alone is right in 55% of cases, so it cannot close reports alone (see Decision). As an assistant, it pre-fills every work order and a person confirms it: about 1 minute when the draft is right, the same 4 minutes when it is wrong. That is 0.55 × 1 + 0.45 × 4 = 2.35 minutes, saving 1.65 minutes per report, about 400 hours or **12,000 EUR a year per centre**.
- *Cost:* zero with a free-tier key; €0.00088 per report at paid prices, about €13 a year.

The 1 and 4 minutes are estimates that a pilot should time.

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

**One request.** The pipeline computes image features (brightness, contrast, size) for the drift check, then component A returns a category, severity, confidence and description as structured JSON. Component B receives only that output, not the photo: it calls `lookup_sla` for the team and deadline, then `lookup_contact` for the mailbox, and writes a short work order. The review rule sends the case to a person if confidence is below 0.7, severity is 4 or more, the category is fire safety, unclear or `not_an_issue`, or B made no tool calls (`not_an_issue` was added after the evaluation; see Decision). Everything is logged (see Operations).

**Models and why.** Both components use `gemini-3.5-flash-lite` through the REST API (`GEMINI_MODEL` changes it). A free key covers both vision and function calling, and nothing heavy runs on Render's 512 MB free service. The tools are Python functions over teams, deadlines and mailboxes we assumed for a typical centre; a pilot would replace them with the centre's real policy.

**Reused from assignments 1-3.** None. All the code was written for this project from the course template.

## Data

Nothing was trained, so the only data are 80 photos: 40 evaluation cases, 30 reference photos and 10 shifted photos. All were resized and stripped of metadata and location.

- **c01 to c14** (`normal`, taken by Rubén): our own phone photos of everyday problems at home and in a building (rubbish bag, running tap, loose wires, marks on a facade, chipped mirror, opened wall with pipes…). 54 to 288 KB each, 2.4 MB in total.
- **c15 to c28** (chosen by Máximo): Wikimedia Commons photos under public domain, CC0 or CC BY, chosen to look like phone photos of a shopping centre. c15 to c18 are `normal` (one clear problem each); c19 to c28 are `hard`: the problem is small, the light is poor, it is already handled (a wet-floor cone), no category fits (a broken vending machine) or two fit (a hanging bulb in front of graffiti). 56 to 276 KB each, 2.2 MB in total. Sources below.
- **c29 to c40** (taken by Juan Jacobo at home on 22 Nov 2026): c29 to c34 are `review` cases a person should see (motion blur, a black frame, a white wall, a reflection); c35 to c40 are `out_of_scope` objects (a bottle, an oven, a padel racket, a sweet). 72 to 340 KB each, 2.6 MB in total.
- **r01 to r30** (reference set, taken by Gonzalo Mir): see Operations.
- **s01 to s10** (shifted set): Wikimedia Commons photos under public domain, CC0 or CC BY, taken in conditions the product was not built for (a dark tunnel, night scenes, black and white, a thermal image, an industrial plant). 28 to 253 KB each, 1.7 MB in total. Sources below.

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
| s01 | [75014 Petite Ceinture Tunnel de Montsouris vers la tranchée d'Arcueil](https://commons.wikimedia.org/wiki/File:75014_Petite_Ceinture_Tunnel_de_Montsouris_vers_la_tranch%C3%A9e_d%27Arcueil.jpg) | Jérôme Bon | CC BY 2.0 |
| s02 | [Broken Glass (18434524128)](https://commons.wikimedia.org/wiki/File:Broken_Glass_(18434524128).jpg) | Rodrigo Paredes | CC BY 2.0 |
| s03 | [Elektroschuetz](https://commons.wikimedia.org/wiki/File:Elektroschuetz.jpg) | Sönke Krüll | CC BY 3.0 |
| s04 | [20201021 Sinter plant Völklingen Ironworks 07](https://commons.wikimedia.org/wiki/File:20201021_Sinter_plant_V%C3%B6lklingen_Ironworks_07.jpg) | Flocci Nivis | CC BY 4.0 |
| s05 | [After the Rain - Flickr - judithjackson957](https://commons.wikimedia.org/wiki/File:After_the_Rain_-_Flickr_-_judithjackson957.jpg) | Judith Jackson | CC BY 2.0 |
| s06 | [Cracks (1489533799)](https://commons.wikimedia.org/wiki/File:Cracks_(1489533799).jpg) | Raphael Schön | CC BY 2.0 |
| s07 | [Destroyed Lamp](https://commons.wikimedia.org/wiki/File:Destroyed_Lamp.jpg) | Jaroslav A. Polák | CC BY 4.0 |
| s08 | [Blue elixir (3156956367)](https://commons.wikimedia.org/wiki/File:Blue_elixir_(3156956367).jpg) | torbakhopper | CC BY 2.0 |
| s09 | [Estintore Dick fine '800](https://commons.wikimedia.org/wiki/File:Estintore_Dick_fine_%27800.jpg) | Museo storico pompieri | CC0 |
| s10 | [California - Arcata Beach early morning, Arcata (NARA 542978)](https://commons.wikimedia.org/wiki/File:CALIFORNIA-ARCATA_BEACH_EARLY_MORNING,_ARCATA_-_NARA_-_542978.jpg) | Tomas Sennett | Public domain |

**Personal data.** No identifiable person appears in any photo. The only exception we found is c29, a laptop wallpaper with two small, blurred figures; the team decided to keep it. The photos show no names, documents or readable number plates: only brand names on products, a house number on a shutter (c18) and safety signs in the reference set. The logs keep a summary and numeric features of each photo, never the photo itself.

## Evaluation

### Components

The 40 cases of `eval/cases.csv` (18 normal, 10 hard, 6 review, 6 out of scope) are both the component and end-to-end test set; nothing was tuned on them. Numbers come from `eval/eval_run_flash_lite.txt` and `eval/eval_run_flash.txt`.

**Component A (vision).** Accuracy 62.5%, macro-F1 0.581. Only 2 cases have an expected severity, so severity is effectively untested, although the review rule and deadlines depend on it.

**Component B (agent) alone**, fed the correct category and A's description: tools used correctly 95.0%, reply consistent with the tools 95.0%, judge pass 92.5%. The failures (c12, c29, c31) are cases where A's description ("no visible damage") contradicts the correct category, and B followed the description.

### End to end

Normal and hard cases count as correct if the category matches; review cases if a person sees them; out-of-scope cases if A answers `not_an_issue` or `other_or_unclear`, or a person sees them. For example, c16 (a stained ceiling tile) should be `water_leak` and c26 (a hanging bulb in front of graffiti) `electrical`.

| Kind | Cases | Product correct | Sent to review |
|---|---|---|---|
| normal | 18 | 66.7% | 11.1% |
| hard | 10 | 60.0% | 0.0% |
| review | 6 | 16.7% | 16.7% |
| out_of_scope | 6 | 50.0% | 0.0% |
| **All** | **40** | **55.0%** | **7.5%** |

**The product is below the baseline: 55.0% against 90.0%.** The baseline comes from what the case authors wrote, not from measured staff, so it may flatter people. The original review rule sent 7.5% of cases to a person (about 3 a day); the 0.7 confidence threshold never fired, because A's lowest confidence was 0.85.

**Judge.** Rubric: the work order matches A's result, takes team, mailbox and deadline from the tools, invents nothing, and is short and clear. Gonzalo Angulo labelled all 40 work orders (pass = consistent and actionable); Claude proposed each label with a reason, without seeing the judge's verdicts. The judge passed 100% and the labels 37 of 40, so **agreement is 92% but Cohen's kappa is 0.00**: it caught none of the 3 human fails (c01, c13, c30), and its pass rate is not evidence of quality. The judge is `gemini-3.8-flash`, so in the 3.8 run it grades its own output without a human check.

**Model comparison** (same cases, prompts, rule and judge):

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

`gemini-3.8-flash` is right on 7 more cases and loses none, but neither model beats the baseline, so a person stays in the loop either way (see Decision). There the gain is worth less than the wait, 15 s against 4 s per photo, so **we kept `gemini-3.5-flash-lite`**. Both models are free with a free-tier key.

### Cost and latency

| Per request (flash-lite, 40 cases) | Tokens (mean) | Cost (mean) | Median | Worst case |
|---|---|---|---|---|
| A (vision) | 1,272 | €0.00046 | | |
| B (agent) | 848 | €0.00042 | | |
| Total | 2,120 | €0.00088 | €0.00098, 2,306 tokens, 4.2 s | €0.00104, 2,359 tokens, 5.1 s |

At 40 reports a day this is **€1.06 a month** (€4.58 with 3.8-flash). Prices are Google's paid-tier prices of 25 Nov 2026 at that day's ECB rate (1 EUR = 1.0935 USD; see `pipeline.py`); with a free key the real cost is zero. Latency is for the whole chain, from one laptop. The judge's calls (€0.12 per run) are not part of the product's cost.

## Operations

**What we log.** One record per request (`logbook.py`): a summary of the input (never the photo), A's and B's outputs, model and prompt versions, tokens, cost, latency, review flag, the user's 👍/👎, and six features: `brightness` and `contrast` (mean and spread of grey levels), `megapixels`, `aspect_ratio`, and A's `confidence` and `severity`. Online, records go to Render's Postgres database.

**Quality signals.** The Monitoring tab plots, per hour, the share sent to review, the share of 👎 and A's mean confidence. An alert fires when more than 40% of the last rated requests (at least 20) are 👎.

**Reference set.** 30 phone photos taken by Gonzalo Mir on 25 Nov 2026 in a university study area (corridors, toilets, fire equipment, signs, sockets), with no people, resized to the format of c01 to c14. `main.py reference` turned them into `monitoring/reference_features.csv`.

**Drift check.** The alert compares the PSI of `brightness` and `contrast` over the last 100 requests against the reference. They describe the light and content of the photo, which is what changes A's answers. The other features are logged but not alerted on: `megapixels` and `aspect_ratio` describe the file, not the scene (PSI 2.9 to 18 on our own normal cases), and `confidence` and `severity` measure how many reports are real incidents (PSI 3.0 and 3.5 on normal cases).

**Threshold.** A feature alerts when its PSI is above `PSI_ALERT = 1.25` and above twice the PSI expected by chance, and only once there are 100 requests. We chose it by simulating 1,000 windows of 100 requests drawn from the 18 normal cases, with a growing share of shifted photos:

| `PSI_ALERT` | False alarms (0% shifted) | 60% shifted | 70% shifted | 80% shifted | 100% shifted |
|---|---|---|---|---|---|
| 0.25 (template default) | 100% | 100% | 100% | 100% | 100% |
| 1.0 | 9.5% | 46% | 95% | 100% | 100% |
| **1.25 (chosen)** | **1.4%** | 12% | 55% | **99%** | 100% |
| 1.5 | 1.2% | 1% | 14% | 77% | 100% |

The textbook 0.25 fires on all normal traffic, because normal photos from other places already sit at a PSI of about 0.5 to 0.65 against a reference from one building. With 1.25, about 1 check in 70 is a false alarm and the alert almost always fires once 80% of the photos are shifted; 1.5 barely lowers false alarms but misses a quarter of those shifts. With windows of 20 requests, normal traffic alone raised an alert in about 75% of windows, so the alert waits for 100. It catches a large, sustained change (a new phone, photos at night, photos from the web), not a few odd photos; those are left to the review rule and the 👎 signal.

**Drift demo** (`main.py drift-demo`, 10 photos shifted by source and conditions, see Data):

| Inputs | n | PSI brightness | PSI contrast | Threshold | Alert |
|---|---|---|---|---|---|
| `normal` cases (c01 to c18) | 18 | 0.524 | 0.653 | 1.25 | quiet |
| shifted photos | 10 | 5.680 | 3.354 | 1.25 | **fires** |

The false-alarm rate on normal inputs is about 1.4% of windows in the simulation. **Limitations:** the reference comes from one building on one evening, and the simulation resamples only 18 cases. With real traffic, the reference should be rebuilt from checked requests and the threshold re-estimated.

## Failures

18 of 40 cases failed with the default model. No case failed in the hand-off from A to B.

1. **Fire-safety problem missed with high confidence, 2 cases (c15, c19).** Both extinguishers left on the floor were called `not_an_issue` at 0.99 and 0.95, so the original rule let them through unseen. They are the only serious cases in the set.
2. **Wrong category, 8 cases.** Problem missed as `not_an_issue`: c05, c06, c12. Wrong type: c07 (spilled glass read as a leak), c13, c22 (wet-floor cone read as a leak), c23, c25 (missing tiles seen, burst pipe not).
3. **Not sent to a person, 5 review cases** (c29 to c31, c33, c34): A was confident (0.85 to 0.99) about photos that are hard to read.
4. **Out-of-scope photo taken as an incident, 3 cases** (c37, c38, c40). In c38 and c40, A gave the expected category, so the label and the kind conflict.

**Weakness of B** (found while labelling): when A's category contradicts its own description (c13, c30), B writes a mismatched, non-actionable order; c01 never says what to clean.

With `gemini-3.8-flash`, 11 cases fail, all of them also failures of flash-lite; it catches c15 but not c19.

**Fix first:** stop `not_an_issue` answers from closing a report unseen. 7 of A's 15 wrong categories are `not_an_issue`, both serious cases included. We applied this fix (see Decision).

## Decision

**Go with conditions: as an assistant to a person, not as an automatic system.**

**Why not go.** The product alone is right in 55.0% of cases against 90.0% for a person, and it missed both serious cases. 3.8-flash reaches 72.5% and still misses c19. No version should close a report without a person.

**Why not no-go.** The chain works: no hand-off failures, B uses its tools correctly in 95% of cases, and the drift alert fires only on shifted photos. As an assistant it saves about 12,000 EUR a year per centre (Business case), at no API cost on the free tier.

**Which cases go to a person.** In the pilot, a person confirms every work order. The review rule marks which ones to **check first and carefully**. After the evaluation we added `not_an_issue` to it (`pipeline.ALWAYS_REVIEW`). The variants below were computed by `evaluate.py` on the same 40 cases (flash-lite, with 3.8-flash in brackets); the other tables in Evaluation use the rule before this change.

| Rule | Sent (per day) | A's wrong categories caught | Review cases sent | Serious caught |
|---|---|---|---|---|
| Before, confidence < 0.7 | 7.5% (3) [15.0% (6)] | 0 of 15 [1 of 10] | 1 of 6 [2 of 6] | 0 of 2 [1 of 2] |
| confidence < 0.9 | 17.5% (7) [45.0% (18)] | 3 of 15 [5 of 10] | 3 of 6 [3 of 6] | 0 of 2 [1 of 2] |
| confidence < 0.95 | 22.5% (9) [50.0% (20)] | 4 of 15 [5 of 10] | 3 of 6 [3 of 6] | 0 of 2 [1 of 2] |
| confidence < 0.99 | 82.5% (33) [95.0% (38)] | 12 of 15 [10 of 10] | 5 of 6 [6 of 6] | 1 of 2 [2 of 2] |
| **Now: before + every `not_an_issue`** | **32.5% (13)** [40.0% (16)] | **7 of 15** [7 of 10] | **3 of 6** [4 of 6] | **2 of 2** [2 of 2] |

The chosen rule marks about 13 reports a day and is the only cheap option that catches both serious cases. Raising the confidence threshold does not help, because A is confidently wrong.

**Conditions to let the product send unmarked reports alone**, measured on new photos, not these 40:

1. At least 100 real photos from the centre, with at least 10 serious cases (we have 2).
2. On unmarked cases, the product is right at least 90% of the time, and no serious case is unmarked.
3. A judge with kappa clearly above 0 against human labels.
4. The centre's real teams, deadlines and mailboxes in the tools, and the 1 and 4 minutes of the business case timed.
5. The drift and 👎 alerts watched weekly; if either fires, every report goes back to a person.

## How to run it

Set `GEMINI_API_KEY` (required; `GEMINI_MODEL` optional) in `.env`, then `uv sync` and `uv run python app.py`. There is no download step and no local model.

- `uv run python main.py evaluate`: about 9 calls per case, cached in `logs/eval_cache.json` (not in git). We estimate about 10 minutes for the first run; later runs take seconds.
- `uv run python main.py drift-demo`: 28 photos, about 110 calls.
- `uv run python check.py --url https://retail-incident-triage.onrender.com`: on 26 Nov 2026 it passed all six steps in about 7 minutes with a free key.

**Free tier.** Both models are free with a free AI Studio key and no billing account; the euro costs above are paid-tier prices. A free key allows 15 requests per minute and a photo takes up to 4 calls, so on a 429 `pipeline._gemini` waits as long as Google asks (`retryDelay`) and retries. Run `check.py` with the quota rested: right after another long run, the drift demo can exceed its 15-minute limit.

## AI use

We used Claude (Anthropic) and Claude Code throughout; the team reviewed and owns all of it.

- 22 Nov: proposed the business case; first version of `pipeline.py`, the app and the configuration.
- 25 Nov: found candidate Wikimedia photos for c15 to c28 and resized them (Máximo chose them and decided each label); ran the evaluation, updated model, prices and judge, and proposed the human labels that Gonzalo Angulo confirmed; drafted Evaluation and Failures.
- 26 Nov: merged the branches, checked c01 to c14 for people, added `not_an_issue` to the review rule, handled the free-tier rate limit, ran `check.py`, and drafted the Business case and Decision and shortened this report. Eduardo chose the model and the rule and reviewed the text.
