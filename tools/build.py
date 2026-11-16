#!/usr/bin/env python3
"""Embed data/flowlaws.json and data/materials.json into index.html so the page also works offline."""
import json, re, os
root = os.path.join(os.path.dirname(__file__), '..')
h = open(os.path.join(root, 'index.html'), encoding='utf8').read()
db = json.load(open(os.path.join(root, 'data/flowlaws.json'), encoding='utf8'))
md = json.load(open(os.path.join(root, 'data/materials.json'), encoding='utf8'))
blk = '/*DB-START*/const DB=' + json.dumps(db, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + ',MDB=' + json.dumps(md, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + ';/*DB-END*/'
i, j = h.index('/*DB-START*/'), h.index('/*DB-END*/') + len('/*DB-END*/')
open(os.path.join(root, 'index.html'), 'w', encoding='utf8').write(h[:i] + blk + h[j:])
print('embedded', len(db['laws']), 'laws and', len(md['materials']), 'materials')
