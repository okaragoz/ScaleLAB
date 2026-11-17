import json,sys
from playwright.sync_api import sync_playwright
JS=r"""
async()=>{
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const log=[],errs=[];let step='init';
window.addEventListener('error',e=>errs.push(step+' :: '+(e.message||e)));
window.addEventListener('unhandledrejection',e=>errs.push(step+' :: rejection '+e.reason));
const base=JSON.stringify(S);
const reset=()=>{S=hydrate(JSON.parse(base));renderLayers();renderBodies();fillStatic();update();};
const res=document.querySelector('.results')||document.body;
const bad=()=>{const t=document.body.innerText.replace(/or undefined layer/g,'');let m=t.match(/.{0,60}(NaN|undefined|Infinity|\[object).{0,30}/);if(m)return m[0].replace(/\s+/g,' ');for(const g of document.querySelectorAll('svg')){const h=g.outerHTML,q=h.match(/.{0,50}(NaN|undefined|Infinity).{0,20}/);if(q)return 'SVG '+g.parentElement.id+': '+q[0];}return '';};
const key=e=>e.dataset.k||(e.dataset.hm!=null?'hm:'+e.dataset.hm:'')||(e.dataset.logk?'logk:'+e.dataset.logk:'')||(e.dataset.take?'take:'+e.dataset.take:'')||('#'+e.id);
const find=(k,type)=>[...document.querySelectorAll('input,select')].find(e=>key(e)===k&&(!type||e.type===type));
const fire=(e,v)=>{if(e.type==='checkbox'){e.checked=v;}else e.value=v;e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}));};
reset();await sleep(100);
const base0=bad();if(base0)log.push(['BASELINE','',base0]);
const items=[...document.querySelectorAll('input,select')].filter(e=>!e.closest('dialog')&&!['libQ','matQ','expSel'].includes(e.id)).map(e=>({k:key(e),type:e.type,v:e.value,opts:e.tagName==='SELECT'?[...e.options].map(o=>o.value):null,min:e.min,max:e.max}));
let n=0;const t0=performance.now();
for(const it of items.slice(A,B)){
  let vals;
  if(it.opts)it.opts=it.opts.filter(o=>o!=='__more');if(it.opts)vals=it.opts.length>12?it.opts.filter((o,i)=>i%Math.ceil(it.opts.length/6)===0):it.opts;
  else if(it.type==='checkbox')vals=[true,false];
  else if(it.type==='range')vals=[it.min,it.max,(+it.min+ +it.max)/2];
  else if(/\.name$/.test(it.k))vals=['<b>x</b> & "q"',''];
  else{const x=parseFloat(it.v);vals=isFinite(x)&&x!==0?[String(x*2),String(x/2),String(x*10),String(x/10)]:['1','10'];vals.push('0','-1','','1e30','1e-30');}
  for(const v of vals){step=it.k+' = '+JSON.stringify(v);reset();const e=find(it.k,it.type);if(!e){log.push(['MISSING',step,'']);continue;}
    console.log('STEP '+step);await sleep(1);try{fire(e,v);}catch(x){errs.push(step+' :: throw '+x.message);}await sleep(12);n++;
    const b=bad();if(b)log.push([['0','-1','','abc','1e30','1e-30'].includes(v)?'edge':'SANE',step,b]);}
}
reset();
return{n,errs,log,total:items.length,ms:performance.now()-t0};
}
"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path="/usr/bin/google-chrome",args=["--no-sandbox"])
    pg=b.new_page(viewport={"width":1500,"height":1000});perr=[]
    pg.on("pageerror",lambda e:perr.append(str(e)[:200]));last=[""];pg.on("console",lambda m:(m.text.startswith("STEP") and (open("/tmp/qa/last_"+sys.argv[1]+".txt","w").write(m.text))))
    pg.goto("http://localhost:8765/index.html");pg.wait_for_timeout(1200)
    pg.evaluate("localStorage.clear()");pg.reload();pg.wait_for_timeout(1200)
    A,B=int(sys.argv[1]),int(sys.argv[2]);r=pg.evaluate(JS.replace("slice(A,B)","slice(%d,%d)"%(A,B)));print("items",r["total"],"ms/step",round(r["ms"]/max(1,r["n"])))
    print("steps",r["n"],"errors",len(r["errs"]),"pageerrors",len(perr),"flags",len(r["log"]))
    for e in sorted(set(r["errs"]))[:40]:print("ERR",e)
    for e in sorted(set(perr))[:10]:print("PERR",e)
    seen=set()
    for l in r["log"]:
        k=(l[0],l[1].split(' = ')[0].replace('0.','N.').replace('1.','N.').replace('2.','N.').replace('3.','N.'),l[2][-40:])
        if l[0]=='SANE' or l[0] in('BASELINE','MISSING'):print(l)
    edge=[l for l in r["log"] if l[0]=='edge'];print("edge flags",len(edge))
    for l in edge[:60]:print(l)
    b.close()
