"""Der Riese jump-down spots, done like Kino / Call of the Dead: walk-map polygons at a ledge get a 'jump area' tag, the
polygons below get a 'land area' tag, and a CPlayerJumpPoint (copy of Kino's) names the pair. Only tags change in the walk
map (same size, no rebuild). Ledges: 1.2-5 m drop, both sides in the same zone (doors/debris not skipped).
in: Der Riese statics, out: statics + preview map"""
import sys, struct, numpy as np; sys.path.insert(0, '/root/work/drdeb'); from ledges import *
SRC, DST, PNG = sys.argv[1:4]
def dj(s):
    h = 5381
    for c in s.lower(): h = (h * 33 + c) & 0xffffffff
    return h
R, L, nb, T, P = load(SRC); Z, E = zones(P); res = ledges(P, Z, dmax=5.0)
cl = []
for r in res:
    m = (r['a'] + r['b']) / 2
    for c in cl:
        if np.linalg.norm(c['m'] - m) < 4 and abs(c['drop'] - r['drop']) < 1: c['r'].append(r); break
    else: cl.append(dict(m=m, drop=r['drop'], r=[r]))
for c in cl: c['U'] = {r['up'] for r in c['r']}; c['L'] = {j for r in c['r'] for j in r['low']}
allU = set().union(*[c['U'] for c in cl]); allL = set().union(*[c['L'] for c in cl])
cl = [c for c in cl if not (c['U'] & allL) and not (c['L'] & allU) and sum(r['len'] for r in c['r']) >= 1.5]
# shared polygons -> shared hash
def groups(key):
    g = list(range(len(cl)))
    for i in range(len(cl)):
        for j in range(i):
            if cl[i][key] & cl[j][key]:
                a, b = g[i], g[j]; g = [b if x == a else x for x in g]
    return g
gu, gl = groups('U'), groups('L')
nb = bytearray(nb); ents = []
KJ = [bytes(x) for x in tlres.parse(get('levels\\kino', 'kino_statics.group.bin'))['lists'][[l['name'] for l in tlres.parse(get('levels\\kino', 'kino_statics.group.bin'))['lists']].index('0x78b2e3ec')]['items'] if name_of(bytes(x)) == 'jump_point_left'][0]
assert KJ.count(b'jump_point_left\0') == 1
EL = L['0x78b2e3ec']['items']; have = {name_of(bytes(e)) for e in EL}
for k, c in enumerate(cl):
    JH, LH = dj(b'dr_jump_area_%02d' % gu[k]), dj(b'dr_land_area_%02d' % gl[k])
    for i in c['U']: assert P[i]['tag'] in (0, JH); struct.pack_into('<I', nb, P[i]['o'] + 32, JH)
    for i in c['L']: assert P[i]['tag'] in (0, LH); struct.pack_into('<I', nb, P[i]['o'] + 32, LH)
    for i in c['U'] | c['L']: P[i]['tag'] = struct.unpack_from('<I', nb, P[i]['o'] + 32)[0]
    r = max(c['r'], key=lambda r: r['len']); pos = (r['a'] + r['b']) / 2 * 100
    nm = b'drjump_point_%02d' % k; assert len(nm) == 15 and nm.decode() not in have
    e = bytearray(KJ.replace(b'jump_point_left\0', nm + b'\0')); struct.pack_into('<I', e, 4, dj(nm))
    i_ = e.find(struct.pack('<3f', *struct.unpack_from('<3f', KJ, KJ.find(bytes.fromhex('a8b5b6c2'))))); assert i_ > 0
    struct.pack_into('<3f', e, i_, *pos)
    for old, new in ((0x0363118e, JH), (0x6d587780, LH)):
        assert e.count(struct.pack('<I', old)) == 1; j = e.find(struct.pack('<I', old)); struct.pack_into('<I', e, j, new)
    EL.append(bytes(e)); c.update(JH=JH, LH=LH, pos=pos, name=nm.decode())
    print(nm.decode(), 'at', pos.round(), 'drop %.1f m' % c['drop'], 'ledge %.1f m' % sum(r['len'] for r in c['r']), 'up', len(c['U']), 'land', len(c['L']))
L['0xacc04716']['items'][0] = bytes(nb)
out = tlres.write(R); open(DST, 'wb').write(out)
R2 = tlres.parse(out); L2 = {l['name']: l for l in R2['lists']}
assert bytes(L2['0xacc04716']['items'][0]) == bytes(nb) and len(L2['0x78b2e3ec']['items']) == len(EL)
# preview map (top view): grey = walk map by height, red = jump area, blue = land area, yellow = jump point
from PIL import Image, ImageDraw
A = np.vstack([p['V'] for p in P]); x0, z0 = A[:, 0].min(), A[:, 2].min(); S = 1500 / max(np.ptp(A[:, 0]), np.ptp(A[:, 2]))
im = Image.new('RGB', (int(np.ptp(A[:, 0]) * S) + 40, int(np.ptp(A[:, 2]) * S) + 40), (20, 20, 20)); d = ImageDraw.Draw(im)
y0, y1 = A[:, 1].min(), A[:, 1].max(); JS = {c['JH'] for c in cl}; LS = {c['LH'] for c in cl}
tf = lambda v: (20 + (v[0] - x0) * S, 20 + (v[2] - z0) * S)
for p in sorted(P, key=lambda p: p['V'][:, 1].mean()):
    g = int(60 + 150 * (p['V'][:, 1].mean() - y0) / (y1 - y0)); col = (200, 40, 40) if p['tag'] in JS else (40, 90, 220) if p['tag'] in LS else (g, g, g)
    d.polygon([tf(v) for v in p['V']], fill=col)
for c in cl:
    q = tf(c['pos'] / 100); d.ellipse([q[0] - 7, q[1] - 7, q[0] + 7, q[1] + 7], fill=(255, 220, 0)); d.text((q[0] + 9, q[1] - 6), c['name'][-2:], fill=(255, 255, 0))
im.save(PNG); print('spots', len(cl), 'statics', len(out))
