"""Find drop-down ledges in a level navmesh: boundary edges of an upper polygon with walkable navmesh 1.2-4.5 m below
just past the edge, and both sides in the same zone (zones = navmesh split at door/debris blocker polygons)."""
import sys, struct, numpy as np, collections
sys.path.insert(0, '/root/work/drdeb'); from entlib import *; import nav
def load(path):
    R = tlres.parse(open(path, 'rb').read()); L = {l['name']: l for l in R['lists']}
    nb = bytes(L['0xacc04716']['items'][0]); T = nav.tiles(nb); P = []
    for ti, t in enumerate(T):
        for i in range(t['pc']):
            o = t['po'] + 40 * i; vc = struct.unpack_from('<I', nb, o + 36)[0]; vs = struct.unpack_from('<6H', nb, o + 4)[:vc]
            ne = struct.unpack_from('<6H', nb, o + 16)[:vc]; tg = struct.unpack_from('<I', nb, o + 32)[0]
            P.append(dict(t=ti, i=i, o=o, V=t['verts'][list(vs)].astype(float), ne=ne, tag=tg))
    return R, L, nb, T, P
def zones(P):
    key = lambda v: (round(v[0], 2), round(v[1], 1), round(v[2], 2))
    E = collections.defaultdict(list)
    for k, p in enumerate(P):
        n = len(p['V'])
        for e in range(n):
            a, b = key(p['V'][e]), key(p['V'][(e + 1) % n]); E[(min(a, b), max(a, b))].append(k)
    par = list(range(len(P)))
    def f(x):
        while par[x] != x: par[x] = par[par[x]]; x = par[x]
        return x
    for ks in E.values():
        for a in ks:
            for b in ks:
                if P[a]['tag'] == 0 and P[b]['tag'] == 0: par[f(a)] = f(b)
    return [f(k) for k in range(len(P))], E
def inside(V, x, z):
    n = len(V); s = 0
    for e in range(n):
        ax, az = V[e][0], V[e][2]; bx, bz = V[(e + 1) % n][0], V[(e + 1) % n][2]
        c = (bx - ax) * (z - az) - (bz - az) * (x - ax)
        if abs(c) < 1e-9: continue
        s |= 1 if c > 0 else 2
    return s != 3
def ledges(P, Z, out_d=0.6, dmin=1.2, dmax=4.5):
    res = []
    for k, p in enumerate(P):
        if p['tag']: continue
        V = p['V']; n = len(V); c = V.mean(0)
        for e in range(n):
            if p['ne'][e] != 0: continue
            a, b = V[e], V[(e + 1) % n]; d = b - a; L_ = np.hypot(d[0], d[2])
            if L_ < 0.6: continue
            nrm = np.array([d[2], 0, -d[0]]) / L_
            if np.dot(nrm, ((a + b) / 2 - c)) < 0: nrm = -nrm
            hits = []
            for t_ in (0.25, 0.5, 0.75):
                q = a + d * t_ + nrm * out_d; y = a[1] + d[1] * t_
                for j, r in enumerate(P):
                    if r['tag'] or j == k: continue
                    if r['V'][:, 1].max() > y - dmin or r['V'][:, 1].min() < y - dmax - 0.5: continue
                    if r['V'][:, 0].min() - 0.01 <= q[0] <= r['V'][:, 0].max() + 0.01 and r['V'][:, 2].min() - 0.01 <= q[2] <= r['V'][:, 2].max() + 0.01 and inside(r['V'], q[0], q[2]):
                        hits.append((j, y - r['V'][:, 1].mean()))
            if len(hits) >= 2 and len({Z[j] for j, _ in hits}) == 1 and Z[hits[0][0]] == Z[k]:
                res.append(dict(up=k, low=sorted({j for j, _ in hits}), a=a, b=b, nrm=nrm, drop=float(np.mean([h for _, h in hits])), len=L_))
    return res
