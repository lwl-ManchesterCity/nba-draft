import base64,csv,io,json,subprocess,unicodedata,re,collections
from pathlib import Path
root=Path(__file__).resolve().parent.parent
repo='https://api.github.com/repos/meharpalbasi/NBA_Lineup202324_Analyzer/git/blobs/'
shas={2025:('8f1aa5101eaa4578569efbc983b739e7994400e0','1dab287a2596e5eeaf0fd4ab09418871a66df30c'),2026:('da844d4fd2186070bc182ef4c58def65456aa8ed','0ce2af8fa02138142e4ed2cf278601394b9c1c94')}
def get(sha):
 raw=subprocess.check_output(['curl','-fsSL','--max-time','60',repo+sha]);return list(csv.DictReader(io.StringIO(base64.b64decode(json.loads(raw)['content']).decode())))
def norm(s):return re.sub('[^a-z0-9]','',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower())
data={y:(get(a),get(b)) for y,(a,b) in shas.items()};players=json.loads((root/'src/data/nba-players.json').read_text())['players'];names=collections.Counter(norm(p['name']) for p in players);out={};counts=collections.Counter();nba_ids=collections.defaultdict(set)
for track,defense in data.values():
 for r in track:
  if r.get('PLAYER_NAME') and r.get('PLAYER_ID'):nba_ids[norm(r['PLAYER_NAME'])].add(str(int(float(r['PLAYER_ID']))))
 for r in defense:
  if r.get('PLAYER_NAME') and r.get('CLOSE_DEF_PERSON_ID'):nba_ids[norm(r['PLAYER_NAME'])].add(str(int(float(r['CLOSE_DEF_PERSON_ID']))))
for p in players:
 name=norm(p['name']);rec={};weights={x['season']:x['weight'] for x in p['weights']};results={'drive':[],'perimeter':[],'defense':[],'potential':[]}
 if names[name]!=1 or len(nba_ids[name])!=1:counts['ambiguous']+=1;continue
 for year,w in weights.items():
  t,d=data[year];actual=next((x for x in p['seasons'] if x['season']==f'{year-1}-{str(year)[-2:]}'),None)
  if not actual:continue
  rs=[r for r in t if norm(r['PLAYER_NAME'])==name and r['SEASON_TYPE']=='Regular Season' and r['PT_MEASURE_TYPE']=='Drives'];ids={r['PLAYER_ID'] for r in rs};
  if len(ids)==1 and rs and abs(sum(float(r['GP']) for r in rs)-actual['gp'])<=1:
   try:
    drives=sum(float(r['DRIVES']) for r in rs);pts=sum(float(r['DRIVE_PTS']) for r in rs)
    if drives>=50:results['drive'].append((w,pts/drives,year,drives))
   except (ValueError,KeyError):pass
  passing=[r for r in t if norm(r['PLAYER_NAME'])==name and r['SEASON_TYPE']=='Regular Season' and r['PT_MEASURE_TYPE']=='Passing']
  if passing and len({r['PLAYER_ID'] for r in passing})==1 and abs(sum(float(r['GP']) for r in passing)-actual['gp'])<=1:
   try:
    mins=sum(float(r['MIN']) for r in passing);potential=sum(float(r['POTENTIAL_AST']) for r in passing)
    if mins>=300:results['potential'].append((w,potential*36/mins,year,mins))
   except (ValueError,KeyError):pass
  for key,category,attempt,diff in [('perimeter','3 Pointers','FG3A','PLUSMINUS'),('defense','Overall','D_FGA','PCT_PLUSMINUS')]:
   rs=[r for r in d if norm(r['PLAYER_NAME'])==name and r['SEASON_TYPE']=='Regular Season' and r['DEFENSE_CATEGORY']==category]
   if len(rs)!=1 or abs(float(rs[0]['GP'])-actual['gp'])>1:continue
   try:
    n=float(rs[0][attempt]);v=float(rs[0][diff]);
    if n>=50:results[key].append((w,-v,year,n))
   except (ValueError,KeyError):pass
 for k,arr in results.items():
  if arr:rec[k+'Metric']=sum(w*v for w,v,y,n in arr)/sum(w for w,v,y,n in arr);rec[k+'Samples']=[{'season':y,'sample':n,'sourceWeight':w} for w,v,y,n in arr];rec['nbaId']=next(iter(nba_ids[name]));counts[k]+=1
 if rec:out[str(p['id'])]=rec
(root/'src/data/external-tracking-2024-26.json').write_text(json.dumps({'source':'NBA stats mirror: NBA_Lineup202324_Analyzer','coverage':dict(counts),'players':out},ensure_ascii=False,indent=2));print(dict(counts),len(players))
