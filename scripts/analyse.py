#!/usr/bin/env python3
"""Analysis for RQ1 to RQ3 (protocol 'Analysis' section): descriptive counts by maturity.

Usage: python3 scripts/analyse.py   (writes analysis/results.md, analysis/results.json, analysis/outcomes.pdf/.png)
Reads data/coding_projects.csv, data/coding_workflows.csv and the latest data/run_history_*.csv.
Only workflows in the defined repository set (scope != outside-defined-scope) that are not smoke runs count.
"""
import csv, glob, json, os, re
from collections import Counter, OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, 'data'); A = os.path.join(ROOT, 'analysis'); os.makedirs(A, exist_ok=True)
LEVELS = ['none', 'manual/ad hoc only', 'on demand only', 'automated, not persisted',
          'automated and persisted', 'automated, persisted and compared']
AUTO = LEVELS[3:]

proj = list(csv.DictReader(open(os.path.join(D, 'coding_projects.csv'))))
wf = [r for r in csv.DictReader(open(os.path.join(D, 'coding_workflows.csv')))
      if r['scope'] != 'outside-defined-scope' and r['smoke_only'] != 'yes']
mat = {r['project']: r['maturity'] for r in proj}


def table(field):
    out = OrderedDict()
    for lv in LEVELS:
        g = sum(1 for r in proj if r[field] == lv and r['maturity'] == 'graduated')
        i = sum(1 for r in proj if r[field] == lv and r['maturity'] == 'incubating')
        out[lv] = {'graduated': g, 'incubating': i, 'all': g + i}
    return out


res = OrderedDict()
res['n_projects'] = len(proj)
res['n_by_maturity'] = dict(Counter(r['maturity'] for r in proj))
res['outcome_configured'] = table('outcome')
res['outcome_active'] = table('outcome_active')
res['outcome_including_outside_scope'] = table('outcome_including_outside_scope')

# Practice among projects whose configured outcome is automated (RQ2, RQ3)
auto_projects = sorted(r['project'] for r in proj if r['outcome'] in AUTO)
res['automated_projects'] = auto_projects


def kinds(r):
    k = set()
    t = r['test_kind']
    if 'micro' in t: k.add('micro-benchmark')
    if 'component/load' in t: k.add('component or load test')
    if 'cluster scale' in t: k.add('end-to-end cluster scale test')
    return k


def triggers(r):
    t = r['trigger'].lower(); k = set()
    if 'scheduled' in t: k.add('scheduled')
    if 'per merge/push' in t: k.add('every merge or push')
    if 'per pr' in t: k.add('every pull request')
    if 'release' in t: k.add('release')
    if 'on demand' in t: k.add('on demand (comment or label)')
    if 'manual' in t: k.add('manual dispatch')
    return k


def infra(r):
    t = r['infrastructure'].lower()
    if 'dedicated' in t or 'self-hosted' in t or 'bare metal' in t or 'external benchmarking service' in t: return 'dedicated or self-hosted machine'
    if t.startswith('cloud cluster') or 'test cluster' in t: return 'cloud cluster'
    if 'prow' in t: return 'shared Prow build cluster'
    if 'hosted runner' in t: return 'shared hosted runner'
    return 'other'


def decision(r):
    t = r['decision'].lower()
    if t.startswith('fixed threshold'): return 'fixed threshold gate'
    if 'comparison with alert' in t or (t.startswith('statistical comparison') and 'with gate' in t): return 'automatic comparison with alert or gate'
    if t.startswith('statistical comparison'): return 'statistical comparison, report only'
    if t.startswith('unknown'): return 'unknown'
    return 'none (report only)'


def persisted(r):
    t = r['persistence'].lower()
    return not (t.startswith('log only') or t.startswith('ci artifact') or t.startswith('ci cache') or t.startswith('unknown'))


def automated(r):
    t = triggers(r)
    return bool(t & {'scheduled', 'every merge or push', 'every pull request', 'release'})


per = {p: {'kind': set(), 'trigger': set(), 'infra': set(), 'decision': set(), 'persisted': False} for p in auto_projects}
for r in wf:
    p = r['project']
    if p not in per or not automated(r): continue
    per[p]['kind'] |= kinds(r); per[p]['trigger'] |= (triggers(r) & {'scheduled', 'every merge or push', 'every pull request', 'release'})
    per[p]['infra'].add(infra(r)); per[p]['decision'].add(decision(r)); per[p]['persisted'] |= persisted(r)


def count(key, values):
    return OrderedDict((v, sum(1 for p in per if v in per[p][key])) for v in values)


res['practice_among_automated'] = OrderedDict([
    ('n', len(per)),
    ('test_kind', count('kind', ['micro-benchmark', 'component or load test', 'end-to-end cluster scale test'])),
    ('trigger', count('trigger', ['scheduled', 'every merge or push', 'every pull request', 'release'])),
    ('infrastructure', count('infra', ['shared hosted runner', 'shared Prow build cluster', 'dedicated or self-hosted machine', 'cloud cluster'])),
    ('decision', count('decision', ['none (report only)', 'fixed threshold gate', 'statistical comparison, report only', 'automatic comparison with alert or gate'])),
    ('strongest_decision', Counter(next(d for d in ['automatic comparison with alert or gate', 'fixed threshold gate',
                                                     'statistical comparison, report only', 'none (report only)']
                                         if d in per[p]['decision']) for p in per)),
    ('persisted_beyond_ci_retention', sum(1 for p in per if per[p]['persisted'])),
])
res['per_project'] = {p: {k: (sorted(v) if isinstance(v, set) else v) for k, v in per[p].items()} for p in per}

# Run history (step 3)
rh_file = sorted(glob.glob(os.path.join(D, 'run_history_*.csv')))[-1]
rh = list(csv.DictReader(open(rh_file)))
res['run_history_file'] = os.path.basename(rh_file)
res['tracked_workflows'] = len(rh)
res['tracked_in_scope'] = sum(1 for r in rh if 'outside defined scope' not in r['note'])
coded = {(r['repo'], r['file'].split(' ')[0].split('/')[-1]) for r in wf}
sched = []
for r in rh:
    if (r['repo'], r['workflow_file']) in coded and int(r['schedule_runs'] or 0) >= 10:
        sched.append({'repo': r['repo'], 'workflow': r['workflow_file'], 'scheduled_runs': int(r['schedule_runs']),
                      'scheduled_success': int(r['schedule_success']),
                      'rate': round(int(r['schedule_success']) / int(r['schedule_runs']), 3)})
res['scheduled_workflows'] = sorted(sched, key=lambda x: x['rate'])
rates = sorted(x['rate'] for x in sched)
res['scheduled_rate_median'] = rates[len(rates) // 2] if len(rates) % 2 else round((rates[len(rates) // 2 - 1] + rates[len(rates) // 2]) / 2, 3)
res['scheduled_below_80pct'] = sum(1 for x in rates if x < 0.8)
def ran(r):
    # completed and skipped are both capped at 2,500; per-event counts recover runs hidden by the cap
    return max(int(r['completed'] or 0) - int(r['skipped'] or 0),
               sum(int(r[k] or 0) for k in ('schedule_runs', 'push_runs', 'dispatch_runs')))
res['disabled_or_idle'] = [{'repo': r['repo'], 'workflow': r['workflow_file'], 'state': r['state'], 'non_skipped_runs': ran(r)}
                           for r in rh if r['state'] != 'active' or ran(r) <= 2]

json.dump(res, open(os.path.join(A, 'results.json'), 'w'), indent=1)

# Markdown summary
L = ['# Results (generated by scripts/analyse.py)', '', f"Projects: {res['n_projects']} ({res['n_by_maturity']})", '']
for key, title in [('outcome_configured', 'Project-level outcome as configured'), ('outcome_active', 'Outcome allowing for 90-day activity'),
                   ('outcome_including_outside_scope', 'Sensitivity: including repositories outside the defined set and attributing Kubernetes node jobs to CRI-O and containerd')]:
    L += [f'## {title}', '', '| Outcome | Graduated | Incubating | All |', '|---|---|---|---|']
    L += [f"| {lv} | {v['graduated']} | {v['incubating']} | {v['all']} |" for lv, v in res[key].items()] + ['']
pa = res['practice_among_automated']
L += [f"## Practice among the {pa['n']} projects with automated performance tests", '']
for k in ('test_kind', 'trigger', 'infrastructure', 'decision', 'strongest_decision'):
    L += [f'**{k}**: ' + '; '.join(f'{a} {b}' for a, b in pa[k].items()), '']
L += [f"Results kept beyond CI retention: {pa['persisted_beyond_ci_retention']} of {pa['n']}", '']
L += ['## Scheduled workflows with at least 10 scheduled runs in 90 days', '', '| Workflow | Scheduled runs | Succeeded | Rate |', '|---|---|---|---|']
L += [f"| {x['repo']} {x['workflow']} | {x['scheduled_runs']} | {x['scheduled_success']} | {x['rate']:.0%} |" for x in res['scheduled_workflows']]
L += ['', f"Median success rate: {res['scheduled_rate_median']:.0%}; below 80%: {res['scheduled_below_80pct']} of {len(res['scheduled_workflows'])}", '',
      '## Disabled or nearly idle tracked workflows (2 or fewer non-skipped runs)', '']
L += [f"- {x['repo']} {x['workflow']}: state {x['state']}, non-skipped runs {x['non_skipped_runs']}" for x in res['disabled_or_idle']]
open(os.path.join(A, 'results.md'), 'w').write('\n'.join(L) + '\n')

# Figure: outcome by maturity (configured and active), horizontal stacked bars
try:
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    cols = ['#d9d9d9', '#bdd7e7', '#9ecae1', '#6baed6', '#3182bd', '#08519c']
    labels = ['None', 'Manual or ad hoc only', 'On demand only', 'Automated, not kept', 'Automated and kept', 'Automated, kept and compared']
    rows = [('Graduated (39)', 'graduated'), ('Incubating (38)', 'incubating')]
    fig, ax = plt.subplots(figsize=(7.0, 2.3))
    for y, (name, m) in enumerate(rows):
        left = 0
        for c, lv, lab in zip(cols, LEVELS, labels):
            v = res['outcome_active'][lv][m]
            ax.barh(y, v, left=left, color=c, edgecolor='white', label=lab if y == 0 else None)
            if v: ax.text(left + v / 2, y, str(v), ha='center', va='center', fontsize=8, color='white' if lv in AUTO[1:] else 'black')
            left += v
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows], fontsize=9); ax.invert_yaxis()
    ax.set_xlabel('Number of projects', fontsize=9); ax.set_xlim(0, 39)
    for s in ('top', 'right'): ax.spines[s].set_visible(False)
    ax.tick_params(labelsize=8)
    ax.legend(ncol=3, fontsize=7, frameon=False, loc='upper center', bbox_to_anchor=(0.5, -0.38))
    fig.tight_layout()
    fig.savefig(os.path.join(A, 'outcomes.pdf')); fig.savefig(os.path.join(A, 'outcomes.png'), dpi=200)
except ImportError:
    pass
print(open(os.path.join(A, 'results.md')).read())
