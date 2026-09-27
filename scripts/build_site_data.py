"""Build the presentation's pinned evidence snapshot; no API calls or private files."""
import argparse
import csv
import io
import json
from pathlib import Path
import sqlite3
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'
parser = argparse.ArgumentParser()
parser.add_argument('--run1', default='7901618f5bb79faab75c5ed98855b97dac3fe493')
parser.add_argument('--run2', default='38597025821c4efad18d20171f79e894cb988daf')
args = parser.parse_args()

def blob(ref, path):
    return subprocess.check_output(['git', 'show', f'{ref}:{path}'], cwd=ROOT)

def rows(ref, path):
    return list(csv.DictReader(io.StringIO(blob(ref, path).decode())))

def stats(ref):
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / 'papers.sqlite'
        db.write_bytes(blob(ref, 'data/db/papers.sqlite'))
        con = sqlite3.connect(f'file:{db}?mode=ro', uri=True)
        result = dict(zip(['papers', 'core', 'extended'], con.execute('SELECT count(*),sum(core_set),sum(extended_set) FROM papers').fetchone()))
        result['routes'] = dict(con.execute('SELECT t.tech_route,count(*) FROM tags t JOIN papers p USING(paper_id) WHERE p.core_set=1 GROUP BY t.tech_route').fetchall())
        con.close()
    result.update(authors=len(rows(ref,'graphs/top_pis.csv')), institutions=len(rows(ref,'graphs/top_institutions.csv')), communities=len(rows(ref,'graphs/clusters.csv')), raw=len(rows(ref,'data/raw/relevance.csv')))
    return result

SITE.mkdir(exist_ok=True)
(SITE/'downloads').mkdir(exist_ok=True)
data = {'snapshot':'2026-09-26', 'repo':'https://github.com/nnicholas-c/ocs-landscape', 'revisions':{'run1':args.run1,'run2':args.run2}, 'run1':stats(args.run1), 'run2':stats(args.run2), 'matrix':rows(args.run1,'deliverables/comparison_matrix.csv'), 'projects':rows(args.run1,'data/projects.csv'), 'people':rows(args.run2,'graphs/top_pis.csv')[:20], 'institutions':rows(args.run2,'graphs/top_institutions.csv')[:20]}
(SITE/'assets/data.js').write_text('window.OCS_DATA = '+json.dumps(data,ensure_ascii=False,indent=2)+';\n')
for name, ref in [('run1',args.run1),('run2',args.run2)]:
    (SITE/'downloads'/f'{name}-coauthor.html').write_bytes(blob(ref,'graphs/coauthor.html'))
    for path in ['graphs/top_pis.csv','graphs/top_institutions.csv','deliverables/curation_report.md','STATUS.md']:
        (SITE/'downloads'/f'{name}-{Path(path).name}').write_bytes(blob(ref,path))
(SITE/'downloads/comparison_matrix.csv').write_bytes(blob(args.run1,'deliverables/comparison_matrix.csv'))
(SITE/'downloads/projects.csv').write_bytes(blob(args.run1,'data/projects.csv'))
paths = subprocess.check_output(['git','ls-tree','-r','--name-only',args.run1],cwd=ROOT,text=True).splitlines()
selected = [p for p in paths if p.endswith('.md') or p.startswith('pipeline/') and p.endswith(('.py','.sql','.yaml')) or p in ['requirements.txt','data/projects.csv','deliverables/comparison_matrix.csv']]
# Fixed timestamps make regeneration deterministic.
with zipfile.ZipFile(SITE/'downloads/source-reference.zip','w',zipfile.ZIP_DEFLATED) as z:
    def put(name, content):
        info=zipfile.ZipInfo(name,(2026,9,26,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,content)
    put('READ_ME.txt', f'Public repository source snapshots, not a runnable data backup.\nRun 1: {args.run1}\nRun 2: {args.run2}\nRun 2 stages 6-8 are incomplete. The run2 README still says not pushed; its STATUS.md and published branch take precedence.\nNo secrets, .git, raw corpus, database binary or full intermediate dataset included.\n'.encode())
    for p in selected:
        put('run1/'+p,blob(args.run1,p))
    run2_paths = set(subprocess.check_output(['git','ls-tree','-r','--name-only',args.run2],cwd=ROOT,text=True).splitlines())
    for p in ['STATUS.md','deliverables/curation_report.md','pipeline/curate.py','pipeline/collect_arxiv_openalex.py','graphs/top_pis.csv','graphs/top_institutions.csv']:
        if p in run2_paths:
            put('run2/'+p,blob(args.run2,p))
print(json.dumps({'run1':data['run1'],'run2':data['run2'],'matrix_cells':len(data['matrix']),'projects':len(data['projects'])},ensure_ascii=False,indent=2))
