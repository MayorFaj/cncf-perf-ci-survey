#!/usr/bin/env python3
"""Aid for protocol step 2: summarise each candidate workflow so it can be read and coded.

Usage: python3 summarise_workflows.py repos/ candidates.csv summary.json
For every candidate file under .github/workflows, records the triggers, cron schedules, branch
filters, runner labels and a fixed list of tell-tale strings (result storage, alerting, tools).
The summary only points the coder at the right lines; codes are assigned by reading the file.
"""
import csv, json, os, re, sys
import yaml

TELLS = ["github-action-benchmark", "fail-on-alert", "alert-threshold", "comment-on-alert", "auto-push",
         "gh-pages", "upload-artifact", "benchstat", "bencher", "codspeed", "clusterloader", "kube-burner",
         "k6", "prombench", "arewefastyet", "threshold", "gsutil", "s3 cp", "grafana", "issue_comment",
         "pull-requests: write", "git push"]


def summarise(path):
    text = open(path, errors="ignore").read()
    info = {"tells": [t for t in TELLS if t in text.lower()]}
    try:
        y = yaml.safe_load(text) or {}
    except Exception as e:  # keep going; the coder reads the file anyway
        info["yaml_error"] = str(e)[:80]
        return info
    on = y.get(True, y.get("on"))
    if isinstance(on, dict):
        info["on"] = list(on.keys())
        info["cron"] = [s.get("cron") for s in (on.get("schedule") or []) if isinstance(s, dict)]
        for k in ("push", "pull_request", "pull_request_target"):
            if isinstance(on.get(k), dict) and on[k].get("branches"):
                info[k + "_branches"] = on[k]["branches"]
    else:
        info["on"] = on if isinstance(on, list) else [on]
    runs = set()
    for job in (y.get("jobs") or {}).values():
        if isinstance(job, dict) and job.get("runs-on") is not None:
            runs.add(json.dumps(job["runs-on"])[:80])
    info["runs_on"] = sorted(runs)
    return info


def main(root, cand_csv, out):
    rows = list(csv.DictReader(open(cand_csv)))
    res = []
    for r in rows:
        if "/workflows/" not in r["file"] or not r["file"].endswith((".yml", ".yaml")):
            continue
        res.append({"repo": r["repo"], "file": r["file"], "keywords": r["keywords"],
                    **summarise(os.path.join(root, r["repo"], r["file"]))})
    json.dump(res, open(out, "w"), indent=1)


if __name__ == "__main__":
    main(*sys.argv[1:4])
