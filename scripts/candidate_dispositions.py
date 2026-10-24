#!/usr/bin/env python3
"""Usage: python3 candidate_dispositions.py <survey-dir with repos/ and comp_repos/>
List every keyword candidate (primary and CLOMonitor component repositories) with its disposition."""
import csv,re,os
import os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys
S=sys.argv[1].rstrip('/')+'/'  # survey working directory holding repos/ and comp_repos/ clones
D=os.path.join(ROOT,'data')+'/'
coded=list(csv.DictReader(open(D+'coding_workflows.csv')))
def is_coded(repo,f):
    for r in coded:
        if r['repo'].lower()==repo.lower() and (f in r['file'] or os.path.basename(f) in r['file']): return True
    return False
LOADWORD=re.compile(r'(?<![a-z])load[ _-]?tests?',re.I)
REASON=[
 (r'^\.github/(actions/cl2-modules|ariane-config|actions/setup-aks-cluster|actions/bpftrace)','supporting file of coded Cilium scale/perf workflows'),
 (r'^\.github/actions/tools/(install|k6)/','supporting file of coded Kyverno k6 workflow'),
 (r'^\.github/(actions/systemtests/run-perf-report|tests/(expected|inputs)/perf-report)','supporting file or test fixture of coded Strimzi performance pipeline'),
 (r'^\.github/scripts/bench-','supporting script of coded wasmCloud bench workflows'),
 (r'^\.github/workflows/scripts/(consolidate-benchmarks|analyze-)','supporting script of coded otel-arrow perf workflows'),
 (r'(renovate\.json5|codecov\.yml|component_owners\.yml|/skills/|/instructions/|commit_prefix_check\.py|update-gradle-wrappers\.sh|test_report_owner_coverage\.py)','configuration, assistant instructions or housekeeping script'),
 (r'\.(png|jpg|svg|gif)$','image file (binary match)'),
 (r'(ISSUE_TEMPLATE|PULL_REQUEST_TEMPLATE|pull_request_template|SECURITY\.md|stale\.yml|CODEOWNERS|dependabot\.yml|copilot-instructions|/agents/|/meetings/|security-self-assessment|README\.md$|cspell\.json)','template, policy or documentation file'),
]
special={
 ('cilium/cilium','.github/workflows/scale-cleanup-kops.yaml'):'cleanup of scale-test clusters, not a test',
 ('cilium/cilium','.github/workflows/common-post-jobs.yaml'):'shared post-job steps',
 ('dapr/dapr','.github/workflows/dapr-perf-publish-charts.yml'):'manual chart publishing for docs (noted in dapr-perf row)',
 ('dapr/dapr','.github/scripts/dapr_bot.js'):'bot handling the ok-to-perf command (noted in dapr-perf row)',
 ('fluxcd/flux2','.github/workflows/conformance.yaml'):'conformance test, not performance',
 ('meshery/meshery','.github/workflows/mesheryctl-e2e.yaml'):'tests the product performance-test feature (mesheryctl perf), not Meshery performance',
 ('metal3-io/baremetal-operator','.github/workflows/plugin-test.yml'):'plugin loading test',
 ('microcks/microcks','.github/workflows/api-check.yml'):'k6 used for functional API checks',
 ('open-policy-agent/gatekeeper','.github/workflows/test-gator.yaml'):'tests the gator bench CLI feature, not Gatekeeper performance',
 ('kubeflow/pipelines','.github/workflows/e2e-test.yml'):'DAG scale test checks success only, no measurement',
 ('kubescape/node-agent','.github/workflows/bypass.yaml'):'manual bypass of the benchmark check',
 ('kubescape/node-agent','.github/workflows/incluster-comp-pr-merged.yaml'):'calls component tests; benchmark keyword only',
 ('kubescape/node-agent','.github/workflows/pr-merged.yaml'):'merge workflow; benchmark keyword only',
 ('wasmCloud/wasmCloud','.github/workflows/wash.yml'):'compiles benches only (cargo test --benches --no-run)',
 ('wasmCloud/wasmCloud','.github/workflows/k6bench-smoke.yml'):'20-second smoke run that keeps the k6 scripts runnable; publishes nothing',
 ('wasmCloud/wasmCloud','.github/workflows/bench-host-checks.yml'):'monthly bench-host maintenance check',
 ('open-telemetry/otel-arrow','.github/workflows/dataflow-engine-binary-size.yml'):'tracks binary size, not run-time performance',
 ('open-telemetry/otel-arrow','.github/workflows/comparison-dashboard.yml'):'dashboard build (results come from the perf workflows)',
 ('open-telemetry/otel-arrow','.github/workflows/rust-ci.yml'):'build/test workflow; perf keywords refer to perf crates',
 ('open-telemetry/otel-arrow','.github/workflows/rust-bench.yml'):'on demand (cargobench label), report only; covered by otel-arrow rows',
 ('open-telemetry/otel-arrow','.github/workflows/pipeline-perf-on-label.yaml'):'on demand variant of the pipeline perf suite (noted in otel-arrow row)',
 ('open-telemetry/otel-arrow','.github/workflows/pipeline-perf-test-manual-pr.yaml'):'manual variant of the pipeline perf suite (noted in otel-arrow row)',
 ('open-telemetry/opentelemetry-java-instrumentation','.github/workflows/publish-petclinic-benchmark-image.yml'):'builds the image used by the overhead benchmark',
 ('open-telemetry/opentelemetry-java-instrumentation','.github/workflows/build-common.yml'):'build workflow; benchmark keyword only',
 ('open-telemetry/opentelemetry-js','.github/workflows/docs.yaml'):'docs publishing',
 ('open-telemetry/opentelemetry-dotnet-contrib','.github/workflows/publish-packages.yml'):'package publishing; benchmark keyword only',
 ('open-telemetry/opentelemetry-dotnet-contrib','.github/workflows/ci.yml'):'path filter for benchmark project only',
 ('open-telemetry/opentelemetry-java','.github/workflows/build.yml'):'build workflow; jmh compile only',
 ('open-telemetry/opentelemetry-java','.github/workflows/codeql.yml'):'CodeQL; benchmarks branch filter only',
 ('open-telemetry/opentelemetry-cpp','.github/workflows/codeql-analysis.yml'):'CodeQL; benchmark library install only',
 ('open-telemetry/opentelemetry-cpp','.github/workflows/iwyu.yml'):'include-what-you-use; benchmark library only',
 ('open-telemetry/opentelemetry-cpp','.github/workflows/cmake_install.yml'):'install test; benchmark library only',
 ('open-telemetry/opentelemetry-cpp','.github/workflows/clang-tidy.yaml'):'clang-tidy; benchmark library only',
 ('open-telemetry/opentelemetry-cpp-contrib','.github/workflows/prometheus.yml'):'build; benchmark library install only',
 ('open-telemetry/opentelemetry-cpp-contrib','.github/workflows/fluentd.yml'):'build; benchmark library only',
 ('open-telemetry/opentelemetry-cpp-contrib','.github/workflows/codeql.yml'):'CodeQL; benchmark library only',
 ('open-telemetry/opentelemetry-python','.github/workflows/generate_workflows.py'):'workflow generator',
 ('open-telemetry/opentelemetry-python-contrib','.github/workflows/generate_workflows_lib/src/generate_workflows_lib/__init__.py'):'workflow generator',
 ('open-telemetry/opentelemetry-collector-contrib','.github/workflows/scripts/setup_e2e_tests.sh'):'e2e setup script',
 ('open-telemetry/opentelemetry-java-instrumentation','.github/workflows/overhead-benchmark-daily.yml'):None,
}
special.update({
 ('keycloak/keycloak','.github/scripts/aws/rds/aurora_create.sh'):'Aurora database integration-test setup (reuses keycloak-benchmark infrastructure scripts)',
 ('longhorn/longhorn','.github/workflows/create-release-task-issues.yml'):'creates a manual benchmark task issue per release (project coded manual/ad hoc)',
 ('meshery/meshery','.github/integration-test-config.yaml'):'tests the product performance-test feature',
 ('vitessio/vitess','.github/workflows/update_golang_version.yml'):'adds the Benchmark me label to Go upgrade PRs (noted in Vitess row)',
 ('Project-HAMi/HAMi','Makefile'):'bench target called by the coded ci.yaml smoke run',
 ('openfga/openfga','Makefile'):'test-bench target called by the coded main.yaml and pull_request.yaml',
 ('etcd-io/etcd','Makefile'):'bench-put target called by the coded Prow job ci-etcd-benchmark-put-amd64',
 ('kubevirt/kubevirt','Makefile'):'perftest target called by the coded Prow job periodic-kubevirt-e2e-k8s-1.36-sig-performance',
 ('open-policy-agent/opa','Makefile'):'developer targets (perf, benchlab); CI uses go run ./build/bench-* directly',
 ('open-policy-agent/gatekeeper','Makefile'):'benchmark-test and native-bench-test targets called by the coded gatekeeper workflows',
 ('open-telemetry/opentelemetry-collector','Makefile'):'gobenchmark target called by the coded perf.yml',
 ('open-telemetry/opentelemetry-go','Makefile'):'benchmark and test-bench targets called by the coded benchmark.yml and ci.yml',
 ('kubeflow/pipelines','.github/resources/scripts/scale_pipeline_test.py'):'scale correctness script, no measurement',
 ('open-telemetry/opentelemetry-cpp','ci/do_ci.sh'):'script behind the coded opentelemetry-cpp benchmark job',
 ('open-telemetry/opentelemetry-cpp','ci/setup_windows_ci_environment.ps1'):'installs the benchmark library only',
})
rows=[]
for fn,base in [('candidates_primary.csv','repos'),('candidates_components.csv','comp_repos')]:
    for r in csv.DictReader(open(D+fn)):
        repo=r['repo'].replace('__','/',1); f=r['file']
        if is_coded(repo,f): disp='coded'; reason=''
        elif (repo,f) in special and special[(repo,f)]: disp='excluded'; reason=special[(repo,f)]
        else:
            reason=None
            for pat,why in REASON:
                if re.search(pat,f): reason=why; break
            if reason is None and set(r['keywords'].split())<= {'load','test','load-test','tests'} :
                t=open(S+base+'/'+r['repo']+'/'+f,errors='ignore').read()
                if not LOADWORD.search(t): reason='false positive: "load test" only inside "upload test..." (Deviation 1)'
            if reason is None and f.endswith('Makefile'): reason='Makefile target not invoked by any CI configuration (manual tooling; see coding_projects.csv)'
            if reason is None: reason='UNRESOLVED'
            disp='excluded'
        if disp=='excluded' and re.search(r'(called by the coded|^supporting|script behind the coded|noted in .* row|covered by .* rows)',reason or ''): disp='supporting file of coded workflow'
        rows.append({'repo':repo,'file':f,'keywords':r['keywords'],'disposition':disp,'reason':reason,'source':'primary' if base=='repos' else 'clomonitor-component'})
w=csv.DictWriter(open(D+'candidates_disposition.csv','w',newline=''),fieldnames=list(rows[0]),lineterminator='\n'); w.writeheader(); w.writerows(rows)
from collections import Counter
print(Counter(r['disposition'] for r in rows))
for r in rows:
    if r['reason']=='UNRESOLVED': print('UNRESOLVED',r['repo'],r['file'],r['keywords'])
