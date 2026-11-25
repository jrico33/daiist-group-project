# Team to-do

Provisional case: **retail incident triage** (a photo goes to a vision step, then an agent drafts the work order). Confirm it with the group first. If the group changes it, `pipeline.py`, the prompts in it and `REPORT.md` change; the rest of this list stays.

## Who does what (6 members; write the names in the Who column)

Photos are the bottleneck, so start with them. There is no GPU work and no model training anywhere in this project: a laptop is enough. What costs compute is Gemini API calls, which have free-tier limits per key, and the clock time of the runs. Each member should use their own key. The workstreams that make many calls are marked.

The brief expects more from larger teams, so with 6 members aim for 40 cases instead of 30 and compare two Gemini models or two prompt versions in the evaluation (workstream 6).

| # | Workstream | Who | Compute |
|---|---|---|---|
| 1 | **Lead and delivery**: confirm the use case, add collaborators, assemble `REPORT.md`, deploy on Render, run `check.py`, tag `final`, presentation. Optional: the bandit bonus. | | Light. Render free plan (512 MB). `check.py` repeats the drift demo, about 120 API calls. |
| 2 | **Cases, part 1**: photos and rows c01 to c14 of `eval/cases.csv` (all `normal`), with `expected` and `baseline`. | Rubén Segura | Light. Manual work, a few hours. |
| 3 | **Cases, part 2**: rows c15 to c28 (c15 to c18 `normal`, c19 to c28 `hard`), with `expected` and `baseline`. | Máximo | Light. Manual work, a few hours. |
| 4 | **Cases, part 3**: rows c29 to c40 (`review` and `out_of_scope`), the `baseline` notes, and the Data section of `REPORT.md` (sources, licences). | Juan Jacobo | Light. About 12 photos, 30 to 45 minutes, no API key needed. |
| 5 | **Reference and drift**: 30 photos for `eval/reference.csv`, 10 shifted photos for `eval/shifted.csv`, then `main.py reference` and `main.py drift-demo`, and the Operations section (alert threshold and its justification). | | Medium. About 120 API calls for the reference set and about 120 per drift demo run. |
| 6 | **Evaluation**: run `main.py evaluate`, label 20 or more cases in `eval/human_labels.csv`, write the Evaluation, Cost and latency, and Failures sections. Compare two models or prompt versions. | | Heaviest. About 9 API calls per case, so about 360 for 40 cases, and double that for the comparison. Answers are cached in `logs/eval_cache.json`, so only the first run of each version is expensive. Use your own key and expect several minutes. |

Order: (1) photos, members 2 to 5 in parallel; (2) the runs, member 5 then member 6, once the CSVs are merged; (3) the write-up by everyone, with the Decision section written by members 1 and 6 together.

The call counts are estimates from the code: one product request is about 4 calls (1 vision, up to 3 agent turns), and an evaluated case adds a second agent run and two judge calls.

## Joining later (claiming a workstream)

Every row above without a name is open. To take one, write your name in the Who column of that row (a one-line edit of this file) and follow the checklists below. You need to be a collaborator on the repository (the owner adds you under Settings, Collaborators), or work from a fork and send a pull request. The rows of `eval/cases.csv` are numbered in advance with their kind already set, so two people never edit the same line and merges stay clean. Name each photo after its row, for example `c29.jpg`, and put it in `eval/inputs/`.

## Workstream 4, step by step (Juan Jacobo)

About 12 photos, 30 to 45 minutes, no API key and no code.

1. **Take 12 photos with your phone.** No people or faces, nothing with names or personal information.
   - c29 to c34 (`review`, 6 photos): cases the product should not decide alone. Take photos that are hard to read: very blurry, very dark, an extreme close-up of an unclear texture, an object half out of the frame, two different things in one shot, a reflection. In the `expected` column write `other_or_unclear`.
   - c35 to c40 (`out_of_scope`, 6 photos): not an incident at all, for example a pet, a plate of food, a plant, a street view, a keyboard, a blank wall. In the `expected` column write `not_an_issue`.
2. **Make them small and anonymous.** About 1024 pixels wide, under 300 KB each, with location switched off in the photo's metadata (on iPhone: Share, Options, turn off Location). Name them `c29.jpg` to `c40.jpg`.
3. **Upload them.** On GitHub open the folder `eval/inputs`, choose Add file, Upload files, drag the 12 photos in and commit.
4. **Fill in rows c29 to c40 of `eval/cases.csv`:** `input` is `eval/inputs/c29.jpg` and so on, `expected` as above, and `baseline` is `correct: a person looks at every report today` for `review` rows and `correct: a person reads it and discards it, about a minute` for `out_of_scope` rows. Tell Claude when the photos are up and it can check them for people and fill the rows with you.
5. **Data section of `REPORT.md`:** say that these are your own photos, taken on the day you took them, with no people. Claude can draft it.

## Everyone

- [ ] Get a free Gemini key (https://aistudio.google.com/apikey), run `cp .env.example .env` and paste it. Then `uv sync` and `uv run python app.py`.
- [ ] Add your first name and GitHub username to `CONTRIBUTIONS.md`, and log what you do there as you go.
- [ ] Work on a branch and open a pull request. Render redeploys on every push to `main`, so do not push to `main` just before the presentation.

## Photos and test files (the biggest piece of work)

Photos go under `eval/inputs/`. Keep each one small (under about 300 KB: the repo is public). No people or faces, no readable names, no number plates. Take them yourselves, or use Wikimedia Commons (CC0 or CC-BY) and write each source and licence in `REPORT.md`, section Data.

- [ ] `eval/cases.csv`: 40 rows, already numbered c01 to c40 with the `kind` set (c01 to c18 `normal`, c19 to c28 `hard`, c29 to c34 `review`, c35 to c40 `out_of_scope`). Fill only your own rows. Cover every category across the `normal` and `hard` rows.
  - `input`: the photo path, for example `eval/inputs/c01.jpg`.
  - `expected`: the correct category, optionally with the severity, for example `water_leak|4`. Categories are in `pipeline.py`: water_leak, electrical, broken_glass_or_structure, cleanliness_or_waste, signage_or_graffiti, fire_safety, other_or_unclear, not_an_issue. Use `not_an_issue` for `out_of_scope` photos (a cat, a landscape, a blank wall).
  - `baseline`: what a person does today with that case, starting with `correct` or `wrong`, then a note.
- [ ] `eval/reference.csv`: 30 or more different normal photos, one column `input`. Not the ones in `cases.csv`.
- [ ] `eval/shifted.csv`: 10 or more photos changed on purpose (night, very dark, blurry, a different kind of place), so the drift alert fires.
- [ ] `eval/human_labels.csv`: after the first `main.py evaluate`, read B's work orders and label 20 or more of them yourselves: `id,label,comment`, label `pass` or `fail`. The judge's agreement with you is computed from this.
- [ ] `uv run python main.py reference`, then commit `monitoring/reference_features.csv`.

## Code and numbers

- [ ] Replace the illustrative data in `pipeline.py` (teams, response hours, prices, the model name) with your own assumptions. Check that the Gemini model name still exists.
- [ ] `uv run python main.py evaluate`. Copy the numbers into `REPORT.md` (Evaluation, Cost and latency, Failures).
- [ ] Justify the review rule (thresholds in `pipeline.py`) and the alert threshold (`monitor.py`) with those numbers. `uv run python main.py drift-demo` must pass: quiet on normal inputs, alert on shifted ones.
- [ ] Replace every [A] assumption in the business case of `REPORT.md` with a real figure, and write the Decision section (go, no-go or go with conditions).
- [ ] Deploy on Render (`SETUP.md`, "Put it online"), put the App URL in `REPORT.md` and run `uv run python check.py --url <your-url>`.
- [ ] Optional, up to +10%: a bandit that learns from the app's 👍/👎, for example choosing among three prompt variants for component B.
- [ ] Run `uv run python check.py` in a fresh clone, then tag `final`.
