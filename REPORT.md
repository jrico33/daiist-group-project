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

*Each component on its own: the metric, the result, the test data and its size.*

### End to end

*How you wrote `eval/cases.csv` (counts by kind, two examples). Results against the baseline. Where the output is free text: the judge's rubric and your agreement with it on your own labels.*

### Cost and latency

*Per request: tokens, euros and seconds, for each component and in total. What it would cost per month at the volume in your business case.*

## Operations

*What you log. The quality signal and the drift check you monitor, the reference set, and the alert threshold with its justification. The drift demo: what you shifted, and the result with the alert firing (screenshot or numbers). The rate of false alarms on normal inputs.*

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
