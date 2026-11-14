import {it,expect} from 'vitest';import {makeEngine} from '../server/synergy.mjs';import data from '../src/data/nba-players.json';
const e=makeEngine(data.players);const base=data.players[0];
it('diagnoses constructed low spacing and rim',()=>{let team=Array.from({length:5},()=>({...base,heightCm:190,tpShrunk:.28,per36:{...base.per36,tpa:.5,blk:.1,reb:4}}));let a=e.analyze(team);expect(a.counts.spacing).toBe(0);expect(a.counts.rim).toBe(0);expect(a.weak.join()).toMatch(/空间拥堵/);expect(a.weak.join()).toMatch(/禁区缺少保护/)});
it('recognizes overloaded creation',()=>{let p=data.players.toSorted((a,b)=>e.measure(b).z.creation-e.measure(a).z.creation)[0];let team=Array.from({length:5},()=>({...p,per36:{...p.per36,load:33},astRatio:.3}));expect(e.analyze(team).weak.join()).toMatch(/球权过载/)});
