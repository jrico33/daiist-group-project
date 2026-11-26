# Group Assignment Report

- **Team** (Blackboard group name):
- **Section**: [BBADBA 5A | BBADBA 5B | PPLEDBA 5A]
- **App URL** (on Render):
- **Final commit** (tag `final`):

*At most about 3,000 words, tables excluded. Members and who did what go in CONTRIBUTIONS.md.*

## Business case

**Users.** The operations team of a shopping centre (property or centre manager and technical-services coordinator). Tenants, security staff and visitors send photos of problems: leaks, broken glass, electrical faults, waste, graffiti, fire-safety issues.

**Decision.** For each incident photo: what is wrong, how urgent it is, which team must act, and by when. A work order is drafted automatically. Uncertain or serious cases go to a person before anything is sent.

**Baseline (today).** A person opens each report, looks at the photo, classifies it and forwards it by email to the right team. We estimate about 4 minutes per report: opening the message, looking at the photo, finding the team and its mailbox, and writing the email. On our 40 evaluation cases, the case authors judged that staff would decide correctly in 36 (90%) and wrongly in 4 (10%), mostly hidden causes such as a leak behind tiles or peeling paint. That 90% is the baseline the product has to beat. These figures are our estimates, not measurements from a real centre.

**Success metric.** (1) Share of reports with the correct category and team against a person's labels in `eval/cases.csv`, compared with the baseline; (2) share of serious incidents (severity 4-5) that are never missed or delayed; (3) minutes of staff time per report.

**Value in euros.** We assume a medium centre receives about 40 reports a day, about 14,600 a year, and that a person costs about 30 EUR an hour with social charges.

- *What we hoped before measuring:* the product handles 70% of reports alone, with 1 minute of review instead of 4 minutes of manual work. That saves about 2.1 minutes per report, about 510 hours or **15,000 EUR a year**.
- *What the evaluation supports:* the product alone is right in 55% of cases, against 90% for a person, so it cannot close reports alone (see Decision). Used as an assistant, it pre-fills every work order and a person confirms or corrects it. Confirming a right draft takes about 1 minute; a wrong one takes about the same 4 minutes as today. The average is 0.55 × 1 + 0.45 × 4 = 2.35 minutes, a saving of 1.65 minutes per report. That is about 400 hours, or **about 12,000 EUR a year per centre**.
- *Cost:* zero with a free-tier key. At paid-tier prices it is €0.00088 per report, about €13 a year (Cost and latency), so the cost does not change the case.

The 1 and 4 minutes are our estimates. A pilot should time them.

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

**One request.** The user uploads a photo in the App tab. The pipeline computes simple image features (brightness, contrast, size) for the drift check, then sends the photo to component A, which returns a category, a severity, a confidence and a description as structured JSON. Component B receives only that output, not the photo: it calls `lookup_sla` for the responsible team and the deadline, then `lookup_contact` for the team mailbox, and writes a short work order. The review rule sends the case to a person if the confidence is below 0.7, the severity is 4 or more, the category is fire safety, unclear or `not_an_issue`, or B made no tool calls (`not_an_issue` was added after the evaluation; see Decision). The input summary, features, both outputs, versions, latency, tokens, cost and the user's thumbs up or down are logged.

**Models and why.** Both components use Gemini through its REST API (the model name is in `pipeline.py` and can be changed with `GEMINI_MODEL`). The course allows a free Gemini key, one API offers vision and function calling, and nothing heavy has to run on Render's 512 MB free service. The tools are plain Python functions over the teams, response deadlines and mailboxes of a typical centre. They are our assumptions, not the policy of a real centre, which would replace them in a pilot.

**Reused from assignments 1-3.** None. All the code was written for this project, starting from the course template.

## Data

*Where each component's data comes from, with links, licences and sizes. Confirm that there is no personal data in your inputs or logs.*

No component was trained: both are Gemini models called through the API, so the only data are the photos below, used to evaluate the product and to monitor it. In total there are 80 photos: 40 evaluation cases, 30 reference photos and 10 shifted photos.

**Photos for cases c01 to c14** (`eval/inputs/c01.jpg.jpeg` to `c14.jpg.jpeg`, and `c10.jpg`; taken by Rubén). These are our own photos, taken with a phone and uploaded on 25 November 2026, so no third-party source or licence is involved. They show everyday problems in a home and a building: a rubbish bag on the floor, a running tap, loose wires from a wall box, black marks on a facade, a damaged towel rail, a blocked sink, a spilled glass, a power connector, a chipped mirror, boxes waiting to be removed, an opened wall with pipes, water outlets, a fallen flower and a damaged wall finish. Eleven are 1,537 × 2,048 pixels (2,048 × 1,537 for c12); c07, c08 and c10 were cropped to frame the problem. They are 54 to 288 KB each, about 2.4 MB in total, and carry no metadata or location. They are the 14 `normal` cases c01 to c14 of the 40 evaluation cases.

**Reference photos for the drift check** (`eval/inputs/r01.jpg` to `r30.jpg`, taken by Gonzalo Mir with a phone on 25 November 2026 in a university study area). Our own photos, with no third-party licence; they are described in the Operations section.

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

**Shifted set for the drift demo** (`eval/inputs/s01.jpg` to `s10.jpg`, listed in `eval/shifted.csv`). These come from Wikimedia Commons, chosen on 25 November 2026 under public domain, CC0 or CC BY licences (no ShareAlike or NonCommercial). They are shifted on purpose: they are not phone photos taken by staff, but web and camera photos taken in conditions the product was not built for (a dark tunnel, night scenes, black and white, a thermal camera image, an industrial plant, a beach). We only resized them to at most 1,024 pixels wide (28 to 253 KB each, about 1.7 MB in total) and removed all metadata; we did not edit their content. No person appears in them.

| File | Source (Wikimedia Commons) | Author | Licence |
|---|---|---|---|
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

**Personal data.** No person appears in c15 to c28, and they show no names, documents or readable number plates; one shows a house number on a shutter (c18) and some show brand names (a vending machine, a food wrapper). No person is in the foreground of c29 to c40. One photo (c29) shows a laptop screen whose wallpaper has two small, blurred figures, not identifiable; the team decided to keep it. Some photos show product brand names (an oven, a remote control, a racket, shoes) and no names, number plates or documents. The reference photos r01 to r30 show no people, faces, screens or names; their only text is safety signs (exits, fire equipment, toilets), and the phone's location was not stored in them. The shifted photos s01 to s10 show no people. No person appears in c01 to c14; their only text is product brand names (a yoghurt pot, paper towels). The logs keep only a summary of each photo and its numeric features, never the photo itself, so they hold no personal data either.

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

**Which to keep:** on these numbers `gemini-3.8-flash`, because it is right on 7 more cases (29 against 22) and loses none that flash-lite gets right, for €3.52 more a month and about 11 s more per request; neither beats the baseline. **The team kept `gemini-3.5-flash-lite`** as the product's model: neither model beats the baseline, so in both cases a person stays in the loop (see Decision), and there the gain from 3.8 is smaller than its cost in waiting time (15 s against 4 s per photo). Both models are free with a free-tier key. The drift check does not depend on the model, because it only watches the brightness and contrast of the photos.

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

**What we log.** Every request writes one record (`logbook.py`): a summary of the input (`photo <name>: <category>, severity <n>`, never the photo itself), the output of component A (category, severity, confidence, description) and of component B (the work order), the model and prompt versions, tokens, cost in euros, latency, whether the case went to review, the user's 👍/👎, and six numeric features of the photo: `brightness` and `contrast` (mean and standard deviation of the grey levels, 0 to 255), `megapixels`, `aspect_ratio`, and the model's `confidence` and `severity`. Online, the records go to Render's Postgres database.

**Quality signals.** The Monitoring tab plots, per hour, the share of requests sent to review, the share of 👎 among rated requests and the mean confidence of component A. A second alert fires when more than 40% of the last rated requests (at least 20) are 👎.

**Reference set.** 30 photos taken by Gonzalo Mir with a phone on the evening of 25 November 2026 in a university study area (corridors, toilets, study rooms, fire safety equipment, signs, sockets, furniture), with no people, faces, screens or names in them. They were resized to 1,536 × 2,048 pixels, the format of the phone photos in c01 to c14, and their metadata was removed (`eval/inputs/r01.jpg` to `r30.jpg`, listed in `eval/reference.csv`). `uv run python main.py reference` turned them into `monitoring/reference_features.csv`.

**What the drift check watches, and what it leaves out.** The alert compares the PSI of `brightness` and `contrast` in the last 100 requests against the reference set (`monitor.DRIFT_FEATURES`). These two describe the light and content of the photo, which is what changes the vision model's answers. We log the other four features but do not alert on them:

- `megapixels` and `aspect_ratio` describe the file format, not the scene. Our own `normal` cases range from 0.26 to 3.1 megapixels with no change in quality, so against a reference of same-size phone photos their PSI is 2.9 to 18 on normal inputs. Alerting on them would be a false alarm on almost every check.
- `confidence` and `severity` come from the model, and the reference photos show everyday scenes rather than incidents (mean severity 1.1, against 1.8 for the `normal` cases). Their PSI on normal inputs is 3.0 and 3.5, so they measure how many reports are real incidents, not whether the photos have changed. Confidence is still plotted as a quality signal.

**The alert rule and its threshold.** A feature alerts when its PSI over the last 100 requests is above `PSI_ALERT = 1.25` and above twice the PSI expected by chance for those sample sizes (`NOISE_MULTIPLE = 2`). The drift alert stays silent until there are 100 requests (`DRIFT_MIN_WINDOW`). We chose these values from a simulation with the features of the drift demo: 1,000 windows of 100 requests, drawn with replacement from the 18 `normal` cases, with a growing share of shifted photos.

| `PSI_ALERT` | False alarms (0% shifted) | 60% shifted | 70% shifted | 80% shifted | 100% shifted |
|---|---|---|---|---|---|
| 0.25 (template default) | 100% | 100% | 100% | 100% | 100% |
| 1.0 | 9.5% | 46% | 95% | 100% | 100% |
| **1.25 (chosen)** | **1.4%** | 12% | 55% | **99%** | 100% |
| 1.5 | 1.2% | 1% | 14% | 77% | 100% |

The textbook threshold of 0.25 fires on every window of normal traffic. Normal photos from other places already sit at a PSI of about 0.5 to 0.65 against a reference taken in one building, because the light and the walls are different. With 1.25, about 1 check in 70 is a false alarm, and the alert almost always fires once 80% of the recent photos are shifted. 1.5 would cut false alarms only slightly (1.2%) but miss a quarter of those shifts. With smaller windows the PSI is mostly noise: with 20 requests, normal traffic alone raised an alert in about 75% of the simulated windows, whatever the threshold. That is why the drift alert waits for 100 requests.

**What this alert can and cannot catch.** It is built for a large, sustained change in the photos: a new phone or app that changes the exposure, staff sending photos at night or from a dark plant room, or photos downloaded from the web instead of taken on site. It does not catch a small share of odd photos mixed into normal traffic. Those are better caught one by one, by the review rule and the 👎 signal.

**Drift demo.** `eval/shifted.csv` lists 10 photos that we shifted on purpose by changing their source and conditions: web and camera photos from Wikimedia Commons of a dark tunnel, night scenes, black and white shots, a thermal camera image and an industrial plant (sources in the Data section). Result of `uv run python main.py drift-demo`, with `gemini-3.5-flash-lite`:

| Inputs | n | PSI brightness | PSI contrast | Threshold | Alert |
|---|---|---|---|---|---|
| `normal` cases (c01 to c18) | 18 | 0.524 | 0.653 | 1.25 | quiet |
| shifted photos | 10 | 5.680 | 3.354 | 1.25 | **fires** |

**False alarms on normal inputs.** The drift demo's normal cases stay quiet. In the simulation above, about 1.4% of windows of 100 normal requests raise a false drift alarm.

**Limitations.** The reference set comes from a single building, photographed in a few minutes on one evening. The simulation resamples only 18 normal cases, so the rates above are rough. Once the app has a few weeks of real traffic, the reference should be rebuilt from logged requests that a person checked, and the threshold re-estimated the same way.

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

**Go with conditions: as an assistant to a person, not as an automatic system.**

**Why not go.** The product alone is right in 55.0% of the 40 cases, against 90.0% for a person today. It also missed both serious cases (c15 and c19, an extinguisher left on the floor): it called them `not_an_issue` with confidence 0.95 or more, so the original review rule let them through unseen. Switching to `gemini-3.8-flash` raises accuracy to 72.5% but still stays below the baseline and still misses c19. On these numbers no version of the product should close a report without a person.

**Why not no-go.** The chain itself works: no case failed in the hand-off from A to B, and B used its tools correctly in 95% of the cases where it was tested alone. The drift alert stays quiet on normal photos and fires on shifted ones. Even as an assistant it saves about 1.65 minutes per report, about 12,000 EUR a year per centre (Business case), at no API cost on the free tier.

**Which cases go to a person.** In the pilot, a person confirms every work order before it is sent. The review rule decides which ones are marked to be **checked first and carefully**: confidence below 0.7, severity 4 or more, fire safety, unclear, `not_an_issue`, or no tool calls. We added `not_an_issue` after the evaluation (`pipeline.ALWAYS_REVIEW`), because 7 of A's 15 wrong categories were `not_an_issue`, including both serious cases. On the 40 cases, with `gemini-3.5-flash-lite`:

| Rule | Marked for review | Per day (40 reports) | A's wrong categories caught | Serious cases caught |
|---|---|---|---|---|
| Before (evaluated) | 7.5% | 3 | 0 of 15 | 0 of 2 |
| **Now: before + every `not_an_issue`** | **32.5%** | **13** | **7 of 15** | **2 of 2** |

The other tables in Evaluation were measured with the rule before this change. The row "Now" comes from the review-rule variants that `evaluate.py` computes on the same run.

**Conditions to let the product send reports alone** (the unmarked ones), all measured on new photos and not on these 40:

1. At least 100 new real photos from the centre, including at least 10 serious cases. Today only 2 serious cases exist, too few to estimate a rate.
2. On unmarked cases, the product is right at least as often as a person (90%), and no serious case is left unmarked.
3. A judge that disagrees with people when they fail (kappa clearly above 0). Today kappa is 0.00, so the judge's pass rate is not evidence of quality.
4. The real teams, deadlines and mailboxes of the centre in `lookup_sla` and `lookup_contact`, and the 1 and 4 minutes of the business case timed in the pilot.
5. The drift alert and the share of 👎 watched every week. If either alert fires, every report goes back to a person.

## How to run it

Keys: `GEMINI_API_KEY` (required) and `GEMINI_MODEL` (optional). There is no download step and no local model: `uv sync`, then `uv run python app.py`. `main.py evaluate` makes about 9 Gemini calls per case and caches the answers in `logs/eval_cache.json`. We did not time the first run exactly. With about 4 s per request plus a second run of B and two judge calls per case, expect roughly 10 minutes for the 40 cases (longer if the free tier's rate limit slows it down); later runs read the cache and take seconds. `uv run python main.py drift-demo` runs the 18 normal cases and the 10 shifted photos, about 2 minutes. `uv run python check.py` checks everything, as the professor will.

Free tier: both models used here (`gemini-3.5-flash-lite` and `gemini-3.8-flash`) are free of charge with a free AI Studio key, with no billing account. The euro costs in this report are what the same calls would cost at paid-tier prices.

## AI use

*What you used and how, or "none".*

Claude (Anthropic) was used on 22 Nov 2026 to propose the provisional business case and to write the first version of `pipeline.py`, the app screen and the configuration. The team reviews and owns all of it.

On 25 Nov 2026 Claude searched Wikimedia Commons for candidate photos for cases c15 to c28, resized them, removed their metadata and helped word the `notes` and `baseline` texts. Máximo chose the 14 photos and decided the description, expected category and baseline of each one.

On 25 Nov 2026 Claude Code ran the evaluation, updated the default model, prices and judge in `pipeline.py` and `evaluate.py`, proposed the human labels that Gonzalo Angulo confirmed (see End to end), and drafted the Evaluation and Failures sections from the runs' numbers.

On 26 Nov 2026 Claude Code merged the workstream branches, checked the photos c01 to c14 for people, reproduced the drift demo offline, checked the free-tier prices, added `not_an_issue` to the review rule and drafted the Business case, Decision and How to run sections. Eduardo chose the model and the review rule and reviewed the text.
