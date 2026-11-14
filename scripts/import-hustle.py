import json,subprocess,tempfile,collections,re,unicodedata
from pathlib import Path
import pyarrow.parquet as pq
root=Path(__file__).resolve().parent.parent
urls={2025:'https://api.github.com/repos/sportsdataverse/sportsdataverse-data/releases/assets/601104792',2026:'https://api.github.com/repos/sportsdataverse/sportsdataverse-data/releases/assets/601105479'}
def norm(x):return re.sub('[^a-z0-9]','',unicodedata.normalize('NFKD',x).encode('ascii','ignore').decode().lower())
rows=[]
for year,url in urls.items():
 with tempfile.NamedTemporaryFile(suffix='.parquet') as f:
  f.write(subprocess.check_output(['curl','-fsSL','--max-time','60','-H','Accept: application/octet-stream',url]));f.flush();rows+=pq.read_table(f.name).to_pylist()
data=json.loads((root/'src/data/nba-players.json').read_text());names=collections.Counter(norm(p['name']) for p in data['players']);ids=collections.defaultdict(set)
for r in rows:ids[norm(r['player_name'])].add(r['player_id'])
out={};counts=collections.Counter();fields=['contested_shots','contested_shots_2_pt','contested_shots_3_pt','deflections','screen_assists','screen_ast_pts','loose_balls_recovered','off_boxouts','def_boxouts']
for p in data['players']:
 n=norm(p['name']);weights={w['season']:w['weight'] for w in p['weights']};season_results=[]
 if names[n]!=1 or len(ids[n])!=1:continue
 for y,w in weights.items():
  rr=[r for r in rows if norm(r['player_name'])==n and r['season']==y];actual=next((s for s in p['seasons'] if s['season']==f'{y-1}-{str(y)[-2:]}'),None)
  if not rr or not actual:continue
  gp=sum(r['g'] for r in rr);minutes=sum(r['min'] for r in rr)
  if abs(gp-actual['gp'])>1 or gp<20 or minutes<=0:continue
  values={k:sum(r[k] for r in rr if r[k] is not None)*36/minutes for k in fields};season_results.append((w,y,gp,minutes,values))
 if not season_results:continue
 rec={'hustleSamples':[{'season':y,'gp':gp,'minutes':minutes} for _,y,gp,minutes,_ in season_results]}
 for k in fields:rec['hustle_'+k]=sum(w*v[k] for w,_,_,_,v in season_results)/sum(w for w,*_ in season_results)
 out[str(p['id'])]=rec;counts['matched']+=1
(root/'src/data/hustle-2024-26.json').write_text(json.dumps({'source':'NBA hustle via sportsdataverse','coverage':dict(counts),'players':out},ensure_ascii=False,indent=2));print(dict(counts),'/',len(data['players']))
