#!/usr/bin/env python3
"""Step 1 of the protocol: keyword scan of CI configuration for performance-test signals.

Usage: python3 scan_candidates.py repos/ candidates.csv
Writes one row per (repository, file) with the matched keywords. Git internals are skipped.
Every candidate is then read and coded by hand (protocol step 2); a keyword hit alone is not a finding.
"""
import csv, glob, os, re, sys

KEYWORDS = re.compile(
    r"(benchmark|benchstat|-bench\b|perf(ormance)?[-_ ]?tests?|load[-_ ]?tests?|scale[-_ ]?tests?|scalability|"
    r"clusterloader2?|kube-burner|\bk6\b|fortio|\bghz\b|nighthawk|codspeed|bencher\b|github-action-benchmark|"
    r"hyperfine|criterion|\bjmh\b|vegeta|\bwrk2?\b|locust|soak)", re.I)


def main(root, out):
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["repo", "file", "keywords"])
        for d in sorted(glob.glob(os.path.join(root, "*/"))):
            repo = os.path.basename(d.rstrip("/"))
            for path in glob.glob(d + "**/*", recursive=True) + glob.glob(d + ".*/**/*", recursive=True):
                rel = os.path.relpath(path, d)
                if rel.startswith(".git" + os.sep) or not os.path.isfile(path) or os.path.getsize(path) > 500_000:
                    continue
                try:
                    text = open(path, errors="ignore").read()
                except OSError:
                    continue
                hits = sorted({m.group(0).lower() for m in KEYWORDS.finditer(text)})
                if hits:
                    w.writerow([repo, rel, " ".join(hits)])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
