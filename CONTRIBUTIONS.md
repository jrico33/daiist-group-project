# Contributions

*Fill this in as you go, not on the last day. It is checked against the commits and against the peer assessment. A first name and a GitHub username are enough: this repo is public.*

## Members

| First name | GitHub username | Main areas |
|---|---|---|
| Juan Jacobo | jrico33 | Repo owner; project setup, business case, pipeline |
| Rubén | rubensegu | Evaluation photos and case labels (c01–c14) |
| Máximo | mgarridoIE | Evaluation photos and case labels (c15–c28) |
| Gonzalo Angulo | gonzaloanguloo | Evaluation (workstream 6): runs, model comparison, human labels, Evaluation/Cost/Failures sections |
| Gonzalo Mir | gonzalomirr | Reference and drift (workstream 5): reference and shifted photos, drift threshold, Operations section |
| | | |

## Log

*One line per piece of work: the date, who did it (more than one name is fine), and what. Code done in pair programming counts for both, even if only one of you committed it.*

| Date | Who | What |
|---|---|---|
| 2026-11-22 | Juan Jacobo | Forked the template; chose a provisional business case; first version of pipeline.py (vision + agent), app screen and config |
| 2026-11-22 | Juan Jacobo | Took and prepared 12 photos (c29-c40), filled rows c29-c40 of eval/cases.csv and wrote the Data section of REPORT.md |
| 2026-11-25 | Rubén | Took and prepared 14 evaluation photos (c01–c14) and added the expected categories and manual baseline decisions to `eval/cases.csv`. |
| 2026-11-25 | Máximo | Uploaded 14 photos (4 normal, 10 hard), making sure no people or private information appeared, wrote the description of each photo and decided its expected category and baseline in eval/cases.csv, and listed their sources and licences in the Data section of REPORT.md |
| 2026-11-25 | Gonzalo Angulo | Moved the default model to gemini-3.5-flash-lite (2.5 models closed to new keys), added per-model EUR prices in pipeline.py, fixed the judge to one model and added serious-case and review-rule numbers to evaluate.py |
| 2026-11-25 | Gonzalo Angulo | Ran the evaluation on the 40 cases with gemini-3.5-flash-lite and gemini-3.8-flash (model comparison) |
| 2026-11-25 | Gonzalo Angulo | Labelled the 40 work orders in eval/human_labels.csv (labels proposed by Claude, confirmed in batches) and computed the judge's agreement |
| 2026-11-25 | Gonzalo Angulo | Wrote the Evaluation, Cost and latency, and Failures sections of REPORT.md, with the numbers for the Decision section |
| 2026-11-25 | Gonzalo Mir | Took 30 reference photos (r01-r30) and chose 10 shifted photos from Wikimedia Commons (s01-s10), ran `main.py reference` and `main.py drift-demo`, set the drift features and alert threshold in monitor.py from a simulation, and wrote the Operations section and the shifted set's sources in REPORT.md |
