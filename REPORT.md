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

**Personal data.** No person appears in c15 to c28, and they show no names, documents or readable number plates; one shows a house number on a shutter (c18) and some show brand names (a vending machine, a food wrapper). No person is in the foreground of c29 to c40. One photo (c29) shows a laptop screen whose wallpaper has two small, blurred figures, not identifiable; the team decided to keep it. Some photos show product brand names (an oven, a remote control, a racket, shoes) and no names, number plates or documents. The reference photos r01 to r30 show no people, faces, screens or names; their only text is safety signs (exits, fire equipment, toilets), and the phone's location was not stored in them. The shifted photos s01 to s10 show no people. The other members' photos are described by their authors [TODO].

## Evaluation

### Components

*Each component on its own: the metric, the result, the test data and its size.*

### End to end

*How you wrote `eval/cases.csv` (counts by kind, two examples). Results against the baseline. Where the output is free text: the judge's rubric and your agreement with it on your own labels.*

### Cost and latency

*Per request: tokens, euros and seconds, for each component and in total. What it would cost per month at the volume in your business case.*

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

*Failed end-to-end cases grouped by cause (which component, or the hand-off between them), with counts, and what you would fix first.*

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
