import json
from playwright.sync_api import sync_playwright
R=[]
def ck(name,cond,info=''):
    R.append((bool(cond),name,str(info)[:160]));
import traceback
def main(p):
    b=p.chromium.launch(executable_path="/usr/bin/google-chrome",args=["--no-sandbox"])
    ctx=b.new_context(viewport={"width":1500,"height":1000},permissions=["clipboard-read","clipboard-write"])
    pg=ctx.new_page();perr=[]
    pg.on("pageerror",lambda e:perr.append(str(e)[:200]))
    pg.goto("http://localhost:8765/index.html");pg.wait_for_timeout(1000)
    pg.evaluate("localStorage.clear()");pg.reload();pg.wait_for_timeout(1200)
    INST=lambda:pg.evaluate("""()=>{window.BAD=()=>{const t=document.body.innerText.replace(/or undefined layer/g,'');let m=t.match(/.{0,60}(NaN|undefined|Infinity|\\[object).{0,30}/);if(m)return m[0].replace(/\\s+/g,' ');for(const g of document.querySelectorAll('svg')){const q=g.outerHTML.match(/.{0,50}(NaN|undefined|Infinity).{0,20}/);if(q)return 'SVG '+g.parentElement.id+': '+q[0];}return '';};
      window.SET=(k,v)=>{const e=[...document.querySelectorAll('input,select')].find(e=>(e.dataset.k===k||('hm:'+e.dataset.hm)===k)&&e.type!=='range');if(!e)throw new Error('no field '+k);if(e.type==='checkbox')e.checked=v;else e.value=v;e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}));};
      window.SC=()=>{const res=runAll(S),sc=scaleModel(S,res);return{req:sc.layers.map(l=>l.req),yours:sc.layers.map(l=>l.yours),h:sc.layers.map(l=>l.h),nph:sc.natPerHour,tS:sc.tS,br:res.ref.layers.map(l=>l.allBrittle)};};}""")
    INST()
    ev=pg.evaluate
    def ok_state(tag):
        bad=ev("BAD()");ck(tag+': page clean',not bad and not perr,bad or perr[:1]);perr.clear()
    # --- the user's sequence through the real controls
    ev("SET('model.anchor','3')");ev("SET('layers.3.etaM','1e4')");y0=ev("SC().yours[3]");pg.click("#bAutofit");pg.wait_for_timeout(200)
    s=ev("({a:S.model.anchor,e:S.layers.map(L=>L.etaM),sc:SC(),sel:document.querySelector('[data-k=\"model.anchor\"]').value})")
    ck('user flow: anchor stays on asthenosphere',s['a']==3 and s['sel']=='3',s['a']);ck('user flow: anchor viscosity unchanged by autofit (typed 1e4 at 25 C)',abs(s['sc']['yours'][3]-y0)<1e-6 and ev('S.layers[3].etaM')==1e4,(y0,s['sc']['yours']))
    ck('user flow: all ductile layers within 1e3..8e4',all(800<=y<=1.01e5 for y,br in zip(s['sc']['yours'],s['sc']['br']) if not br),s['sc']['yours']);ok_state('user flow')
    pg.click("#bAutofit");pg.wait_for_timeout(150);s2=ev("({a:S.model.anchor,e:S.layers.map(L=>L.etaM)})");ck('autofit twice gives the same result',s2['e']==s['e'] and s2['a']==3,s2)
    # autofit with each ductile layer as anchor at several viscosities
    for a in (1,2,3):
        for v in ('1500','1e4','7e4'):
            pg.click("#bExample");pg.wait_for_timeout(120);ev(f"SET('model.anchor','{a}')");ev(f"SET('layers.{a}.etaM','{v}')");y0=ev(f"SC().yours[{a}]");pg.click("#bAutofit");pg.wait_for_timeout(120)
            s=ev("({a:S.model.anchor,sc:SC()})");ys=[y for y,br in zip(s['sc']['yours'],s['sc']['br']) if not br]
            ck(f'autofit anchor {a} at {v}: anchor and viscosity kept, range respected',s['a']==a and abs(s['sc']['yours'][a]/y0-1)<1e-9 and ev(f'S.layers[{a}].etaM')==float(v) and min(ys)>=790 and max(ys)<=1.01e5,(s['a'],ys))
            ck(f'autofit anchor {a} at {v}: stiffness order kept',all(ys[i]>=ys[i+1]*0.999 for i in range(len(ys)-1)),ys)
    ok_state('autofit matrix')
    # time mode
    pg.click("#bExample");pg.wait_for_timeout(120);ev("SET('model.mode','time')");ev("SET('model.myrPerHour','2')");s=ev("SC()");ck('time mode: 1 h = 2 Myr',abs(s['nph']/(2*3.15576e13)-1)<1e-3,s['nph']);pg.click("#bAutofit");pg.wait_for_timeout(120)
    s2=ev("({m:S.model.mode,sc:SC()})");ck('time mode: autofit keeps the chosen time scale',s2['m']=='time' and abs(s2['sc']['nph']/s['nph']-1)<1e-9,s2['m']);ok_state('time mode')
    # scaling relations
    pg.click("#bExample");pg.wait_for_timeout(120);a=ev("SC()");ev("SET('layers.1.etaM','160000')");c=ev("SC()")
    ck('anchor viscosity x2 -> all required x2',all(abs(c['req'][i]/a['req'][i]-2)<1e-6 for i in (1,2,3)),c['req']);ck('anchor viscosity x2 -> natural time per lab hour halves',abs(c['nph']/a['nph']-0.5)<1e-6,c['nph']/a['nph'])
    pg.click("#bExample");pg.wait_for_timeout(120);ev("SET('model.kmPerCm','40')");c=ev("SC()");ck('length scale x2 -> model thickness halves',all(abs(c['h'][i]/a['h'][i]-0.5)<1e-9 for i in range(4)),c['h'])
    pg.click("#bExample");pg.wait_for_timeout(120);z0=ev("GEO.lay[0].z1");ev("SET('hm:3','28')");s=ev("({h:S.layers[3].h,hmax:S.layers[3].hMax,f:document.querySelector('[data-k=\"layers.3.h\"]').value,z:GEO.lay[0].z1,lz:GEO.lay[3].z1-GEO.lay[3].z0})")
    ck('model thickness 28 cm -> 560 km and fields follow',s['h']==560 and s['hmax']==560 and s['f']=='560',s);ck('28 cm layer drawn 28 cm thick, stack rises',abs(s['lz']-28)<1e-6 and abs(s['z']-(z0-7.5+28))<1e-6,s);ok_state('model thickness')
    pg.click("#bExample");pg.wait_for_timeout(120);ev("SET('layers.3.h','200')");ck('asthenosphere thickness changes the drawing',abs(ev("GEO.lay[0].z1")-(z0+2.5))<1e-6,ev("GEO.lay[0].z1"))
    for g in ('hMin','hMax','h'):
        ev(f"SET('ui.geo','{g}')");ok_state('geometry '+g)
    # layer buttons: anchor follows its layer
    pg.click("#bExample");pg.wait_for_timeout(120);nm=ev("S.layers[S.model.anchor].name")
    ev("document.querySelector(\"button[data-act=down][data-i='1']\").click()");pg.wait_for_timeout(120);ck('move anchor layer down: anchor follows',ev("S.layers[S.model.anchor].name")==nm and ev("S.model.anchor")==2,ev("S.model.anchor"))
    ev("document.querySelector(\"button[data-act=up][data-i='2']\").click()");pg.wait_for_timeout(120);ev("document.querySelector(\"button[data-act=up][data-i='1']\").click()");pg.wait_for_timeout(120);ck('move anchor layer up twice: anchor follows',ev("S.layers[S.model.anchor].name")==nm and ev("S.model.anchor")==0,ev("S.model.anchor"));ok_state('reorder')
    pg.click("#bExample");pg.wait_for_timeout(120);ev("document.querySelector(\"button[data-act=del][data-i='0']\").click()");pg.wait_for_timeout(120);ck('remove layer above anchor: anchor follows',ev("S.layers[S.model.anchor].name")==nm,ev("S.model.anchor"));ok_state('remove')
    for i in range(4):
        pg.click("#bAdd");pg.wait_for_timeout(100)
    ck('add layers up to the limit of six',ev("S.layers.length")==6);ok_state('six layers')
    while ev("S.layers.length")>1:
        ev("document.querySelector(\"button[data-act=del][data-i='0']\").click()");pg.wait_for_timeout(80)
    ok_state('one layer');pg.click("#bAutofit");pg.wait_for_timeout(100);ok_state('one layer autofit')
    # bodies
    pg.click("#bExample");pg.wait_for_timeout(120)
    for i in range(6):pg.click("#bAddBody");pg.wait_for_timeout(60)
    ck('bodies limited to six',ev("S.bodies.length")==6);ok_state('six bodies')
    for sh in ('cyl','box','sphere'):
        ev(f"SET('bodies.0.shape','{sh}')");ok_state('body shape '+sh)
    for zr in ('floor','top'):
        ev(f"SET('bodies.0.zref','{zr}')");ok_state('body zref '+zr)
    ev("SET('bodies.0.Tb','60')");ev("SET('bodies.0.alpha','9.4e-4')");ev("SET('bodies.0.EaB','15.5')");ok_state('warm body');ev("SET('bodies.0.fed',true)");ok_state('fed body')
    while ev("S.bodies.length")>0:
        ev("document.querySelector(\"button[data-bdel='0']\").click()");pg.wait_for_timeout(60)
    ok_state('no bodies')
    # box shapes
    pg.click("#bExample");pg.wait_for_timeout(120);ev("SET('box.shape','cyl')");ok_state('cylinder box');ev("SET('box.z','5')");ok_state('box too low')
    # every fix / use button that appears, in a few states
    clicked=set()
    for prep in ("0","S.box.z=5","S.layers.forEach(L=>{L.rhoM=1000})","S.layers[2].etaM=10","S.layers[2].ef=50","S.layers.forEach(L=>{L.etaM=0;L.mat='custom'})"):
        for rnd in range(8):
            pg.click("#bExample");pg.wait_for_timeout(100);ev("()=>{"+prep+";renderLayers();fillStatic();update();}")
            ids=ev("[...document.querySelectorAll('#results button[data-fix],#results button[data-use]')].map(b=>b.dataset.fix?'F:'+b.dataset.fix:'U:'+b.dataset.use)")
            todo=[i for i in ids if (prep,i) not in clicked]
            if not todo:break
            i=todo[0];clicked.add((prep,i));sel=("#results button[data-fix='%s']" if i[0]=='F' else "#results button[data-use='%s']")%i[2:]
            pg.locator(sel).first.click();pg.wait_for_timeout(150);ok_state(f'fix button {i} (state {prep[:28]})')
    ck('fix buttons exercised',len(clicked)>=5,sorted(set(i for _,i in clicked)))
    # exports
    pg.click("#bExample");pg.wait_for_timeout(120)
    for o in ev("[...document.querySelector('#expSel').options].map(o=>o.value)"):
        ev(f"()=>{{const e=document.querySelector('#expSel');e.value='{o}';e.dispatchEvent(new Event('change',{{bubbles:true}}));}}");t=ev("document.querySelector('#expTxt').value")
        ck(f'export {o}: text without NaN/undefined',len(t)>200 and 'NaN' not in t and 'undefined' not in t and 'Infinity' not in t,len(t))
    t=ev("csv()");ck('CSV export',len(t)>200 and 'NaN' not in t and 'undefined' not in t,len(t))
    # copy setup / paste setup round trip
    ev("SET('layers.3.h','180')");pg.click("#bSave");pg.wait_for_timeout(150);clip=ev("navigator.clipboard.readText()");before=ev("JSON.stringify(S)")
    pg.click("#bExample");pg.wait_for_timeout(100);pg.click("#bLoad");pg.fill("#dlgTxt",clip);pg.click("#dlgOk");pg.wait_for_timeout(200)
    ck('copy setup -> paste setup restores the state',ev("S.layers[3].h")==180 and json.loads(ev("JSON.stringify(S)"))==json.loads(before));ok_state('paste setup')
    pg.click("#bLoad");pg.fill("#dlgTxt","{not json");pg.click("#dlgOk");pg.wait_for_timeout(150);ck('bad pasted setup is refused without breaking',ev("S.layers[3].h")==180);
    if ev("document.querySelector('#dlg').open"):pg.click("#dlgCancel")
    ok_state('bad paste')
    # persistence
    pg.reload();pg.wait_for_timeout(1000);INST();ck('setup survives a reload',ev("S.layers[3].h")==180);ok_state('reload')
    # libraries
    ev("document.querySelectorAll('details').forEach(d=>d.open=true)");pg.wait_for_timeout(200)
    pg.fill("#libQ","olivine");pg.wait_for_timeout(150);n1=ev("document.querySelector('#tLib')?document.querySelector('#tLib').rows.length:-1");pg.fill("#libQ","zzzz");pg.wait_for_timeout(150);n2=ev("document.querySelector('#tLib')?document.querySelector('#tLib').rows.length:-1");ck('flow-law search filters',n1>3 and n2<=1,(n1,n2));pg.fill("#libQ","")
    pg.fill("#matQ","korasilon");pg.wait_for_timeout(150);n1=ev("document.querySelector('#tMat').rows.length");ck('materials search filters',n1==15,n1);pg.fill("#matQ","");ok_state('libraries')
    # custom law
    pg.click("#bAddLaw");pg.fill("#lawName","Test law");pg.fill("#ldA","1e-3");pg.fill("#ldn","3");pg.fill("#ldE","300");pg.fill("#lfA","1e3");pg.fill("#lfn","1");pg.fill("#lfE","250");pg.click("#lawOk");pg.wait_for_timeout(200);ck('custom law added',ev("S.userLaws.length")==1,ev("document.querySelector('#lawErr').textContent"))
    if ev("document.querySelector('#dlgLaw').open"):pg.click("#lawCancel")
    ok_state('custom law')
    # planets
    for o in ev("[...document.querySelector('#planet').options].map(o=>o.value)"):
        ev(f"()=>{{const e=document.querySelector('#planet');e.value={json.dumps(o)};e.dispatchEvent(new Event('change',{{bubbles:true}}));}}");ok_state('planet '+o)
    # every rock and every material on every layer
    pg.click("#bExample");pg.wait_for_timeout(120)
    r=ev("""async()=>{const out=[];const rocks=[...document.querySelector('[data-k="layers.1.rock"]').options].map(o=>o.value);
      for(const id of rocks){for(const i of [1,3]){SET('layers.'+i+'.rock',id);const b=BAD();const s=SC();if(b||!s.req.every((v,j)=>s.br[j]||v>0&&isFinite(v)))out.push(id+'@'+i+' '+b);}}
      return{n:rocks.length,out};}""");ck(f'all {r["n"]} flow laws on a crust and a mantle layer',not r['out'],r['out'][:4])
    pg.click("#bExample");pg.wait_for_timeout(120)
    r=ev("""async()=>{const out=[];const ms=[...document.querySelector('[data-k="layers.1.mat"]').options].map(o=>o.value);
      for(const id of ms){for(const i of [0,1,2,3]){SET('layers.'+i+'.mat',id);const b=BAD();if(b)out.push(id+'@'+i+' '+b);}}return{n:ms.length,out};}""");ck(f'all {r["n"]} material choices on every layer',not r['out'],r['out'][:4])
    ck('no script errors in the whole run',not perr,perr[:3])
    b.close()
with sync_playwright() as p:
    try:main(p)
    except Exception as e:print('EXC',str(e)[:300])
f=[x for x in R if not x[0]];print(len(R),'checks,',len(f),'failed')
for x in f:print('FAIL',x[1],'|',x[2])
print('fix ids:',[x[2] for x in R if x[1]=='fix buttons exercised'])
