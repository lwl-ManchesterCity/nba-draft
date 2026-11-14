import subprocess,json,base64,csv,io,unicodedata,re,collections,pathlib
root=pathlib.Path(__file__).resolve().parent.parent
sources={'bpm':'https://api.github.com/repos/gh1sung/nba-chemistry/contents/data/bpm_2024_25.csv','defense':'https://api.github.com/repos/maxhostetter-eng/nba-defensive-shot-tracking-analysis/git/blobs/271cab4cc5b91b4bffddcd433216b59d3db760a3'}
def read(url):
 data=json.loads(subprocess.check_output(['curl','-fsSL','--max-time','30',url]))
 return list(csv.DictReader(io.StringIO(base64.b64decode(data['content']).decode('utf-8-sig'))))
def norm(s):return re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower())
players=json.loads((root/'src/data/nba-players.json').read_text())['players'];source={k:read(v) for k,v in sources.items()};out={}; counts=collections.Counter()
for p in players:
 record={}
 for kind in sources:
  rows=[r for r in source[kind] if norm(r['PLAYER_NAME' if kind=='bpm' else 'player_name'])==norm(p['name']) and (kind=='bpm' or r['season']=='2024-25')]
  # Prefer season-total row, then require season games to agree.
  if kind=='bpm':
   totals=[r for r in rows if re.fullmatch(r'\d+TM',r['TEAM'])]
   if totals:rows=totals
  rows=[r for r in rows if abs(float(r['GP' if kind=='bpm' else 'gp'])-p['gp'])<=1]
  if len(rows)!=1:continue
  try:
   if kind=='bpm': record['bpm']=float(rows[0]['BPM'])
   else:
    record['defendedFgPct']=float(rows[0]['opp_fg_pct']);record['defendedAttemptsPerGame']=float(rows[0]['shots_defended']);record['defenseGames']=int(rows[0]['gp'])
   counts[kind]+=1
  except (ValueError,KeyError):continue
 if record:out[str(p['id'])]=record
(root/'src/data/advanced-2024-25.json').write_text(json.dumps({'season':'2024-25','sources':sources,'matched':dict(counts),'players':out},ensure_ascii=False,indent=2))
print('matches',dict(counts),'/',len(players))
