// Checks the app's physics and the shared database. Run: node tests/validate.js
const fs=require('fs'),path=require('path'),root=path.join(__dirname,'..');
const html=fs.readFileSync(path.join(root,'index.html'),'utf8');
const core=html.split('/*CORE-START*/')[1].split('/*CORE-END*/')[0];
const T=new Function(core+';return {selfTest,ROCKS,MATERIALS,lawFromJson,lawToJson,checkLaw}')();
// 0. the copy embedded in index.html must match the data files (run: python3 tools/build.py)
const emb=JSON.stringify(T.ROCKS.filter(k=>k.id!=='custom').map(T.lawToJson)),file=JSON.stringify(JSON.parse(fs.readFileSync(path.join(root,'data/flowlaws.json'),'utf8')).laws.map(T.lawFromJson).map(T.lawToJson));
const stale=emb!==file;
let fail=0;const bad=m=>{console.error('FAIL  '+m);fail++;};
// 1. database files
const laws=JSON.parse(fs.readFileSync(path.join(root,'data/flowlaws.json'),'utf8')).laws.map(T.lawFromJson),ids=new Set();
for(const k of laws){for(const e of T.checkLaw(k))bad(`flow law "${k.name||k.id}": ${e}`);if(ids.has(k.id))bad(`flow law id "${k.id}" is used twice`);ids.add(k.id);}
const mats=JSON.parse(fs.readFileSync(path.join(root,'data/materials.json'),'utf8')).materials,mids=new Set();
for(const m of mats){if(!m.id||!m.name)bad('material needs an id and a name');if(mids.has(m.id))bad(`material id "${m.id}" is used twice`);mids.add(m.id);
  if(!(m.rho>0))bad(`material "${m.name}": density must be positive`);if(m.kind==='viscous'&&!(m.eta0>=0&&m.n>0&&m.e0>0))bad(`material "${m.name}": n and e0 must be positive, eta0 must not be negative`);if(!['viscous','granular'].includes(m.kind))bad(`material "${m.name}": kind must be viscous or granular`);}
// 2. physics, run on the database laws
const cu=T.ROCKS.find(k=>k.id==='custom');T.ROCKS.length=0;T.ROCKS.push(...laws,cu);
const t=T.selfTest();for(const x of t)if(!x.pass)bad(`${x.group}: ${x.name} (got ${x.got}, expected ${x.exp})`);
if(stale)console.log('NOTE  index.html embeds an older copy of data/flowlaws.json. The live site reads the data file; run python3 tools/build.py to refresh the offline copy.');
console.log(`${laws.length} flow laws, ${mats.length} materials, ${t.length} physics tests, ${fail} failures`);process.exit(fail?1:0);
