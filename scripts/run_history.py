#!/usr/bin/env python3
"""Protocol step 3: run history of every coded GitHub Actions performance workflow.

Usage: GITHUB_TOKEN=... python3 run_history.py data/actions_tracked.csv data/run_history_<date>.csv [days]

For each tracked workflow it records, over the last `days` (default 90) before the collection time:
- the workflow's state (active, disabled_manually, disabled_inactivity, or not_found);
- the number of runs, the number of completed runs, and how many concluded success or failure
  (counts come from the API's total_count, so they are exact even for busy workflows);
- the date of the most recent run.
When `job_regex` is set, the performance test is one job inside a larger workflow. The script then
also reads the jobs of the most recent completed runs (up to JOB_SAMPLE) and reports how many of them
contained a matching job and how those jobs concluded, because the workflow-level numbers then
describe the whole CI workflow, not the performance job.
Only the public GitHub REST API is used; no repository is modified.
"""
import csv, datetime as dt, json, os, re, sys, time, urllib.error, urllib.parse, urllib.request

API = "https://api.github.com"
JOB_SAMPLE = 30


def get(path, params=None):
    url = API + path + ("?" + urllib.parse.urlencode(params) if params else "")
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28",
        **({"Authorization": "Bearer " + os.environ["GITHUB_TOKEN"]} if os.environ.get("GITHUB_TOKEN") else {})})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if e.code in (403, 429, 500, 502, 503) and attempt < 4:
                reset = e.headers.get("x-ratelimit-reset")
                wait = max(5, int(reset) - int(time.time()) + 1) if reset and e.headers.get("x-ratelimit-remaining") == "0" else 10 * (attempt + 1)
                time.sleep(min(wait, 900))
                continue
            raise


def count(repo, wf, since, **extra):
    d = get(f"/repos/{repo}/actions/workflows/{wf}/runs", {"created": ">=" + since, "per_page": 1, **extra})
    return (d or {}).get("total_count", 0), ((d or {}).get("workflow_runs") or [None])[0]


def job_sample(repo, wf, since, rx):
    d = get(f"/repos/{repo}/actions/workflows/{wf}/runs",
            {"created": ">=" + since, "status": "completed", "per_page": JOB_SAMPLE})
    runs = (d or {}).get("workflow_runs") or []
    with_job, concl = 0, {}
    for run in runs:
        jobs = get(f"/repos/{repo}/actions/runs/{run['id']}/jobs", {"per_page": 100, "filter": "latest"}) or {}
        hits = [j for j in jobs.get("jobs", []) if re.search(rx, j.get("name") or "")]
        if hits:
            with_job += 1
            for j in hits:
                concl[j.get("conclusion") or "none"] = concl.get(j.get("conclusion") or "none", 0) + 1
    return len(runs), with_job, concl


def main(tracked, out, days=90):
    now = dt.datetime.now(dt.timezone.utc)
    since = (now - dt.timedelta(days=int(days))).strftime("%Y-%m-%d")
    fields = ["project", "repo", "workflow_file", "collected_at", "window_start", "state", "runs", "completed",
              "success", "failure", "cancelled", "success_rate_completed", "last_run_at", "last_run_event",
              "job_regex", "job_sample_runs", "job_sample_runs_with_job", "job_conclusions", "note"]
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        for t in csv.DictReader(open(tracked)):
            repo, wf = t["repo"], t["workflow_file"]
            row = {k: t.get(k, "") for k in ("project", "repo", "workflow_file", "job_regex", "note")}
            row.update(collected_at=now.strftime("%Y-%m-%dT%H:%M:%SZ"), window_start=since)
            meta = get(f"/repos/{repo}/actions/workflows/{wf}")
            if meta is None:
                row["state"] = "not_found"
                w.writerow(row)
                continue
            row["state"] = meta.get("state")
            runs, last = count(repo, wf, since)
            completed, _ = count(repo, wf, since, status="completed")
            success, _ = count(repo, wf, since, status="success")
            failure, _ = count(repo, wf, since, status="failure")
            cancelled, _ = count(repo, wf, since, status="cancelled")
            row.update(runs=runs, completed=completed, success=success, failure=failure, cancelled=cancelled,
                       success_rate_completed=round(success / completed, 3) if completed else "",
                       last_run_at=(last or {}).get("created_at", ""), last_run_event=(last or {}).get("event", ""))
            if t.get("job_regex"):
                n, k, c = job_sample(repo, wf, since, t["job_regex"])
                row.update(job_sample_runs=n, job_sample_runs_with_job=k,
                           job_conclusions=";".join(f"{a}={b}" for a, b in sorted(c.items())))
            w.writerow(row)
            f.flush()
            print(repo, wf, row["state"], runs, file=sys.stderr)


if __name__ == "__main__":
    main(*sys.argv[1:4])
