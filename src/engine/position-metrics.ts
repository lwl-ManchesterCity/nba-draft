export type MetricKey='passing'|'ballhandler'|'control'|'scoring'|'shooting'|'efficiency'|'disrupt'|'spot'|'selfcreate'|'offball'|'secondary'|'boards'|'transition'|'perimeterDefense'|'activity'|'insideFinish'|'offBoards'|'defBoards'|'rimDefense'|'contests'|'roll'|'post'|'screen'|'centerPassing'|'steals'|'blocks';
type Component={key:string,weight:number,invert?:boolean};
export type Metric={key:MetricKey,label:string,description:string,components:Component[]};
const one=(key:MetricKey,label:string,description:string,field:string,invert=false):Metric=>({key,label,description,components:[{key:field,weight:1,invert}]});
const none=(key:MetricKey,label:string,description:string):Metric=>({key,label,description,components:[]});
const M:Record<MetricKey,Metric>={
passing:one('passing','组织创造（间接）','当前仅有助攻率；潜在助攻追踪暂缺，无法完整衡量创造机会。','astRatio'),
ballhandler:one('ballhandler','持球挡拆','Synergy 挡拆持球每回合得分；每赛季至少30回合。仅有部分赛季时按可用赛季计算。','ballhandlerPpp'),
control:{key:'control',label:'球权控制',description:'助失比60% + 失误率代理反向40%；不能直接衡量节奏控制。',components:[{key:'astTo',weight:.6},{key:'turnoverRatio',weight:.4,invert:true}]},
scoring:one('scoring','得分产量','双赛季加权场均得分，受上场时间影响。','pts'),
shooting:{key:'shooting',label:'外线投射',description:'每36分钟三分出手55% + 收缩后三分命中率45%；持球和接球投篮目前未分开。',components:[{key:'tpa',weight:.55},{key:'tpShrunk',weight:.45}]},
efficiency:one('efficiency','进攻效率','双赛季加权真实命中率 TS%。','ts'),
disrupt:{key:'disrupt',label:'外线防守干扰',description:'每36分钟传球干扰50% + 三分干扰出手50%；统计动作次数，不等于防守效果。',components:[{key:'hustle_deflections',weight:.5},{key:'hustle_contested_shots_3_pt',weight:.5}]},
spot:one('spot','定点进攻','Synergy 定点进攻每回合得分；每赛季至少30回合，不能单独代表接球三分能力。','spotPpp'),
selfcreate:one('selfcreate','持球得分','单打与持球挡拆合并得分除以回合数；每赛季至少30回合，受战术角色影响。','isoPnrPpp'),
offball:one('offball','动态无球','绕掩护、手递手与空切合计每回合得分；每赛季至少30回合。','offballPpp'),
secondary:one('secondary','次级组织（间接）','当前仅有助攻率；潜在助攻追踪暂缺。','astRatio'),
boards:one('boards','篮板参与','每36分钟篮板；未按篮板机会调整。','reb36'),
transition:one('transition','无球终结','空切与转换进攻合计每回合得分；每赛季至少30回合，转换进攻未必全是无球。','cutTransitionPpp'),
perimeterDefense:one('perimeterDefense','抢断产量','每36分钟抢断次数，只反映抢断产量，不代表整体侧翼防守能力。','stl36'),
steals:one('steals','抢断产量','每36分钟抢断次数，不代表整体防守能力。','stl36'),
blocks:one('blocks','盖帽产量','每36分钟盖帽次数，不等于完整的护框能力。','blk36'),
activity:{key:'activity',label:'防守活跃度',description:'每36分钟传球干扰50% + 争抢球50%；反映动作次数，不等于整体防守。',components:[{key:'hustle_deflections',weight:.5},{key:'hustle_loose_balls_recovered',weight:.5}]},
insideFinish:none('insideFinish','篮下终结','缺少篮下区域出手和命中数据，暂不评分；顺下不等于篮下投篮。'),
offBoards:one('offBoards','进攻篮板','双赛季加权每36分钟进攻篮板数量，未按篮板机会调整。','oreb36'),
defBoards:one('defBoards','防守篮板','双赛季加权每36分钟防守篮板数量，未按篮板机会调整。','dreb36'),
rimDefense:one('rimDefense','篮下防守','篮下常态命中率减实际命中率；每赛季至少20场及50次防守出手，不区分协防与对位。','rimDifferential'),
contests:{key:'contests',label:'防守干扰',description:'每36分钟干扰投篮60% + 传球干扰40%；统计动作次数，不等于防守效果。',components:[{key:'hustle_contested_shots',weight:.6},{key:'hustle_deflections',weight:.4}]},
roll:one('roll','挡拆顺下','Synergy 挡拆顺下每回合得分；每赛季至少30回合。','rollPpp'),
post:one('post','低位进攻','Synergy 低位进攻每回合得分；每赛季至少30回合。','postPpp'),
screen:{key:'screen',label:'掩护贡献',description:'每36分钟掩护助攻50% + 掩护助攻得分50%；没有全部掩护次数，受队友投篮和战术影响。',components:[{key:'hustle_screen_assists',weight:.5},{key:'hustle_screen_ast_pts',weight:.5}]},
centerPassing:one('centerPassing','中锋策应（间接）','当前仅有助攻率；潜在助攻追踪暂缺。','astRatio')};
const configs:MetricKey[][]=[['passing','ballhandler','control','scoring','shooting','efficiency','disrupt','spot'],['scoring','selfcreate','spot','offball','secondary','efficiency','disrupt','boards'],['scoring','selfcreate','shooting','transition','secondary','perimeterDefense','activity','boards'],['scoring','shooting','offBoards','defBoards','rimDefense','contests','secondary','efficiency'],['scoring','offBoards','defBoards','rimDefense','blocks','screen','centerPassing','efficiency']];
export function metricsForPosition(index:number):Metric[]{return (configs[index]??configs[0]).map(k=>M[k])}
function raw(p:any,key:string):number|null {if(!p)return null;let x:number|undefined;switch(key){case 'tpa':x=p.per36?.tpa;break;case 'reb36':x=p.per36?.reb;break;case 'stl36':x=p.per36?.stl;break;case 'blk36':x=p.per36?.blk;break;case 'turnoverRatio':{const load=p.per36?.load;x=load>0?p.tov*36/p.mpg/load:undefined;break}default:x=p[key]}return typeof x==='number'&&Number.isFinite(x)?x:null}
export function metricValue(p:any,key:MetricKey,pool:any[]):number|null{const parts=M[key].components;if(!parts.length)return null;let result=0;for(const part of parts){const val=raw(p,part.key),values=pool.map(q=>raw(q,part.key)).filter((x):x is number=>x!==null);if(val===null||values.length<20)return null;const below=values.filter(x=>x<val).length,equal=values.filter(x=>x===val).length,percent=(below+equal*.5)/values.length*100;result+=part.weight*(part.invert?100-percent:percent)}return result}

const fieldLabels:Record<string,string>={hustle_deflections:'每36分钟传球干扰',hustle_contested_shots_3_pt:'每36分钟三分干扰出手',hustle_contested_shots:'每36分钟干扰出手',hustle_loose_balls_recovered:'每36分钟争抢球',hustle_screen_assists:'每36分钟掩护助攻',hustle_screen_ast_pts:'每36分钟掩护助攻得分',astRatio:'助攻率',astTo:'助失比',turnoverRatio:'失误率估计',pts:'场均得分',tpa:'每36分钟三分出手',tpShrunk:'收缩后三分命中率',ts:'真实命中率',reb36:'每36分钟篮板',oreb36:'每36分钟进攻篮板',dreb36:'每36分钟防守篮板',stl36:'每36分钟抢断',blk36:'每36分钟盖帽',ballhandlerPpp:'挡拆持球每回合得分',isoPnrPpp:'单打与持球挡拆每回合得分',spotPpp:'定点进攻每回合得分',offballPpp:'动态无球每回合得分',cutTransitionPpp:'空切与转换每回合得分',rollPpp:'挡拆顺下每回合得分',postPpp:'低位进攻每回合得分',rimDifferential:'篮下命中率差'};
export function metricSources(p:any,metric:Metric){return metric.components.map(c=>({key:c.key,label:fieldLabels[c.key]??c.key,value:raw(p,c.key),samples:p?.[c.key.startsWith('hustle_')?'hustleSamples':c.key==='rimDifferential'?'rimSamples':c.key.replace(/Ppp$/,'Samples')]}))}
