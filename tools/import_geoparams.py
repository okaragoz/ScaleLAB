#!/usr/bin/env python3
"""Import the creep-law database of GeoParams.jl (MIT licence) into data/flowlaws.json.
Usage: python3 tools/import_geoparams.py /path/to/GeoParams.jl
Units written: A in MPa^-n um^p s^-1, E in kJ/mol, V in cm3/mol, Peierls stress in MPa."""
import re, sys, json, math, os, subprocess
src = sys.argv[1]; D = os.path.join(src, 'src/CreepLaw/Data')
def ev(expr, units):
    e = expr.split('#')[0].strip().rstrip(',').strip()
    if e.startswith('uconvert('):            # uconvert(target, value) -> value
        depth = 0
        for i, c in enumerate(e):
            if c == '(': depth += 1
            elif c == ')': depth -= 1
            elif c == ',' and depth == 1: e = e[i+1:-1].strip(); break
    e = e.replace('exp10(', 'EXPTEN(').replace('NoUnits', '').replace('//', '/').replace('^', '**').replace('μ', 'u')
    e = re.sub(r'(?<![A-Za-z_\d.])(\d+\.?\d*(?:[eE][+-]?\d+)?)(?![eE][+-]?\d)(?![\d.])\s*(?=[A-Za-z(])', r'\1*', e)
    e = re.sub(r'\)\s*(?=[A-Za-z])', ')*', e)
    env = dict(units); env.update(EXPTEN=lambda x: 10**x, exp=math.exp, sqrt=math.sqrt, log=math.log)
    if e.endswith('*'): e = e[:-1]
    return float(eval(e, {'__builtins__': {}}, env))
UA = dict(MPa=1.0, Pa=1e-6, GPa=1e3, kPa=1e-3, um=1.0, m=1e6, mm=1e3, s=1.0)
UE = dict(kJ=1.0, J=1e-3, mol=1.0)
UV = dict(m=100.0, cm=1.0, mol=1.0)
UN = dict()
APP = {'AxialCompression': 'axial', 'SimpleShear': 'shear', 'Invariant': 'none'}
def blocks(fn):
    t = open(os.path.join(D, fn), encoding='utf8').read()
    for m in re.finditer(r'^function (\w+)\(\)(.*?)^end', t, re.S | re.M):
        body = m.group(2)
        d = re.search(r'data = \w+\(;(.*?)\n    \)', body, re.S)
        if not d: continue
        f = {}
        for line in d.group(1).split('\n'):
            k = re.match(r'\s*(\w+)\s*=\s*(.+)$', line)
            if k: f[k.group(1)] = k.group(2)
        c = re.search(r'Comment = "((?:[^"\\]|\\.)*)"', body)
        yield m.group(1), f, (c.group(1) if c else '')
laws = {}
def entry(fid, f, comment):
    name = f['Name'].split('#')[0].strip().rstrip(',').strip().strip('"')
    rock, _, ref = name.partition('|')
    key = name
    e = laws.setdefault(key, dict(id=re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_'), name=rock.strip(), ref=ref.strip(), status='geoparams', note='', water_label='', water_default=1,
        disl=dict(enabled=False, A=1, n=1, p=0, r=0, E=0, V=0, apparatus='axial'),
        diff=dict(enabled=False, A=1, n=1, p=0, r=0, E=0, V=0, apparatus='axial'),
        peierls=dict(enabled=False, A=1, n=0, E=0, sp=1000, pp=1, q=1, apparatus='axial')))
    return e
def app(f): return APP.get(f.get('Apparatus', 'AxialCompression').split('#')[0].strip().rstrip(','), 'axial')
skipped = []
for fn, key in (('DislocationCreep.jl', 'disl'), ('DiffusionCreep.jl', 'diff')):
    for fid, f, c in blocks(fn):
        try:
            m = dict(enabled=True, A=ev(f['A'], UA), n=ev(f['n'], UN), p=-ev(f['p'], UN) if 'p' in f else 0.0, r=ev(f.get('r', '0'), UN), E=ev(f['E'], UE), V=ev(f.get('V', '0'), UV), apparatus=app(f))
        except Exception as ex:
            skipped.append((fid, str(ex))); continue
        e = entry(fid, f, c); e[key] = m
        e['note'] = (e['note'] + ' ' + (('Dislocation: ' if key == 'disl' else 'Diffusion: ') + c if c else '')).strip()
        if m['r']:
            coh = 'C_OH' in f['A'] or 'H/10^6 Si' in f['A'] or 'constant C_OH' in e['ref'] or 'COH' in fid
            e['water_label'] = 'C_OH (H/10⁶ Si)' if coh else 'fH₂O (MPa)'
            e['water_default'] = 1000 if coh else 100
for fn, nonlin in (('PeierlsCreep.jl', False), ('NonLinearPeierlsCreep.jl', True)):
    for fid, f, c in blocks(fn):
        try:
            m = dict(enabled=True, A=ev(f['A'], UA), n=ev(f['n'], UN) if nonlin else 0.0, E=ev(f['E'], UE), sp=ev(f['TauP'], UA), pp=ev(f['o'], UN), q=ev(f['q'], UN), apparatus=app(f))
        except Exception as ex:
            skipped.append((fid, str(ex))); continue
        e = entry(fid, f, c); e['peierls'] = m
        e['note'] = (e['note'] + ' ' + ('Peierls: ' + c if c else '')).strip()
laws = {k: v for k, v in laws.items() if not k.lower().startswith('test')}
for e in laws.values():
    if 'fO2' in e['name'] and e['water_label']: e['water_label'] = 'fO₂ term (see note)'; e['water_default'] = 1
extra = json.load(open('tools/extra_laws.json', encoding='utf8'))
ver = re.search(r'^version = "(.+)"', open(os.path.join(src, 'Project.toml')).read(), re.M).group(1)
commit = subprocess.run(['git', '-C', src, 'log', '-1', '--format=%h %ad', '--date=short'], capture_output=True, text=True).stdout.strip()
out = dict(source=f'GeoParams.jl v{ver} ({commit}), https://github.com/JuliaGeodynamics/GeoParams.jl, MIT licence', laws=sorted(list(laws.values()) + extra, key=lambda e: (e['name'].lower(), e['ref'])))
ids = {}
for e in out['laws']:
    n = ids.get(e['id'], 0); ids[e['id']] = n + 1
    if n: e['id'] += f'_{n+1}'
json.dump(out, open('data/flowlaws.json', 'w', encoding='utf8'), ensure_ascii=False, indent=1)
print(len(out['laws']), 'laws;', sum(e['disl']['enabled'] for e in out['laws']), 'disl,', sum(e['diff']['enabled'] for e in out['laws']), 'diff,', sum(e['peierls']['enabled'] for e in out['laws']), 'peierls; skipped', skipped)
