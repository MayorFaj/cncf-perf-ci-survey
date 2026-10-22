#!/usr/bin/env python3
"""Shallow, sparse clone of the CI configuration of every project in the population file.

Usage: python3 fetch_ci_configs.py data/cncf_projects_2026-10-20.csv repos/
Only CI-related paths are checked out (.github/, Makefile, .circleci/, .prow*, ci/, .buildkite/,
azure-pipelines*, .gitlab-ci.yml, .travis.yml). The commit SHA of each clone is written to
repos/SHAS.csv so that every coding decision can be traced to a fixed version.
"""
import csv, os, subprocess, sys, concurrent.futures as cf

PATHS = ["/.github/", "/.circleci/", "/.prow*", "/Makefile", "/.travis.yml", "/azure-pipelines*",
         "/.gitlab-ci.yml", "/ci/", "/.buildkite/", "/.ci/"]


def get(row, out):
    url = row["repo_url"].rstrip("/")
    slug = url.split("github.com/")[1].replace("/", "__")
    d = os.path.join(out, slug)
    if not os.path.isdir(d):
        p = subprocess.run(["git", "clone", "-q", "--depth", "1", "--filter=blob:none", "--sparse", url, d],
                           capture_output=True, text=True, timeout=300)
        if p.returncode:
            return slug, "", "clone failed: " + p.stderr.strip()[-120:]
        subprocess.run(["git", "-C", d, "sparse-checkout", "set", "--no-cone", *PATHS], check=True)
    sha = subprocess.run(["git", "-C", d, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    return slug, sha, "ok"


def main(pop, out):
    os.makedirs(out, exist_ok=True)
    rows = list(csv.DictReader(open(pop)))
    with cf.ThreadPoolExecutor(8) as ex, open(os.path.join(out, "SHAS.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["repo", "sha", "status"])
        for slug, sha, status in ex.map(lambda r: get(r, out), rows):
            w.writerow([slug, sha, status])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
