# Codebook

Rules used to code `data/coding_workflows.csv` (one row per performance workflow or job) and `data/coding_projects.csv` (one row per project). The fields follow `PROTOCOL.md`; the rules below make the judgement calls explicit. Rules marked *(Deviation n)* were fixed during step 2, before any analysis, and are recorded in the protocol's Deviations section.

## What counts as a performance test

- A run that **measures** time, throughput, latency or resource use and makes the numbers available to a person or a check. Micro-benchmarks, component or load tests and cluster scale tests all count.
- **Smoke runs** that execute benchmarks only to keep them compiling or working, and discard the timings by design (for example `-benchtime=1x`, `--skip_expensive_benchmarks`, BenchmarkDotNet `Job Short` with `SkipBaseline`), are recorded with `smoke_only = yes` and do **not** count as performance testing for RQ1. *(Deviation 4)*
- Compiling benchmarks without running them (`cargo test --benches --no-run`) is not recorded.
- **Scale-correctness tests** that only check that a large job succeeds, with no measurement, are excluded (for example the Kubeflow Pipelines 120-node DAG test). *(Deviation 4)*
- Workflows that test a product's **own performance-testing feature** are excluded, because they do not measure the project's performance (Meshery `mesheryctl perf`, Gatekeeper `gator bench`). *(Deviation 4)*
- Keyword hits for "load test" that come only from "upload test results" are false positives. *(Deviation 1)*

## Which repositories belong to a project *(Deviation 2)*

1. The primary repository from the CNCF landscape.
2. Every repository that CLOMonitor (`cncf/clomonitor`, `data/cncf.yaml`, commit `3e452bd`, 20 October 2026) lists for the project with the `code` or `code-lite` check set. Specification and community repositories are thereby mapped to their code repositories.
3. Dedicated performance or CI-system repositories in the project's GitHub organisation, found by probing a fixed list of names (`perf-tests`, `benchmark(s)`, `<project>-benchmark`, `test-infra`, `infra`, `ci`, `tools` and the others listed in Deviation 2), plus Prow job configurations in `kubernetes/test-infra`, `istio/test-infra`, `knative/infra` and `kubevirt/project-infra`.

Repositories found by chance outside this set (`envoyproxy/gateway`, `falcosecurity/libs`, `istio/ztunnel`) are coded with `scope = outside-defined-scope` and affect only the sensitivity column `outcome_including_outside_scope`.

## Trigger

- **Automated**: schedule, push or merge, pull request, release or tag. Runs with no person starting them.
- **On demand**: started by a person through a PR comment or label.
- **Manual only**: `workflow_dispatch` or equivalent only.

## Decision

- **none (report only)**: numbers are printed, uploaded or charted, and nothing fails or alerts on them. Failing only on test errors or request error rates counts as none for performance.
- **fixed threshold gate**: the run fails when a number crosses a constant written in the code or configuration (ClusterLoader2 SLOs, k6 thresholds, test asserts, committed ceilings).
- **baseline/history comparison with alert**: the run compares with an earlier measurement and comments, opens an issue or fails when the change crosses a threshold. A comparison with a baseline measured in the same job (PR versus base branch) counts here.
- **statistical comparison**: a significance test (benchstat, Mann-Whitney) is computed. Coded separately because some projects show it without alerting.
- Code that would alert but is never called is coded as what actually runs, with a note (Vitess `Regression()`, KubeVirt `perfscale-audit`).

## Persistence

- **log only** or **CI artifact (expires)**: gone after the platform's retention period. The GitHub Actions cache counts as expiring.
- **repository branch or gh-pages history**, **external storage**, **external dashboard or database**, **release assets**: kept beyond CI retention.

## Project-level outcome *(Deviation 3 for the "on demand only" level)*

Assigned from the strongest practice found in the project's repositories:

1. **none**: no performance test in CI and no project tooling or documented procedure for running one.
2. **manual/ad hoc only**: the project provides tooling or a documented procedure (Makefile target not used by CI, performance repository, release checklist item, published one-off study), but no CI runs it.
3. **on demand only**: CI runs a performance test only when a person starts it (manual dispatch, PR comment or label).
4. **automated, not persisted**: an automated run whose results expire.
5. **automated and persisted**: an automated run whose results are kept.
6. **automated, persisted and compared**: as 5, plus an automatic alert or gate against a baseline or history (as pre-registered). Fixed-threshold gates and dashboard-only comparisons do not reach this level; they are recorded in `automated_decision`.

**Activity (step 3).** `outcome_active` applies the pre-registered `active` field: a level that rests only on GitHub Actions workflows with no non-skipped run in the 90-day window drops to the level the remaining evidence supports (KEDA, Karmada). `actions_runs_90d` sums non-skipped runs of the project's tracked in-scope workflows; for jobs inside larger workflows it counts runs of the whole workflow, and the job-level sample in `data/run_history_*.csv` shows whether the performance job ran. Prow, internal CI and external services are not measured.

Go `Benchmark` functions alone, without a target, script or documentation that tells people to run them, do not make a project "manual/ad hoc".

## Ambiguous cases

| Project | Issue | Decision |
| --- | --- | --- |
| CRI-O, containerd | Kubernetes Prow node-throughput jobs run with a container runtime | Attributed to Kubernetes, which owns and reads them |
| gRPC | Benchmarks run by Google's internal CI; scripts are public, the schedule is not | Coded automated and persisted (BigQuery, public dashboard); trigger "not public" |
| KEDA | Weekly workflow in a repository inactive since December 2023; GitHub disables schedules in inactive repositories | Coded from the configuration; step 3 run history decides whether it still runs |
| Flux | Benchmark repository runs on PRs and pushes to `bench*` branches, prepared by hand for each release candidate | On demand only |
| Harbor | `goharbor/perf` CI runs the k6 scripts at small size, but only when the perf repository itself changes | Manual/ad hoc only |
| OpenTelemetry | Specification/community primary repository | Mapped to its 39 CLOMonitor code repositories plus `opentelemetry-benchmarks` |
| OPA | Nightly history is compared statistically on a dashboard; the per-push workflow alerts against the commit before the push | Top level: persisted history plus an automatic alerting comparison |
| Kubescape | `helm-charts` triggers a workflow in a vendor repository whose results are not visible | Recorded with decision and persistence "unknown"; does not raise the project outcome |
| Envoy, Falco | Strong practice exists only in repositories outside the defined set | Main outcome from the defined set; sensitivity column shows the alternative |
