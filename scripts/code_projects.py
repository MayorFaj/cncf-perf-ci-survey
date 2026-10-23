#!/usr/bin/env python3
"""Project-level coding (protocol step 2). One row per project; evidence points to coding_workflows.csv
or to the file/repository read. Outcome levels follow PROTOCOL.md, with the refinement in Deviation 3."""
import csv
import os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D=os.path.join(ROOT,'data')+'/'
N='none'; M='manual/ad hoc only'; O='on demand only'; A='automated, not persisted'; P='automated and persisted'; T='automated, persisted and compared'
# name: (outcome, persisted, automated_decision, smoke_only_seen, outcome_incl_outside_scope, evidence)
X={
'Argo':(N,'','','', '', 'No candidate in argo-cd or 4 CLOMonitor code repos (argo-workflows Makefile has no bench target used in CI)'),
'Buildpacks':(T,'gh-pages history','history comparison with alert (200%, fail-on-alert)','','', 'pack benchmark.yml'),
'CRI-O':(N,'','','','', 'No candidate; cri-o/tools (2019) is not a performance tool. Kubernetes Prow node-throughput jobs exercise a container runtime but belong to Kubernetes (ambiguous case)'),
'Cilium':(P,'GCS results bucket','fixed thresholds (ClusterLoader2)','yes (cilium/ebpf benchtime=1x)','', '8 scale/perf workflows in cilium/cilium'),
'CloudEvents':(N,'','','','', 'Spec repo mapped to 4 CLOMonitor code repos (SDKs); no candidate'),
'CoreDNS':(M,'','','','', 'coredns/perf-tests (last commit 2017-10-27): manual scripts only'),
'Crossplane':(N,'','','','', 'No candidate'),
'CubeFS':(M,'','','','', 'Benchmark tools in repo (blobstore/tool/bench, rpc2/bench); not run in CI'),
'Dapr':(P,'Azure Storage','fixed thresholds (test asserts)','','', 'dapr-perf.yml nightly, dapr-perf-components.yml weekly'),
'Dragonfly':(M,'','','','', 'dragonflyoss/perf-tests (dfbench, active); its CI runs unit tests only'),
'Envoy':(M,'','','yes (benchmark tests with --skip_expensive_benchmarks)',P, 'envoyproxy/envoy-perf (last commit 2024-09-11), Nighthawk, docs FAQ how to benchmark Envoy. Outside defined scope: envoyproxy/gateway gates PRs on >5% benchstat regression and attaches a benchmark report to each release'),
'Falco':(N,'','','',A, 'No candidate in falco, falcosidekick or falcosecurity/test-infra. Outside defined scope: falcosecurity/libs perf.yml gates PRs against the latest master artifact (kept 30 days)'),
'Fluentd':(A,'','none','','', 'benchmark.yml in_tail benchmark on push/PR, job summary only'),
'Flux':(O,'RESULTS.md by hand','none','','', 'fluxcd/flux-benchmark test.yaml: run per release candidate via PR/push to bench* branches'),
'Harbor':(M,'','','','', 'goharbor/perf k6 scripts; its CI only exercises the scripts at small size on changes to the perf repo (last commit 2025-12-08)'),
'Helm':(N,'','','','', 'No candidate; helm/prow (2018) has no performance job'),
'Istio':(P,'S3 per commit (blob.istio.io)','statistical comparison, report only (benchstat)','','', 'Prow postsubmit benchmark-report_istio_postsubmit; optional presubmit. Outside defined scope: ztunnel /test bench'),
'Jaeger':(M,'','','','', 'jaegertracing/jaeger-performance (last commit 2021-06-07; OpenShift Jenkinsfile)'),
'KEDA':(P,'Grafana Cloud k6 + Prometheus remote write','fixed thresholds (k6)','','', 'kedacore/keda-performance weekly on AKS; repo inactive since 2023-12-27, activity checked in step 3'),
'Karmada':(O,'','none (side-by-side, judged by people)','','', 'ci-performance-compare.yaml manual dispatch'),
'Knative':(P,'InfluxDB + grafana.knative.dev','fixed thresholds (SLA checks)','','', 'knative/infra Prow periodic performance-tests_serving_main_periodic'),
'KubeEdge':(N,'','','','', 'No candidate; only docs/images/perf'),
'Kubeflow':(N,'','','','', 'kubeflow/pipelines DAG scale test (120 nodes) checks success only, no measurement: excluded'),
'Kubernetes':(P,'perf-dash','fixed thresholds (ClusterLoader2 SLOs, release-blocking)','','', 'kubernetes/test-infra sig-scalability jobs + kubernetes/perf-tests'),
'Kyverno':(A,'','fixed thresholds (committed ceilings)','','', 'check-tests.yaml + tests-k6.yaml'),
'Linkerd':(M,'','','','', 'No candidate in linkerd2 or linkerd2-proxy; published one-off benchmark studies (2019, 2021)'),
'Open Policy Agent (OPA)':(T,'benchmarks branch (120 nights) + site','statistical comparison (nightly) + regression comment (per push)','','', 'opa benchmarks-nightly.yaml, benchmarks.yaml; gatekeeper /benchmark and bench-test'),
'OpenTelemetry':(T,'gh-pages history; CodSpeed','history comparison with alert (Python 200%, C++ 200%, Rust 120% comment-on-alert); CodSpeed','yes (Go test-bench, .NET validate-benchmarks)','', 'Spec/community repo mapped to CLOMonitor code repos (39) + opentelemetry-benchmarks'),
'Prometheus':(O,'','none (people compare dashboards)','','', 'prombench via PR comment (repository_dispatch)'),
'Rook':(N,'','','','', 'No candidate'),
'SPIFFE':(N,'','','','', 'Spec repo; no candidate in CLOMonitor code repos'),
'SPIRE':(N,'','','','', 'No candidate'),
'The Update Framework (TUF)':(N,'','','','', 'No candidate'),
'TiKV':(A,'','none','','', 'tikv/rust-prometheus criterion on push/PR (logs); tikv docs describe manual go-ycsb benchmarking'),
'Vitess':(P,'arewefastyet database + benchmark.vitess.io','statistical comparison shown on dashboard; no automated alert found','','', 'vitessio/arewefastyet nightly CRON + Benchmark me label'),
'cert-manager':(N,'','','','', 'No candidate; cert-manager/test-infra has no performance job'),
'containerd':(M,'','','','', 'Makefile benchmark target, not used by CI; containerd Prow jobs are builds only'),
'etcd':(P,'perf-dash','none','','', 'kubernetes/test-infra ci-etcd-benchmark-put-amd64 daily'),
'in-toto':(N,'','','','', 'No candidate in 7 code repos'),
'Artifact Hub':(N,'','','','', 'No candidate'),
'Backstage':(M,'','','','', 'catalog-backend performance tests skipped unless PERFORMANCE_TEST is set; no workflow sets it'),
'Chaos Mesh':(N,'','','','', 'No candidate'),
'Cloud Custodian':(N,'','','','', 'No candidate; cloud-custodian/infra (2023) has no performance job'),
'Confidential Containers':(N,'','','','', 'Umbrella repo mapped to CLOMonitor code repo (operator); no candidate'),
'Container Network Interface (CNI)':(N,'','','','', 'No candidate'),
'Contour':(M,'','','','', 'Makefile bench target deploys a GCP cluster (not used by CI); projectcontour/contour-perf last commit 2021-03-04'),
'Cortex':(M,'','','','', 'cortexproject/test-infra corbench (last commit 2025-08-06); no trigger in cortex CI'),
'Emissary-Ingress':(N,'','','','', 'No candidate'),
'Flatcar Container Linux':(N,'','','','', 'No candidate'),
'Fluid':(N,'','','','', 'No candidate'),
'HAMi':(N,'','','yes (BENCHTIME=10x, timings deliberately not compared)','', 'ci.yaml benchmark smoke run'),
'KServe':(M,'','','','', 'test/benchmark and docs/samples/performance-testing: manual'),
'Keycloak':(P,'result-data branch','none on performance (error-rate check only)','','', 'keycloak/keycloak-benchmark weekly ROSA run'),
'KubeVela':(N,'','','','', 'No candidate'),
'KubeVirt':(P,'Prometheus (3 months) + Grafana','none (audit tool not invoked)','','', 'kubevirt/project-infra periodic sig-performance 3x daily'),
'Kubescape':(A,'','baseline comparison with gate (>10% CPU/memory vs latest release, same job)','','', 'node-agent benchmark.yaml per PR; helm-charts triggers a vendor repository on label'),
'Lima':(N,'','','','', 'No candidate'),
'Litmus':(N,'','','','', 'No candidate'),
'Longhorn':(M,'','','','', 'Release checklist issue template for manual benchmarks; longhorn/benchmark (kbench) tool, CI builds the tool only'),
'Meshery':(N,'','','','', 'Performance workflows test Meshery performance-management features, not Meshery performance: excluded'),
'Microcks':(N,'','','','', 'k6 used for functional API tests: excluded'),
'NATS':(A,'','none','','', 'nats-server mqtt-test benchmarks per PR (logs, TODO compare); nats.rs cargo bench on push (artifact)'),
'Notary Project':(N,'','','','', 'No candidate'),
'OpenCost':(N,'','','','', 'No candidate'),
'OpenFGA':(A,'Actions cache only (expires)','history comparison with alert (github-action-benchmark, fail-on-alert)','','', 'main.yaml and pull_request.yaml; baseline kept only in the Actions cache'),
'OpenFeature':(M,'','','','', 'Spec repo mapped to CLOMonitor code repos; flagd Makefile benchmark target not used by CI'),
'OpenKruise':(N,'','','','', 'No candidate'),
'OpenYurt':(N,'','','','', 'No candidate'),
'Operator Framework':(N,'','','','', 'No candidate; operator-framework/test-infra (2021) has no performance job'),
'Strimzi':(O,'','none','','', 'system-tests.yml /gha run pipeline=performance on CNCF-provided runners'),
'Tekton':(N,'','','','', 'No candidate; tektoncd/plumbing has no performance job'),
'Thanos':(N,'','','','', 'No candidate'),
'Volcano':(M,'','','','', 'benchmark/ framework for kind+KWOK or real clusters: manual'),
'gRPC':(P,'BigQuery + public dashboard','none','','', 'grpc/grpc tools/internal_ci performance jobs on GKE (internal CI)'),
'k8gb':(N,'','','','', 'No candidate'),
'metal3-io':(N,'','','','', 'No candidate in 6 code repos'),
'wasmCloud':(P,'S3 history + site','none','','', 'bench.yml and k6bench.yml on release; bench-compare.yml manual'),
}
pop=list(csv.DictReader(open(D+'cncf_projects_2026-10-20.csv')))
assert set(X)=={r['name'] for r in pop}, set(X)^{r['name'] for r in pop}
# Step 3: activity. Sum of non-skipped runs in the 90-day window over the project's tracked GitHub Actions
# workflows in the defined scope (data/run_history_*.csv). Projects whose tests run on Prow or an external
# service are marked n/a. outcome_active applies the pre-registered 'active' field: a level that rests only on
# workflows with no run in the window drops to the level the remaining evidence supports.
import glob
RH=sorted(glob.glob(D+'run_history_*.csv'))[-1]
OUTSIDE={('envoyproxy/gateway'),('falcosecurity/libs')}
act={}
for r in csv.DictReader(open(RH)):
    if r['repo'] in OUTSIDE: continue
    n=(int(r['completed'] or 0)-int(r['skipped'] or 0)) if r['state']!='not_found' else 0
    act[r['project']]=act.get(r['project'],0)+max(n,0)
NOT_ACTIONS={'Kubernetes','etcd','Istio','KubeVirt','Knative','gRPC'}
DOWN={'KEDA':(M,'only workflow disabled by GitHub for inactivity (disabled_inactivity), 0 runs in 90 days'),
      'Karmada':(M,'manual comparison workflow had 0 runs in 90 days')}
F=['project','maturity','outcome','persisted_where','automated_decision','smoke_only_runs','outcome_including_outside_scope','actions_runs_90d','outcome_active','evidence']
w=csv.DictWriter(open(D+'coding_projects.csv','w',newline=''),fieldnames=F,lineterminator='\n'); w.writeheader()
for r in pop:
    o,p,d,s,oo,e=X[r['name']]
    nm=r['name']
    runs=('n/a (Prow or internal CI)' if nm in NOT_ACTIONS else 'n/a (external service: arewefastyet)' if nm=='Vitess'
          else 'unknown (performance job absent from 30 sampled system-test runs)' if nm=='Strimzi'
          else (act.get(nm,'') if nm in act else ''))
    oa,why=DOWN.get(nm,(o,''))
    w.writerow(dict(zip(F,[nm,r['maturity'],o,p,d,s,oo or o,runs,oa,e+('; step 3: '+why if why else '')])))
from collections import Counter
for m in ('graduated','incubating',None):
    c=Counter(DOWN.get(r['name'],(X[r['name']][0],))[0] for r in pop if m is None or r['maturity']==m)
    print('active', m or 'all', sum(c.values()), dict(c))
