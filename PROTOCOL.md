# How do CNCF projects test performance in CI? Study protocol

Status: **pre-registered**. Committed on 22 October 2026, before full data collection. Changes after this commit are recorded in the Deviations section at the end.
Author: Mayowa Fajobi (ORCID 0009-0009-5848-5825)
Target: IEEE Software article (4,200 words incl. figures; 15 references; 3 practitioner insights). The data and code are released openly with a DOI.

## Motivation

Our nightly kgateway data showed that a pass/fail scale gate missed a 7x teardown improvement and a 10x route-ready gap between release lines, because the numbers were printed to logs and never kept or compared (companion industry paper and data paper, both under submission; dataset DOI 10.5281/zenodo.23568203). Is this typical? We do not know how cloud-native projects run performance tests in CI, what they do with the results, or whether those results survive.

## Research questions

- **RQ1 Prevalence.** How many CNCF graduated and incubating projects run performance, benchmark or scale tests automatically in CI?
- **RQ2 Practice.** When they do: what kind of test (micro-benchmark, load or end-to-end, cluster scale), on what trigger (per PR, per merge, scheduled, on demand, manual), on which branches, and on what infrastructure (shared hosted runners, self-hosted, cloud clusters)?
- **RQ3 Use of results.** Do they gate (fail on a threshold), compare against a baseline or history (alerting), or only report? Are results persisted beyond log or artifact retention, and where (repository branch, external dashboard, database)?
- **RQ4 Lessons.** What do maintainers' own documents (proposals, issues, docs) say about noise, cost and false alarms?

## Population and sample

- All projects at CNCF **graduated** or **incubating** maturity in the CNCF landscape (`cncf/landscape`, `landscape.yml`, commit `f667e522238a058238190107ca94e5cdb08c4009` of 20 October 2026): **77 projects (39 graduated, 38 incubating)**, listed in `data/cncf_projects_2026-10-20.csv`. No sampling: the full population is studied.
- Unit of analysis: the **project**, not one repository. For each project we inspect its primary repository (from the landscape) and, when the project points to them, dedicated performance repositories or CI systems (for example a separate perf-tests repository, Prow jobs, or a benchmark dashboard).
- Projects whose primary repository is a specification or community repository without code (for example CloudEvents spec, OpenFeature spec, SPIFFE spec, OpenTelemetry community) are mapped to their main implementation repository if the project names one, and otherwise reported as "no code repository".
- Sandbox projects are out of scope; kgateway (sandbox) is the motivating case only.

## Data collection

1. **Automated candidate detection.** Shallow, sparse clone of each repository's CI configuration (`scripts/fetch_ci_configs.py`: `.github/`, `Makefile`, `.circleci/`, `.prow*`, `ci/`, `.buildkite/`, `azure-pipelines*`), recording each clone's commit SHA. Keyword scan for performance-test signals (`scripts/scan_candidates.py`: benchmark, `-bench`, benchstat, perf/load/scale test, ClusterLoader2, kube-burner, k6, fortio, nighthawk, ghz, vegeta, github-action-benchmark, Bencher, CodSpeed, JMH, criterion, and others listed in the script).
2. **Manual verification and coding.** Every candidate file is read and coded; keyword hits that are not performance tests (for example "upload test results") are discarded. For projects with no candidate, we additionally search the project's documentation and organisation repositories for performance-testing infrastructure, so that tests run outside the main repository are not missed.
3. **Run history.** For each confirmed automated performance workflow on GitHub Actions, we record from the public API whether it ran in the last 90 days, how often, and its success rate.
4. Every coding decision is recorded with the file path and commit SHA, so that it can be checked.

## Coding scheme (per confirmed performance workflow or job)

| Field | Values |
|---|---|
| test_kind | micro-benchmark; component/load; end-to-end cluster scale |
| trigger | per PR; per merge/push; scheduled (frequency); on demand (comment/label); manual only; release only |
| branches | main only; main + release branches |
| infrastructure | hosted runner; self-hosted/bare metal; cloud cluster (provider); unknown |
| decision | none (report only); fixed threshold gate; baseline/history comparison with alert; statistical comparison (e.g. benchstat) |
| persistence | log only; CI artifact (expires); repository branch or gh-pages history; external dashboard or database |
| visibility | PR comment; dashboard; none |
| active | ran in last 90 days (yes/no); runs in last 90 days; success rate |

Project-level outcome: **none**; **manual/ad hoc only** (documented but not automated); **automated, not persisted**; **automated and persisted**; **automated, persisted and compared** (alerting or gating on history).

## Reliability

The author codes all projects. To check the coding, a random 20% of projects are re-coded from scratch after two weeks without looking at the first coding, and agreement is reported (Cohen's kappa for the project-level outcome). Ambiguous cases are listed in the release.

## Analysis

Descriptive counts and proportions for RQ1 to RQ3, split by maturity (graduated vs incubating). No statistical claims beyond description; the population is small and fully enumerated. RQ4 is a short qualitative summary with quotes from public project documents.

## Threats

- Tests run in systems we cannot see (private CI, vendor labs) are missed; we report what is publicly visible, which is also what contributors can see.
- Keyword detection can miss unusual names; the manual search of projects with no hits reduces this.
- A snapshot in time: workflows change. All inputs are pinned to commit SHAs and dates.

## Pilot (22 October 2026)

All 77 repositories cloned. The keyword scan, excluding git internals, matched 161 files in 37 repositories; restricted to workflow, Makefile and CI-system files with a strong signal (for example benchstat, k6, ClusterLoader2, github-action-benchmark, perf/scale-test names), 22 of 77 repositories have candidates. Broad terms such as "benchmark" also match issue templates and documentation, which confirms that manual coding (step 2) is required. Five candidates read in full show the range the coding scheme must capture:

- Open Policy Agent: nightly benchmark workflow (02:00 UTC), results uploaded as CI artifacts.
- OpenFGA: benchmarks on every push to main with github-action-benchmark, history kept and alerting that can fail the build.
- Cilium: ClusterLoader2 scale tests on GCE, scheduled on weekdays, plus network, L7 and FQDN performance workflows.
- Prometheus: prombench, started on demand from a pull-request comment, runs on a dedicated cluster.
- Karmada: performance comparison started manually; results as artifacts.

Known limitation shown by the pilot: Kubernetes runs its scale tests from Prow and the separate `kubernetes/perf-tests` repository, so its main repository shows no performance workflow. The protocol's step 2 (organisation and documentation search) is required, not optional.

## Planned outputs

- An IEEE Software article (practitioner-oriented, peer reviewed).
- The coded data set and scripts, archived on Zenodo with a DOI.

## Timeline

- Late Oct: commit protocol, full collection and coding.
- Early Nov: reliability re-coding; analysis.
- Nov to Dec: article draft; email abstract to IEEE Software editor-in-chief.

## Deviations

Deviations 1 to 6 were made during step 2 (coding, 23 October 2026), before run-history collection. Deviations 7 and 8, and the codebook rule that lowers a project's level when its configured jobs did not run in the 90-day window, were set on 23 and 24 October after run history was collected and before the article was written. Coding rules are spelled out in `CODEBOOK.md`.

1. **Keyword false positives.** The pattern for "load test" also matches "upload test results". The scan script is left as pre-registered; every such hit was checked with a word-boundary search and is listed as a false positive in `data/candidates_disposition.csv`.
2. **Repository set.** Step 2 showed that core performance practice often lives outside the primary repository (for example OpenTelemetry's language repositories and Kubernetes' Prow jobs). To keep the search systematic rather than ad hoc, a project's repositories are defined as: (a) the landscape primary repository; (b) all repositories CLOMonitor lists for the project with the `code` or `code-lite` check set (`cncf/clomonitor` commit `3e452bd71c6f3640752036744a2111eec4cd2677`, 20 October 2026; 198 additional repositories after removing two redirects of primary repositories, `dragonflyoss/Dragonfly2` and `oam-dev/kubevela`); (c) organisation repositories matching a fixed list of names, probed with `git ls-remote` (perf-tests, perf-test, perf, performance, benchmark, benchmarks, bench, \<project\>-benchmark(s), \<project\>-bench, \<project\>-perf, \<project\>-performance, \<project\>-perf-tests, \<project\>-scale-tests, scale-tests, loadtest, load-test, \<project\>-loadtest, tools, test-infra, performance-tests, perf-testing, benchmarking, benchmark-tests, perf-dashboard, perfdash, loadtesting, load-testing, scale, scale-test, scale-testing, \<project\>-perf-test, \<project\>-performance-tests, \<project\>-load-test(s), \<project\>-scale, \<project\>-scale-test, \<project\>-benchmarking, bench-tools, benchmark-tools, perf-tools, \<project\>-perf-tools, nighthawk, infra, ci, \<project\>-ci, ci-infra, prow); (d) Prow job configurations for the projects in `kubernetes/test-infra`, `istio/test-infra`, `knative/infra` and `kubevirt/project-infra`. The GitHub organisation listing API was not available from the collection environment, so (c) replaces a full listing. Repositories found outside this set are coded but reported only as a sensitivity result.
3. **Outcome levels.** "manual/ad hoc only" is split into "manual/ad hoc only" (tooling or documentation, no CI run) and "on demand only" (CI runs the test when a person starts it by manual dispatch, comment or label). Merging the two recovers the pre-registered scale.
4. **Coding rules clarified.** Smoke runs that discard timings are recorded but not counted for RQ1; scale tests without measurement, and tests of a product's own performance-testing feature, are excluded. Fixed-threshold gates and dashboard-only comparisons do not reach the "compared" level, which keeps the pre-registered definition (alerting or gating against a baseline or history).
5. **Extra columns.** `coding_workflows.csv` adds `scope` and `smoke_only`; `coding_projects.csv` adds `outcome_including_outside_scope`. The `active` field is filled in step 3.
6. **Step 3 data source.** The collection environment's GitHub API access is limited to configured repositories, so run history (step 3) will be collected by a GitHub Actions workflow in this repository using its own token against the public Actions API.

7. **Reliability check.** To report this month, the planned re-coding by the author after two weeks was replaced by a blind re-coding by a second coder: a senior platform engineer who did not take part in the first coding re-coded a random 20% sample (16 projects, seed 20261024, `data/reliability_sample.json`) from the codebook without its ambiguous-cases table and the sampled repositories alone, with no access to the first coding. Agreement on the project-level outcome was 14 of 16, Cohen's kappa 0.79 (`data/reliability_human_coder.csv`, `analysis/reliability.json`). The two disagreements were resolved as follows. CRI-O: the second coder was right; `docs/ci.md` documents an on-demand performance job, so CRI-O moves from none to manual/ad hoc. Envoy: Envoy Mobile's `mobile-perf.yml` compares binary size, which the first coding had already excluded for otel-arrow; the rule is now written in the codebook and Envoy stays manual/ad hoc. Because the CRI-O case showed that documented tooling can be missed, every project coded none was re-examined by listing its repository trees for performance, benchmark, load, scale and stress paths and documents; six more moved to manual/ad hoc (Argo, CloudEvents, HAMi, KubeEdge, KubeVela, Microcks). A supplementary scan of all workflow file names and titles in the defined set for perf, bench, load, scale, stress, latency, throughput, soak and capacity found one more performance workflow (Kubescape `storage` perf-ab), which did not change any project outcome; its run history was not collected (`data/supplementary_scan.csv`). The agreement reported is the one before these corrections. An AI coding agent given the same materials in a separate session produced identical labels; its notes are kept in `data/reliability_second_coder.csv`.
8. **Attribution of Kubernetes node jobs.** Kubernetes SIG Node runs node performance tests against CRI-O and containerd every 12 hours in `kubernetes/test-infra`. They are attributed to Kubernetes, which owns them; attributing them to CRI-O and containerd is reported as a sensitivity result.

**Corrections to the pilot notes** (facts, not method changes): OPA's nightly results are kept on a `benchmarks` branch (120 nights) and published as a site, not only as CI artifacts. OpenFGA keeps its baseline only in the GitHub Actions cache, which expires, so it does not keep a lasting history.
