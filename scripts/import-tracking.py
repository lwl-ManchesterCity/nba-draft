import json,subprocess,base64,csv,io,unicodedata,re,collections,os,tempfile
from pathlib import Path
import pyarrow.parquet as pq
root=Path(__file__).resolve().parent.parent
api='https://api.github.com/repos/sportsdataverse/sportsdataverse-data/releases/tags/nba_stats_synergy'
def curl(url,binary=False):return subprocess.check_output(['curl','-fsSL','--max-time','60','-H','Accept: application/octet-stream' if binary else 'Accept: application/vnd.github+json',url])
def norm(n):return re.sub('[^a-z0-9]','',unicodedata.normalize('NFKD',n).encode('ascii','ignore').decode().lower())
assets=json.loads(curl(api))['assets'];selected=[a for a in assets if a['name'] in [f'regular-season_{kind}_offensive_totals_{year}.parquet' for kind in ['postup','prrollman','cut','prballhandler','spotup','handoff','offscreen','isolation','transition'] for year in [2025,2026]]]
if len(selected)!=18:raise SystemExit('缺少战术数据文件')
rows=[]
for asset in selected:
 with tempfile.NamedTemporaryFile(suffix='.parquet') as f:
  f.write(curl(asset['url'],True));f.flush();rows.extend(pq.read_table(f.name).to_pylist())
d=json.loads(curl('https://api.github.com/repos/maxhostetter-eng/nba-defensive-shot-tracking-analysis/git/blobs/271cab4cc5b91b4bffddcd433216b59d3db760a3'));defs=list(csv.DictReader(io.StringIO(base64.b64decode(d['content']).decode())))
players=json.loads((root/'src/data/nba-players.json').read_text())['players'];names=collections.Counter(norm(p['name']) for p in players);nba_ids=collections.defaultdict(set)
for r in rows:nba_ids[norm(r['player_name'])].add(r['player_id'])
out={};coverage=collections.Counter()
for p in players:
 n=norm(p['name']);rec={};weights={w['season']:w['weight'] for w in p['weights']}
 if names[n]!=1:continue
 if len(nba_ids[n])==1:
  year_values=[]
  for y,w in weights.items():
   subset=[r for r in rows if norm(r['player_name'])==n and r['season']==y and r['play_type'].lower() in ['postup','prrollman','cut']];total=sum(r['poss'] or 0 for r in subset);pts=sum(r['pts'] or 0 for r in subset)
   if total>=30:year_values.append((w,pts/total,total,y))
  if year_values:
   rec['insidePpp']=sum(w*v for w,v,_,_ in year_values)/sum(w for w,_,_,_ in year_values);rec['insidePossPerGame']=sum(w*k/next(s['gp'] for s in p['seasons'] if s['season']==f'{y-1}-{str(y)[-2:]}') for w,_,k,y in year_values)/sum(w for w,_,_,_ in year_values);rec['insideSamples']=[{'season':y,'possessions':k} for _,_,k,y in year_values];coverage['inside']+=1
  for key,kinds in {'ballhandler':['prballhandler'],'isoPnr':['isolation','prballhandler'],'spot':['spotup'],'offball':['offscreen','handoff','cut'],'cutTransition':['cut','transition'],'roll':['prrollman'],'post':['postup']}.items():
   records=[]
   for y,w in weights.items():
    subset=[r for r in rows if norm(r['player_name'])==n and r['season']==y and r['play_type'].lower() in kinds];poss=sum(r['poss'] or 0 for r in subset);pts=sum(r['pts'] or 0 for r in subset)
    if poss>=30:records.append((w,pts/poss,poss,y))
   if records:
    rec[key+'Ppp']=sum(w*v for w,v,_,_ in records)/sum(w for w,_,_,_ in records);rec[key+'Samples']=[{'season':y,'possessions':poss} for _,_,poss,y in records];coverage[key]+=1
 ds=[]
 for y,w in weights.items():
  q=[r for r in defs if norm(r['player_name'])==n and r['season']==f'{y-1}-{str(y)[-2:]}']
  if len(q)!=1:continue
  r=q[0]
  try:
   gp=float(r['gp']);att=float(r['rim_attempts_defended']);fg=float(r['rim_fg_pct_allowed']);expected=float(r['rim_normal_fg_pct'])
   if gp>=20 and att*gp>=50:ds.append((w,expected-fg,att*gp,y,fg,expected))
  except (ValueError,KeyError):pass
 if ds:rec['rimDifferential']=sum(w*v for w,v,*_ in ds)/sum(w for w,*_ in ds);rec['rimSamples']=[{'season':y,'attempts':round(a),'allowed':fg,'baseline':exp} for _,_,a,y,fg,exp in ds];coverage['rim']+=1
 if rec:out[str(p['id'])]=rec
(root/'src/data/tracking-2024-26.json').write_text(json.dumps({'coverage':dict(coverage),'players':out},ensure_ascii=False,indent=2));print(dict(coverage),'/',len(players))
