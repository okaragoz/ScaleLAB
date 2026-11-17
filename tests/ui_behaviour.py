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
            ev("document.querySelector('#bExample').click()");pg.wait_for_timeout(120);ev("S.layers.forEach(L=>{L.lkM=false})");ev(f"SET('model.anchor','{a}')");ev(f"SET('layers.{a}.etaM','{v}')");y0=ev(f"SC().yours[{a}]");pg.click("#bAutofit");pg.wait_for_timeout(120)
            s=ev("({a:S.model.anchor,sc:SC()})");ys=[y for y,br in zip(s['sc']['yours'],s['sc']['br']) if not br]
            ck(f'autofit anchor {a} at {v}: anchor and viscosity kept, range respected',s['a']==a and abs(s['sc']['yours'][a]/y0-1)<1e-9 and ev(f'S.layers[{a}].etaM')==float(v) and min(ys)>=790 and max(ys)<=1.01e5,(s['a'],ys))
            rq=[r for r,br in zip(s['sc']['req'],s['sc']['br']) if not br];ck(f'autofit anchor {a} at {v}: layers keep nature\'s order of stiffness',all((ys[i]-ys[j])*(rq[i]-rq[j])>=-1e-6 for i in range(len(ys)) for j in range(len(ys))),(ys,rq))
    ok_state('autofit matrix')
    # time mode
    ev("document.querySelector('#bExample').click()");pg.wait_for_timeout(120);ev("SET('model.mode','time')");ev("SET('model.myrPerHour','2')");s=ev("SC()");ck('time mode: 1 h = 2 Myr',abs(s['nph']/(2*3.15576e13)-1)<1e-3,s['nph']);pg.click("#bAutofit");pg.wait_for_timeout(120)
    s2=ev("({m:S.model.mode,sc:SC()})");ck('time mode: autofit keeps the chosen time scale',s2['m']=='time' and abs(s2['sc']['nph']/s['nph']-1)<1e-9,s2['m']);ok_state('time mode')
    # scaling relations
    ev("document.querySelector('#bExample').click()");pg.wait_for_timeout(120);a=ev("SC()");ev("SET('layers.3.etaM','40000')");c=ev("SC()")
    ck('anchor viscosity x2 -> all required x2',all(abs(c['req'][i]/a['req'][i]-2)<1e-6 for i in (1,2,3)),c['req']);ck('anchor viscosity x2 -> natural time per lab hour halves',abs(c['nph']/a['nph']-0.5)<1e-6,c['nph']/a['nph'])
    ev("document.querySelector('#bExample').click()");pg.wait_for_timeout(120);h0=ev("S.layers.map(L=>L.h)");ev("SET('model.kmPerCm','40')");c=ev("SC()");h1=ev("S.layers.map(L=>L.h)")
    ck('locked model thickness stays when the length scale changes',all(abs(c['h'][i]/a['h'][i]-1)<1e-9 for i in range(4)),c['h']);ck('...and the natural thickness follows (x2)',all(abs(h1[i]/h0[i]-2)<1e-9 for i in range(4)),h1)
    ev("document.querySelector('#bExample').click()");pg.wait_for_timeout(120);ev("document.querySelector('[data-lock=\"1.lkH\"]').click()");ev("SET('model.kmPerCm','40')");c=ev("SC()");ck('unlocked layer: model thickness halves, locked ones stay',abs(c['h'][1]/a['h'][1]-0.5)<1e-9 and abs(c['h'][2]/a['h'][2]-1)<1e-9,c['h'])
    ck('lock button shows its state',ev("document.querySelector('[data-lock=\"1.lkH\"]').getAttribute('aria-pressed')")=='false' and ev("document.querySelector('[data-lock=\"2.lkH\"]').getAttribute('aria-pressed')")=='true' and ev("document.querySelector('[data-k=\"layers.2.h\"]').disabled") and not ev("document.querySelector('[data-k=\"layers.1.h\"]').disabled"))
    ev("document.querySelector('#bExample').click()");pg.wait_for_timeout(120);z0=ev("GEO.lay[0].z1");ev("SET('hm:3','28')");s=ev("({h:S.layers[3].h,hmax:S.layers[3].hMax,f:document.querySelector('[data-k=\"layers.3.h\"]').value,z:GEO.lay[0].z1,lz:GEO.lay[3].z1-GEO.lay[3].z0})")
    ck('model thickness 28 cm -> 560 km and fields follow',s['h']==560 and s['hmax']==560 and s['f']=='560',s);ck('28 cm layer drawn 28 cm thick, stack rises',abs(s['lz']-28)<1e-6 and abs(s['z']-(z0-20+28))<1e-6,s);ok_state('model thickness')
    ev("document.querySelector('#bExample').click()");pg.wait_for_timeout(120);ev("document.querySelector('[data-lock=\"3.lkH\"]').click()");ev("SET('layers.3.h','450')");ck('asthenosphere thickness changes the drawing',abs(ev("GEO.lay[0].z1")-(z0+2.5))<1e-6,ev("GEO.lay[0].z1"))
    for g in ('hMin','hMax','h'):
        ev(f"SET('ui.geo','{g}')");ok_state('geometry '+g)
    # layer buttons: anchor follows its layer
    ev("document.querySelector('#bExample').click()");pg.wait_for_timeout(120);nm=ev("S.layers[S.model.anchor].name")
    ev("document.querySelector(\"button[data-act=up][data-i='3']\").click()");pg.wait_for_timeout(120);ck('move anchor layer up: anchor follows',ev("S.layers[S.model.anchor].name")==nm and ev("S.model.anchor")==2,ev("S.model.anchor"))
    ev("document.querySelector(\"button[data-act=down][data-i='1']\").click()");pg.wait_for_timeout(120);ck('move another layer past the anchor: anchor follows',ev("S.layers[S.model.anchor].name")==nm and ev("S.model.anchor")==1,ev("S.model.anchor"));ok_state('reorder')
    ev("document.querySelector('#bExample').click()");pg.wait_for_timeout(120);ev("document.querySelector(\"button[data-act=del][data-i='0']\").click()");pg.wait_for_timeout(120);ck('remove layer above anchor: anchor follows',ev("S.layers[S.model.anchor].name")==nm,ev("S.model.anchor"));ok_state('remove')
    for i in range(4):
        pg.click("#bAdd");pg.wait_for_timeout(100)
    ck('add layers up to the limit of six',ev("S.layers.length")==6);ok_state('six layers')
    while ev("S.layers.length")>1:
        ev("document.querySelector(\"button[data-act=del][data-i='0']\").click()");pg.wait_for_timeout(80)
    ok_state('one layer');pg.click("#bAutofit");pg.wait_for_timeout(100);ok_state('one layer autofit')
    # bodies
    ev("document.querySelector('#bExample').click()");pg.wait_for_timeout(120)
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
    ev("document.querySelector('#bExample').click()");pg.wait_for_timeout(120);ev("SET('box.shape','cyl')");ok_state('cylinder box');ev("SET('box.z','5')");ok_state('box too low')
    # every fix / use button that appears, in a few states
    clicked=set()
    for prep in ("0","S.box.z=5","S.layers.forEach(L=>{L.rhoM=1000})","S.layers[2].etaM=10","S.layers[2].ef=50","S.layers.forEach(L=>{L.etaM=0;L.mat='custom'})"):
        for rnd in range(8):
            ev("document.querySelector('#bExample').click()");pg.wait_for_timeout(100);ev("()=>{"+prep+";renderLayers();fillStatic();update();}")
            ids=ev("[...document.querySelectorAll('#results button[data-fix],#results button[data-use]')].map(b=>b.dataset.fix?'F:'+b.dataset.fix:'U:'+b.dataset.use)")
            todo=[i for i in ids if (prep,i) not in clicked]
            if not todo:break
            i=todo[0];clicked.add((prep,i));sel=("#results button[data-fix='%s']" if i[0]=='F' else "#results button[data-use='%s']")%i[2:]
            pg.locator(sel).first.click();pg.wait_for_timeout(150);ok_state(f'fix button {i} (state {prep[:28]})')
    ck('fix buttons exercised',len(clicked)>=5,sorted(set(i for _,i in clicked)))
    # lab-first behaviour
    ev("document.querySelector('#bExample').click()");pg.wait_for_timeout(120)
    ck('example: anchor is the asthenosphere with the 2e4 Pa s base oil, locked',ev("S.model.anchor")==3 and ev("S.layers[3].etaM")==2e4 and ev("S.layers[3].lkM") and abs(ev("SC().yours[3]")-2e4)<1)
    ev("SET('layers.2.etaM','50000')");ck('typing a viscosity locks it',ev("S.layers[2].lkM")==True and ev("document.querySelector('[data-lock=\"2.lkM\"]').getAttribute('aria-pressed')")=='true')
    before=ev("JSON.stringify(S.layers.map(L=>[L.h,L.rhoM]))");pg.click("#bAutofit");pg.wait_for_timeout(150)
    ck('autofit leaves the locked layer, the anchor, thicknesses and densities alone',ev("S.layers[2].etaM")==5e4 and ev("S.layers[3].etaM")==2e4 and ev("S.model.anchor")==3 and ev("JSON.stringify(S.layers.map(L=>[L.h,L.rhoM]))")==before)
    ev("document.querySelector('[data-lock=\"2.lkM\"]').click()");pg.click("#bAutofit");pg.wait_for_timeout(150);s=ev("SC()");ck('after unlocking, autofit fits that layer',abs(s['yours'][2]/s['req'][2]-1)<0.1,(s['yours'][2],s['req'][2]))
    ck('fitted layer uses only lab stock or an own mix',ev("S.layers[2].mat") in ('custom','korasilon_m_20000000_r','silicone_oil_1200'),ev("S.layers[2].mat"))
    ev("S.layers[3].etaM=0;renderLayers();update()");j=ev("JSON.stringify(S)");pg.click("#bAutofit");pg.wait_for_timeout(150);ck('anchor without material: autofit refuses and changes nothing',ev("JSON.stringify(S)")==j and ev("S.model.anchor")==3);ok_state('anchor without material')
    ev("document.querySelector('#bExample').click()");pg.wait_for_timeout(120);ev("SET('layers.1.forceBrittle',true)");s=ev("SC()")
    ck('brittle switch: layer has no required viscosity and its viscosity fields are hidden',s['br'][1] and ev("getComputedStyle(document.querySelector('details.layer[data-li=\"1\"] label.visc')).display")=='none' and 'brittle' in ev("document.querySelectorAll('#results table')[1].rows[2].innerText"),ev("document.querySelectorAll('#results table')[1].rows[2].innerText"));ok_state('brittle switch')
    ev("SET('layers.1.forceBrittle',false)");ck('brittle switch off again',not ev("SC().br[1]") and ev("getComputedStyle(document.querySelector('details.layer[data-li=\"1\"] label.visc')).display")!='none')
    n0=ev("document.querySelector('[data-k=\"layers.1.rock\"]').options.length");ck('flow-law menu is short',n0<=14,n0);ck('material menu is short',ev("document.querySelector('[data-k=\"layers.1.mat\"]').options.length")<=8)
    ev("SET('layers.1.rock','__more')");pg.wait_for_timeout(150);ck('More flow laws opens the search',ev("document.querySelector('#dlgPick').open") and ev("S.layers[1].rock")=='diabase_caristan_1982')
    pg.fill("#pickQ","eclogite jin");pg.wait_for_timeout(100);pg.locator("#pickL button").first.click();pg.wait_for_timeout(150)
    ck('picked flow law is applied and stays in the short menu',ev("S.layers[1].rock")=='eclogite_jin_et_al_2001' and ev("document.querySelector('[data-k=\"layers.1.rock\"]').value")=='eclogite_jin_et_al_2001' and not ev("document.querySelector('#dlgPick').open"));ok_state('flow-law picker')
    ev("SET('layers.2.mat','__more')");pg.wait_for_timeout(150);pg.fill("#pickQ","M 1 000 000");pg.wait_for_timeout(100);pg.locator("#pickL button").first.click();pg.wait_for_timeout(150)
    ck('picked material is applied, locked and added to my lab materials',ev("S.layers[2].mat")=='korasilon_m_1000000' and ev("S.layers[2].lkM") and 'korasilon_m_1000000' in ev("S.inv"));ok_state('material picker')
    ev("document.querySelector('[data-inv=\"korasilon_m_1000000\"]').click()");ck('material removed from my lab materials',('korasilon_m_1000000' not in ev("S.inv")) and ev("S.layers[2].mat")=='korasilon_m_1000000');ok_state('inventory remove')
    ev("document.querySelector('#bExample').click()");pg.wait_for_timeout(150);ck('mixing guide present',"per kg of base fluid" in ev("document.querySelector('#mix').innerText"))
    ev("document.querySelector('#bExample').click()");pg.wait_for_timeout(150);s=ev("SC()");ys=[y for y,b in zip(s['yours'],s['br']) if not b]
    ck('Venus example: every ductile layer between 9e3 and 9e4 Pa s and matching its target',min(ys)>=9e3 and max(ys)<=9e4 and all(abs(y/r-1)<0.02 for y,r,b in zip(s['yours'],s['req'],s['br']) if not b),ys)
    ck('Venus example: stack fits the 25 x 25 x 30 cm box',ev("S.box.x")==25 and ev("S.box.z")==30 and abs(sum(s['h'])*100-23.95)<1e-6,sum(s['h'])*100)
    pg.click("#bFit");pg.wait_for_timeout(1500);nf=ev("[...document.querySelectorAll('#tFit button')].filter(b=>b.textContent==='fits').length");nr=ev("document.querySelector('#tFit').rows.length")
    ck('fit scan: 12 gradients, some combinations fit and some do not',nr==13 and 0<nf<ev("document.querySelectorAll('#tFit button').length"),(nr,nf))
    ev("document.querySelector('#tFit button[data-fit=\"2.0\"]').click()");pg.wait_for_timeout(200);ck('fit scan: clicking a cell applies gradient and thickness',ev("S.nat.G")==12 and ev("S.layers[1].h")==20,(ev("S.nat.G"),ev("S.layers[1].h")));ok_state('fit scan')
    # brittle module
    ev("document.querySelector('#bExample').click()");pg.wait_for_timeout(150);ck('example mantle lid is 39 km thick',ev("S.layers[2].h")==39)
    ck('brittle fields shown only on the brittle layer',ev("getComputedStyle(document.querySelector('details.layer[data-li=\"0\"] .brit')).display")!='none' and ev("getComputedStyle(document.querySelector('details.layer[data-li=\"1\"] .brit')).display")=='none')
    ck('brittle table lists the sand layer',ev("document.querySelector('#tBrit').rows.length")==2 and '33°' in ev("document.querySelector('#tBrit').innerText"),ev("document.querySelector('#tBrit').innerText")[:200])
    ck('engine fields hidden without driven deformation',ev("getComputedStyle(document.querySelector('.tectOnly')).display")=='none')
    for t in ('comp1','comp2','ext1','ext2'):
        ev(f"SET('model.tect','{t}')");ok_state('experiment '+t)
    ck('engine fields shown for a driven experiment',ev("getComputedStyle(document.querySelector('.tectOnly')).display")!='none')
    ev("SET('model.tect','comp2')");ev("SET('model.vWall','500')");ev("document.querySelector('#results button[data-fix=\"vfit\"]').click()");pg.wait_for_timeout(150)
    bd=ev("(()=>{const b=brittleDesign(S,LAST.sc,LAST.res);return{eN:b.eN,e:S.nat.e,v:S.model.vWall,f:document.querySelector('[data-k=\"model.vWall\"]').value}})()")
    ck('Set engine speed matches the reference strain rate and updates the field',abs(bd['eN']/bd['e']-1)<0.01 and float(bd['f'])==bd['v'],bd)
    ev("SET('model.tect','ext1')");ck('extension with compression regime is flagged',ev("!!document.querySelector('#results button[data-fix=\"regfit\"]')"));ev("document.querySelector('#results button[data-fix=\"regfit\"]').click()");pg.wait_for_timeout(150);ck('Set regime switches nature to extension',ev("S.nat.regime")=='0.75' and 'normal' in ev("document.querySelector('#tBrit').innerText"))
    d0=ev("brittleDesign(S,LAST.sc,LAST.res).rows[0].base");ev("SET('layers.0.sat','sat')");d1=ev("brittleDesign(S,LAST.sc,LAST.res).rows[0].base");ck('saturation lowers the brittle strength',d1<d0,(d0,d1))
    ev("SET('layers.0.phiM','25')");ev("SET('layers.0.CM','0')");ck('friction angle and cohesion feed the table','25° · 0 Pa' in ev("document.querySelector('#tBrit').innerText"))
    c0=ev("brittleDesign(S,LAST.sc,LAST.res).cp.Rm");ev("SET('model.couple','detach')");c1=ev("brittleDesign(S,LAST.sc,LAST.res).cp.Rm");ck('basal detachment changes the coupling number',c0!=c1 and 'basal detachment' in ev("document.querySelector('#britChecks').innerText"),(c0,c1));ok_state('brittle module')
    ev("SET('layers.0.mat','beads')");ck('choosing a granular material brings its friction angle and cohesion',ev("S.layers[0].phiM")==22 and ev("S.layers[0].CM")==10)
    # header menu and planet examples
    for k in ('earth','mars','mercury','moon','venus'):
        pg.click("details.mi >> nth=0 >> summary");pg.wait_for_timeout(100);vis=ev("getComputedStyle(document.querySelector('[data-ex=\"%s\"]')).display!=='none' && document.querySelector('details.mi').open"%k)
        pg.click('[data-ex="%s"]'%k);pg.wait_for_timeout(350);s_=ev("SC()");ys=[y for y,b_ in zip(s_['yours'],s_['br']) if not b_]
        ck(k+' example: loads from the menu, menu closes, planet set',vis and not ev("document.querySelector('details.mi').open") and ev("S.nat.planet").lower()==k,ev("S.nat.planet"))
        ck(k+' example: base oil anchor at 2e4 and every ductile layer inside the buildable range',ev("S.model.anchor")==3 and abs(s_['yours'][3]-2e4)<1 and min(ys)>=790 and max(ys)<=1.01e5,ys);ok_state(k+' example')
    pg.click("details.mi >> nth=1 >> summary");pg.wait_for_timeout(100);pg.click('[data-fn="go:Validation"]');pg.wait_for_timeout(300)
    ck('Functions menu opens a folded panel',ev("[...document.querySelectorAll('#results details')].find(d=>d.querySelector('h2')&&d.querySelector('h2').textContent.trim()==='Validation').open"))
    pg.click("details.mi >> nth=1 >> summary");pg.wait_for_timeout(100);pg.click('[data-fn="scan"]');pg.wait_for_timeout(1500);ck('Functions menu runs the fit scan',ev("document.querySelector('#tFit').rows.length")==13)
    pg.click("#bSim");pg.wait_for_timeout(2500);ck('Simulate opens the 2D Stokes preview with a canvas',ev("document.getElementById('slst-section').style.display")=='' and ev("document.querySelectorAll('#slst-panel canvas').length")>=1)
    g=ev("(()=>{const a=document.getElementById('slst-section'),b=[...document.querySelectorAll('#results section.panel')].find(x=>x.querySelector('h2').textContent.trim()==='Model geometry');return{above:!!(a.compareDocumentPosition(b)&Node.DOCUMENT_POSITION_FOLLOWING),hs:a.getBoundingClientRect().height,hg:b.getBoundingClientRect().height,top:a.getBoundingClientRect().top}})()")
    ck('simulation panel sits above Model geometry and is in view',g['above'] and g['top']<400,g);ck('simulation panel is about as tall as Model geometry',0.5<g['hs']/g['hg']<1.6,g)
    t0=ev("(document.getElementById('slst-panel').innerText.match(/Lab: [^\\n]*/)||[document.querySelector('#slst-panel [data-s=stats]').innerText])[0]");pg.locator("#slst-panel button.slst-main").click();pg.wait_for_timeout(4000);t1=ev("(document.getElementById('slst-panel').innerText.match(/Lab: [^\\n]*/)||[document.querySelector('#slst-panel [data-s=stats]').innerText])[0]")
    ck('simulation runs: model time advances',t0!=t1,(t0,t1));pg.locator("#slst-panel button.slst-main").click();ck('simulation runs on a setup with a brittle sand layer',ev("S.layers[0].forceBrittle")==True);ok_state('simulation')
    ck('simulator takes the brittle layer and its strength from ScaleLAB',ev("document.querySelector('#slst-panel [data-s=\"plastic\"]').value")=='brittle' and ev("document.querySelector('#slst-panel [data-s=\"yield\"]').disabled") and float(ev("document.querySelector('#slst-panel [data-s=\"yield\"]').value"))>0,ev("document.querySelector('#slst-panel [data-s=\"yield\"]').value"))
    ck('playback has 0.25x and 0.5x',ev("[...document.querySelector('#slst-panel [data-s=\"speed\"]').options].map(o=>o.value).join()")=='0.25,0.5,1,2,3')
    cv=ev("(()=>{const c=document.querySelector('#slst-panel canvas').getBoundingClientRect();return[c.width,c.height]})()");ck('preview pane height about 495 px (420 plot + axes), width follows the tank shape',480<cv[1]<510 and 0.6<cv[0]/cv[1]<1.0,cv)
    ck('grid has an Extreme option','extreme' in ev("[...document.querySelector('#slst-panel [data-s=\"quality\"]').options].map(o=>o.value)"))
    pg.wait_for_timeout(1500);st=lambda:ev("(document.getElementById('slst-panel').innerText.match(/Lab: [^\\n]*/)||[document.querySelector('#slst-panel [data-s=stats]').innerText])[0]");ck('time has advanced before the example change',not st().startswith('Lab: 0.0 s'),st())
    names0=ev("document.querySelector('#slst-panel [data-s=\"legend\"]').innerText");pg.click("details.mi >> nth=0 >> summary");pg.wait_for_timeout(100);pg.click('[data-ex="moon"]');pg.wait_for_timeout(2500)
    ck('changing the example restarts the simulation from the new setup',st().startswith('Lab: 0.0 s') and ev("ScaleLABStokes.isOpen()"),st())
    ck('example without a body falls back to perturbed interfaces',ev("document.querySelector('#slst-panel [data-s=\"preset\"]').value")=='interface')
    ev("SET('layers.3.rhoM','990')");pg.wait_for_timeout(1500);ck('changing a density restarts it too',st().startswith('Lab: 0.0 s'));ok_state('simulation refresh')
    ev("document.getElementById('slst-hide').click()");pg.wait_for_timeout(200);ck('simulation panel can be hidden again',ev("document.getElementById('slst-section').style.display")=='none')
    pg.click("details.mi >> nth=0 >> summary");pg.wait_for_timeout(100);pg.mouse.click(700,600);pg.wait_for_timeout(100);ck('menu closes on an outside click',not ev("document.querySelector('details.mi').open"))
    ev("document.querySelector('#bExample').click()");pg.wait_for_timeout(200);bd=ev("GEO.bodies[0]");lay=ev("GEO.lay")
    ck('Venus example: eclogite root is centred and hangs from the base of the crust into the mantle lid',ev("S.bodies[0].name")=='Eclogite root' and bd['x']==0 and bd['z']+bd['r']>lay[1]['z0'] and bd['z']-bd['r']>lay[2]['z0'] and bd['z']<lay[1]['z0'],(bd['z'],bd['r'],lay[1]['z0'],lay[2]['z0']))
    # exports
    ev("document.querySelector('#bExample').click()");pg.wait_for_timeout(120)
    for o in ev("[...document.querySelector('#expSel').options].map(o=>o.value)"):
        ev(f"()=>{{const e=document.querySelector('#expSel');e.value='{o}';e.dispatchEvent(new Event('change',{{bubbles:true}}));}}");t=ev("document.querySelector('#expTxt').value")
        ck(f'export {o}: text without NaN/undefined',len(t)>200 and 'NaN' not in t and 'undefined' not in t and 'Infinity' not in t,len(t))
    t=ev("csv()");ck('CSV export',len(t)>200 and 'NaN' not in t and 'undefined' not in t,len(t))
    # copy setup / paste setup round trip
    ev("SET('layers.3.h','180')");ev("document.querySelector('#bSave').click()");pg.wait_for_timeout(150);clip=ev("navigator.clipboard.readText()");before=ev("JSON.stringify(S)")
    ev("document.querySelector('#bExample').click()");pg.wait_for_timeout(100);ev("document.querySelector('#bLoad').click()");pg.fill("#dlgTxt",clip);pg.click("#dlgOk");pg.wait_for_timeout(200)
    ck('copy setup -> paste setup restores the state',ev("S.layers[3].h")==180 and json.loads(ev("JSON.stringify(S)"))==json.loads(before));ok_state('paste setup')
    ev("document.querySelector('#bLoad').click()");pg.fill("#dlgTxt","{not json");pg.click("#dlgOk");pg.wait_for_timeout(150);ck('bad pasted setup is refused without breaking',ev("S.layers[3].h")==180);
    if ev("document.querySelector('#dlg').open"):pg.click("#dlgCancel")
    ok_state('bad paste')
    # persistence
    pg.reload();pg.wait_for_timeout(1000);INST();ck('setup survives a reload',ev("S.layers[3].h")==180);ok_state('reload')
    # libraries
    ev("document.querySelectorAll('details').forEach(d=>d.open=true)");pg.wait_for_timeout(200)
    pg.fill("#libQ","olivine");pg.wait_for_timeout(150);n1=ev("document.querySelector('#tLib')?document.querySelector('#tLib').rows.length:-1");pg.fill("#libQ","zzzz");pg.wait_for_timeout(150);n2=ev("document.querySelector('#tLib')?document.querySelector('#tLib').rows.length:-1");ck('flow-law search filters',n1>3 and n2<=1,(n1,n2));pg.fill("#libQ","")
    pg.fill("#matQ","korasilon");pg.wait_for_timeout(150);n1=ev("document.querySelector('#tMat').rows.length");ck('materials search filters',n1==16,n1);pg.fill("#matQ","");ok_state('libraries')
    # custom law
    pg.click("#bAddLaw");pg.fill("#lawName","Test law");pg.fill("#ldA","1e-3");pg.fill("#ldn","3");pg.fill("#ldE","300");pg.fill("#lfA","1e3");pg.fill("#lfn","1");pg.fill("#lfE","250");pg.click("#lawOk");pg.wait_for_timeout(200);ck('custom law added',ev("S.userLaws.length")==1,ev("document.querySelector('#lawErr').textContent"))
    if ev("document.querySelector('#dlgLaw').open"):pg.click("#lawCancel")
    ok_state('custom law')
    # planets
    for o in ev("[...document.querySelector('#planet').options].map(o=>o.value)"):
        ev(f"()=>{{const e=document.querySelector('#planet');e.value={json.dumps(o)};e.dispatchEvent(new Event('change',{{bubbles:true}}));}}");ok_state('planet '+o)
    # every rock and every material on every layer
    ev("document.querySelector('#bExample').click()");pg.wait_for_timeout(120);ev("S.inv=MATERIALS.map(m=>m.id);S.favR=ROCKS.map(r=>r.id);renderLayers()")
    r=ev("""async()=>{const out=[];const rocks=[...document.querySelector('[data-k="layers.1.rock"]').options].map(o=>o.value).filter(v=>v!=='__more');
      for(const id of rocks){for(const i of [1,3]){SET('layers.'+i+'.rock',id);const b=BAD();const s=SC();if(b||!s.req.every((v,j)=>s.br[j]||v>0&&isFinite(v)))out.push(id+'@'+i+' '+b);}}
      return{n:rocks.length,out};}""");ck(f'all {r["n"]} flow laws on a crust and a mantle layer',not r['out'],r['out'][:4])
    ev("document.querySelector('#bExample').click()");pg.wait_for_timeout(120);ev("S.inv=MATERIALS.map(m=>m.id);renderLayers()")
    r=ev("""async()=>{const out=[];const ms=[...document.querySelector('[data-k="layers.1.mat"]').options].map(o=>o.value).filter(v=>v!=='__more');
      for(const id of ms){for(const i of [0,1,2,3]){SET('layers.'+i+'.mat',id);const b=BAD();if(b)out.push(id+'@'+i+' '+b);}}return{n:ms.length,out};}""");ck(f'all {r["n"]} material choices on every layer',not r['out'],r['out'][:4])
    ck('no script errors in the whole run',not perr,perr[:3])
    b.close()
with sync_playwright() as p:
    try:main(p)
    except Exception as e:print('EXC',str(e)[:300])
f=[x for x in R if not x[0]];print(len(R),'checks,',len(f),'failed')
for x in f:print('FAIL',x[1],'|',x[2])
print('fix ids:',[x[2] for x in R if x[1]=='fix buttons exercised'])
