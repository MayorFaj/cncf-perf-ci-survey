# How do CNCF projects test performance in CI?

A pre-registered study of how the 77 CNCF graduated and incubating projects run performance, benchmark and scale tests in continuous integration, and what they do with the results.

**Status:** protocol pre-registered on 22 October 2026 (see [`PROTOCOL.md`](PROTOCOL.md)); step 2 (coding) complete on 23 October 2026; run history (step 3) and the reliability re-coding are next.

**Author:** Mayowa Fajobi (ORCID [0009-0009-5848-5825](https://orcid.org/0009-0009-5848-5825))

## Why

In a companion study of kgateway's nightly scale tests ([dataset](https://doi.org/10.5281/zenodo.23568203)), a pass/fail gate missed a 7x performance change because the numbers were printed to CI logs and never kept or compared. This study asks whether that is typical across cloud-native projects.

## Contents

| Path | What it is |
| --- | --- |
| `PROTOCOL.md` | Research questions, population, data collection, coding scheme, reliability check, analysis, threats, pilot and deviations |
| `data/cncf_projects_2026-10-20.csv` | The population: 77 projects from the CNCF landscape snapshot |
| `scripts/fetch_ci_configs.py` | Shallow, sparse clone of each project's CI configuration, recording commit SHAs |
| `scripts/scan_candidates.py` | Keyword scan for performance-test candidates (step 1 of the protocol) |
| `scripts/summarise_workflows.py` | Lists triggers, schedules, runners and tell-tale strings of each candidate workflow, to point the coder at the right lines |
| `CODEBOOK.md` | Coding rules and ambiguous cases |
| `data/repo_shas.csv` | Commit SHA of every primary-repository clone |
| `data/clomonitor_component_repos.csv`, `data/extra_repo_shas.csv` | Additional code, performance and CI repositories searched in step 2, with commit SHAs |
| `data/candidates_primary.csv`, `data/candidates_components.csv` | Keyword candidates (step 1) |
| `data/candidates_disposition.csv` | What happened to every candidate: coded, supporting file, or excluded with a reason |
| `data/coding_workflows.csv` | One row per performance workflow or job (step 2) |
| `data/coding_projects.csv` | One row per project with the project-level outcome (step 2) |
| `scripts/code_workflows.py`, `scripts/code_projects.py`, `scripts/candidate_dispositions.py` | Generate the three coding files; each row records what was read and at which commit |

## Reproduce step 1

```bash
python3 scripts/fetch_ci_configs.py data/cncf_projects_2026-10-20.csv repos/
python3 scripts/scan_candidates.py repos/ candidates.csv
```

Requires Python 3.8+ and git. No other dependencies.

## Licence

Code: Apache License 2.0 (`LICENSE`). Data and documents: CC BY 4.0.
