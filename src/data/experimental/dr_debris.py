"""Der Riese: the 2 buyable debris (DR_Debris04/08) use Der Riese's own model B (0xe05f4ec5, filing-cabinet pile, from the
iOS derriese_dynamics) instead of Kino's debris; DR_Door12 renders Der Riese's door (0x08e40ffe) like the other 10 doors.
B is rebuilt as a one-bone skinned copy of Kino's door asset (same method as the Shangri-La debris): closed/opening/open
anims, the 'open' ones sink it 20 m. Its textures (PVRTC) are converted to ETC1. New group derriese_debris, linked from
derriese.group before the statics. out: <dir>/derriese.group.bin, derriese_statics.group.bin, derriese_debris.group.bin"""
import sys, os, struct, math, numpy as np
sys.path.insert(0, '/root/work/tools'); sys.path.insert(0, '/home/claude/cod-boz-remastered/src/lib')
import dz, tlres, grp2, etcmip, texture2ddecoder as td
from propdump import comps
from PIL import Image
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
def dj(s):
    h = 5381
    for c in s.lower(): h = (h * 33 + c) & 0xffffffff
    return h
VB = bytes.fromhex('b836d00b') * 2; UB = bytes.fromhex('d5aac40a') * 2; CB = bytes.fromhex('35c0c5d1') * 2; TB = bytes.fromhex('e23f5189') * 2
D, F, C, _, _ = dz.parse('/root/work/s2/dz3d.dz')
def get(di, nm):
    i = [k for k, f in enumerate(F) if f[0] == nm and f[1] == di][0]; c = C[i]; return bytes(D[c[0]:c[0] + c[1]])
# ---------------- model B from the iOS package (read only)
PK = tlres.parse(open('/tmp/dr_dyn_raw.bin', 'rb').read()); PL = {l['cls']: [bytes(x)[4:] for x in l['items']] for l in PK['lists']}
def pk(c, h): r = [x for x in PL[c] if struct.unpack_from('<I', x, 0)[0] == h]; assert len(r) == 1, (hex(c), hex(h), len(r)); return r[0]
HB = 0xe05f4ec5; it = pk(0x89546ed9, HB)
i = it.find(VB); sz, cnt, z0, n, bias = struct.unpack_from('<HHHHh', it, i + 8)
P = np.frombuffer(it, '<i2', 3 * n, i + 18).reshape(3, n).T.astype(float) + bias
if cnt > n: P = np.vstack([P, P[np.frombuffer(it, '<u2', cnt - n, i + 18 + 6 * n).astype(int)]])
j = it.find(UB); uc = struct.unpack_from('<H', it, j + 10)[0]; UV = np.frombuffer(it, '<i2', 2 * uc, j + 14).reshape(-1, 2).astype(int)
assert uc == len(P), (uc, len(P))
nmat = None
for kk in range(1, 16):
    if struct.unpack_from('<II', it, len(it) - 8 - 4 * kk) == (0, kk): nmat = kk; break
mats = struct.unpack_from('<%dI' % nmat, it, len(it) - 4 * nmat)
bym = {}; k = it.find(TB)
while k >= 0:
    tc, _, m = struct.unpack_from('<HHH', it, k + 10); assert tc % 3 == 0 and m < nmat
    bym.setdefault(m, []).append(np.frombuffer(it, '<u2', tc, k + 18).astype(int).reshape(-1, 3)); k = it.find(TB, k + 4)
bym = {m: np.vstack(v) for m, v in bym.items()}; assert all((v < len(P)).all() for v in bym.values())
# textures of B's materials (long material: texture hash at 33)
def pvr(h):
    x = pk(0x3521f539, h); s = x.find(struct.pack('<I', 0x8c02)); assert 0 <= s < 80
    _, nm_, w, hh, sz_ = struct.unpack_from('<5I', x, s); off = s + 20 + 4 * nm_
    rgba = td.decode_pvrtc(bytes(x[off:off + sz_]), w, hh, False); return np.frombuffer(rgba, np.uint8).reshape(hh, w, 4)[:, :, [2, 1, 0]].copy()
mtex = {}
for mi, mh in enumerate(mats):
    if mi not in bym: continue
    mx = pk(0x2544f997, mh); mtex[mi] = struct.unpack_from('<I', mx, 33)[0]
print('model B verts', len(P), 'mats', nmat, {mi: (len(bym[mi]), hex(t)) for mi, t in mtex.items()})
# ---------------- templates
g = grp2.parse(open('/root/work/nachtsrc/nacht_env.group.bin', 'rb').read()); Lg = lambda c: [x for cc, h, it_ in g['lists'] if cc == c for x in it_]
TPL128 = [x for x in Lg(0x3521f539) if x.find(bytes.fromhex('648d0000')) > 0 and x[4:7].hex() == '144322' and struct.unpack_from('<I', x, x.find(bytes.fromhex('648d0000')) + 8)[0] == 128][0]
mtpl = [m for m in Lg(0x2544f997) if len(m) == 55][0]
KH = 0xdfbe538c; KANIM = {'closed': 0x09afcb05, 'opening': 0x50324add, 'open': 0x6421bcdb}
KD = grp2.parse(open('/root/work/s2/orig/kino_dynamics.group.bin', 'rb').read())
kget = lambda c, h: [x for L_ in KD['lists'] if L_[0] == c for x in L_[2] if struct.unpack_from('<I', x, 0)[0] == h][0]
k_skel, k_asm = kget(0xe1ccaf5c, KH), kget(0xba5bf49f, KH)
ROOTPAT = struct.pack('<8h', 0, 0, 0, 4096, 0, 0, 0, -604); DROP = -8000
def sink(anim, last_only):
    a = bytearray(anim); hits = [i for i in range(len(a) - 15) if a[i:i + 16] == ROOTPAT]; assert hits
    for i in (hits[-1:] if last_only else hits): struct.pack_into('<h', a, i + 2, DROP)
    return bytes(a)
# ---------------- new asset
Hk = dj(b'derriese_debris_b'); AH = {nm: dj(('derriese_debris_b_' + nm).encode()) for nm in KANIM}
tex_items, mat_items, tbm = [], [], {}
for mi, th0 in mtex.items():
    arr = np.asarray(Image.fromarray(pvr(th0)).resize((128, 128), Image.LANCZOS))
    th = dj(('derriese_dt_%08x' % th0).encode()); mh = dj(('derriese_dm_%08x' % th0).encode())
    s_ = TPL128.find(bytes.fromhex('648d0000')); tb = bytearray(struct.pack('<I', th) + TPL128[4:]); etcmip.write(tb, s_, arr); tex_items.append(bytes(tb))
    m = bytearray(mtpl); struct.pack_into('<I', m, 0, mh); struct.pack_into('<I', m, 33, th); mat_items.append(bytes(m)); tbm[mh] = bym[mi]
    Image.fromarray(arr).save('/tmp/drdeb_tex_%d.png' % mi)
# size: B scaled uniformly to the Kino debris width it replaces (the entities' scales then fit each opening as before)
KDB = kget(0x89546ed9, 0x793ffd74); i2 = KDB.find(VB); _, _, _, n2, b2 = struct.unpack_from('<HHHHh', KDB, i2 + 8)
PK2 = np.frombuffer(KDB, '<i2', 3 * n2, i2 + 18).reshape(3, n2).T.astype(float) + b2
used = np.unique(np.concatenate([v.reshape(-1) for v in bym.values()])); Pu = P[used]
S = (PK2[:, 0].max() - PK2[:, 0].min()) / (Pu[:, 0].max() - Pu[:, 0].min())
c0 = np.array([(Pu[:, 0].max() + Pu[:, 0].min()) / 2, Pu[:, 1].min(), (Pu[:, 2].max() + Pu[:, 2].min()) / 2])
Q = np.round((P - c0) * S).astype(int); Q[:, 1] -= 4                    # 4 cm into the floor, no visible gap
assert np.abs(Q).max() < 8000
print('scale', round(S, 3), 'size cm', (Q[used].max(0) - Q[used].min(0)).tolist(), 'kino debris', (PK2.max(0) - PK2.min(0)).tolist())
U = UV.copy()
def skinned_model(name, Q, U, C, tris_by_mat):
    n = len(Q); c = (Q.min(0) + Q.max(0)) // 2; r = int(math.ceil(np.sqrt(((Q - c) ** 2).sum(1)).max())) + 1
    bl = [VB + struct.pack('<HHHHh', 28 + 6 * n, n, 0, n, 0) + Q.T.astype('<i2').tobytes(),
          UB + struct.pack('<HHH', 28 + 4 * n, n, 0) + U.astype('<i2').tobytes(),
          CB + struct.pack('<HHHB', 28 + 4 * n, n, 0, 0) + np.vstack([C, C, C, np.full(n, 255, np.uint8)]).astype(np.uint8).tobytes()]
    ms = list(tris_by_mat)
    for mi_, mh_ in enumerate(ms):
        T = tris_by_mat[mh_]; ix = T.reshape(-1).astype('<u2').tobytes(); cnt = T.size
        bl.append(TB + struct.pack('<HHHHH', 28 + 2 * cnt, cnt, 0, mi_, 0) + ix + struct.pack('<HH', 0, n))
    hdr = struct.pack('<I', name) + struct.pack('<HHHH', 0, 3, n, n) + struct.pack('<iiiiI', int(c[0]), int(c[1]), int(c[2]), r, len(bl))
    return hdr + b''.join(bl) + struct.pack('<II', 0, len(ms)) + b''.join(struct.pack('<I', m) for m in ms)
mod = skinned_model(Hk, Q, U, np.full(len(Q), 165, np.uint8), tbm)
skel = struct.pack('<I', Hk) + k_skel[4:]
recs = b''.join(struct.pack('<H4h', i, *(4 * Q[i]), -128) for i in range(len(Q)))
skin = struct.pack('<IIIII', Hk, 1, Hk, Hk, 1) + struct.pack('<IIII', 0x7ec0334e, 0, len(Q), 2 + 10 * len(Q)) + bytes([0, 0xff]) + recs
anims = []
for nm, src in KANIM.items():
    a = kget(0xc6133cad, src); assert struct.unpack_from('<I', a, 4)[0] == KH
    a = struct.pack('<II', AH[nm], Hk) + a[8:]
    if nm != 'closed': a = sink(a, last_only=(nm == 'opening'))
    anims.append(a)
asm = bytearray(k_asm)
for nm, src in KANIM.items(): p_ = asm.find(struct.pack('<I', src)); assert p_ > 0; struct.pack_into('<I', asm, p_, AH[nm])
asm = bytes(asm).replace(struct.pack('<I', KH), struct.pack('<I', Hk))
GD = grp2.parse(open('/root/work/temple/temple_dynamics.group.bin', 'rb').read())
assert GD['pre'].count(b'temple_dynamics\0') == 1; GD['pre'] = GD['pre'].replace(b'temple_dynamics\0', b'derriese_debris\0')
NEW = {0x3521f539: tex_items, 0x2544f997: mat_items, 0x89546ed9: [mod], 0xe1ccaf5c: [skel], 0xe1ccafe2: [skin], 0xc6133cad: anims, 0xba5bf49f: [asm], 0x78b2e3ec: []}
assert sorted(NEW) == sorted(L_[0] for L_ in GD['lists'])
for L_ in GD['lists']: L_[2] = NEW[L_[0]]
gb = grp2.build(GD); open(OUT + '/derriese_debris.group.bin', 'wb').write(gb)
G2 = grp2.parse(gb); assert [len(L_[2]) for L_ in G2['lists']] == [len(NEW[L_[0]]) for L_ in G2['lists']]
# ---------------- derriese.group: link the new group before the statics
tg = bytearray(get('levels\\derriese', 'derriese.group.bin')); cl = tg.find(struct.pack('<I', 0x3b495dc0)); assert cl > 0
sz_, cnt_ = struct.unpack_from('<IB', tg, cl + 4); assert cnt_ == 2
ent_ = b'levels/derriese//derriese_debris.group\0' + bytes.fromhex('0000000000100000') + struct.pack('<I', dj(b'derriese_debris'))
k_ = tg.find(b'levels/derriese//derriese_statics.group'); assert k_ > cl
tg[k_:k_] = ent_; struct.pack_into('<IB', tg, cl + 4, sz_ + len(ent_), 3); open(OUT + '/derriese.group.bin', 'wb').write(bytes(tg))
# ---------------- statics: entities
R = tlres.parse(get('levels\\derriese', 'derriese_statics.group.bin')); L = {l['name']: l for l in R['lists']}
def name_of(x):
    for c in comps(x):
        if c[0] == 'CIsNamed' and c[2]: p = c[2][0]; return x[p[4]:p[4] + p[3]].split(b'\0')[0].decode('latin1')
def prop_off(x, comp, prop): return [(d_, s_) for c, o, ps in comps(x) if c == comp for p_, t, n_, s_, d_ in ps if t.lower() == prop.lower()][0]
EL = L['0x78b2e3ec']['items']; idx = {name_of(bytes(x)): i for i, x in enumerate(EL)}
for nm in ('DR_Debris04', 'DR_Debris08'):
    x = bytearray(bytes(EL[idx[nm]]))
    for c_, p_ in (('CIsAnimator', '0x7c9df3b4'), ('CIsASMAnimator', 'ASM'), ('CIsRenderableModel', '0x7c9df3b4')):
        o_, s_ = prop_off(bytes(x), c_, p_); assert s_ == 4; struct.pack_into('<I', x, o_, Hk)
    assert bytes(x).count(struct.pack('<I', 0x793ffd74)) == 2
    x = bytes(x).replace(struct.pack('<I', 0x793ffd74), struct.pack('<I', Hk))
    assert not any(x.count(struct.pack('<I', h_)) for h_ in (0x481b101f, 0x513ffe04, 0x793ffd74)) and x.count(struct.pack('<I', Hk)) == 5
    assert len(x) == len(EL[idx[nm]]); EL[idx[nm]] = x
# DR_Door12: its renderable = DR_Door01's (Der Riese door model, Kino door skeleton it already animates with)
def comp_span(x, name):
    cs = comps(x); i = [k for k, c in enumerate(cs) if c[0] == name]; assert len(i) == 1; i = i[0]
    s = cs[i][1]; e = cs[i + 1][1] if i + 1 < len(cs) else None; return s, e
d1, d12 = bytes(EL[idx['DR_Door01']]), bytes(EL[idx['DR_Door12']])
s1, e1 = comp_span(d1, 'CIsRenderableModel'); s12, e12 = comp_span(d12, 'CIsRenderableModel'); assert e1 and e12
new12 = bytearray(d12[:s12] + d1[s1:e1] + d12[e12:])
tot0 = struct.unpack_from('<I', d12, 0)[0]; assert tot0 == len(d12) and struct.unpack_from('<I', d12, 8)[0] == 11   # header: size, hash, 11
struct.pack_into('<I', new12, 0, len(new12))
assert [c[0] for c in comps(bytes(new12))] == [c[0] for c in comps(d12)] and name_of(bytes(new12)) == 'DR_Door12'
assert bytes(new12).count(struct.pack('<I', 0x08e40ffe)) == 1 and prop_off(bytes(new12), 'CIsASMAnimator', 'ASM')
EL[idx['DR_Door12']] = bytes(new12)
sb = tlres.write(R); open(OUT + '/derriese_statics.group.bin', 'wb').write(sb)
R2 = tlres.parse(sb); assert len(R2['lists'][[l['name'] for l in R2['lists']].index('0x78b2e3ec')]['items']) == len(EL)
print('ok asset %08x' % Hk, 'debris group', len(gb), 'statics', len(sb))
