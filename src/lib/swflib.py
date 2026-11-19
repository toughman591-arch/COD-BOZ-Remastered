"""Minimal SWF helpers: tags, sprites, PlaceObject2 parse/build (matrix, name, clip actions kept raw)."""
import struct
def header_end(b): nb = b[8] >> 3; return 8 + (5 + 4 * nb + 7) // 8 + 4
def tags(b, p, end):
    out = []
    while p < end:
        cl, = struct.unpack_from('<H', b, p); code, ln = cl >> 6, cl & 0x3f; h = 2
        if ln == 0x3f: ln, = struct.unpack_from('<I', b, p + 2); h = 6
        out.append((code, bytes(b[p:p + h + ln]), h)); p += h + ln
        if code == 0: break
    return out
def body(t): return t[1][t[2]:]
def tag(code, bd, long=False):
    if len(bd) < 0x3f and not long: return (code, struct.pack('<H', code << 6 | len(bd)) + bd, 2)
    return (code, struct.pack('<HI', code << 6 | 0x3f, len(bd)) + bd, 6)
def cid(t): return struct.unpack_from('<H', body(t), 0)[0]
def load(path):
    b = open(path, 'rb').read(); assert b[:3] == b'FWS'; he = header_end(b); return b[:he], tags(b, he, len(b))
def build(h, T):
    out = bytearray(h) + b''.join(t[1] for t in T); struct.pack_into('<I', out, 4, len(out)); return bytes(out)
def subtags(bd):
    sid, fc = struct.unpack_from('<HH', bd, 0); return sid, fc, tags(bd, 4, len(bd))
def sprite_tag(sid, fc, S): return tag(39, struct.pack('<HH', sid, fc) + b''.join(x[1] for x in S), long=True)
class BR:
    def __init__(s, b, p): s.b, s.p, s.bit = b, p, 0
    def u(s, n):
        v = 0
        for _ in range(n):
            v = (v << 1) | ((s.b[s.p] >> (7 - s.bit)) & 1); s.bit += 1
            if s.bit == 8: s.bit = 0; s.p += 1
        return v
    def s_(s, n):
        v = s.u(n); return v - (1 << n) if n and v >> (n - 1) else v
    def align(s):
        if s.bit: s.bit = 0; s.p += 1
class BW:
    def __init__(s): s.v, s.n = 0, 0
    def u(s, v, n): s.v = (s.v << n) | (v & ((1 << n) - 1)); s.n += n
    def bytes(s):
        pad = (-s.n) % 8; v = s.v << pad; return v.to_bytes((s.n + pad) // 8, 'big') if s.n + pad else b''
def nbits(*vals):
    n = 1
    for v in vals:
        while not (-(1 << (n - 1)) <= v < (1 << (n - 1))): n += 1
    return n
def read_matrix(b, p):
    r = BR(b, p); m = {}
    if r.u(1): n = r.u(5); m['sx'] = r.s_(n) / 65536; m['sy'] = r.s_(n) / 65536
    if r.u(1): n = r.u(5); m['r0'] = r.s_(n) / 65536; m['r1'] = r.s_(n) / 65536
    n = r.u(5); m['tx'] = r.s_(n); m['ty'] = r.s_(n); r.align(); return m, r.p
def write_matrix(m):
    w = BW()
    if 'sx' in m:
        a, c = round(m['sx'] * 65536), round(m['sy'] * 65536); n = nbits(a, c); w.u(1, 1); w.u(n, 5); w.u(a, n); w.u(c, n)
    else: w.u(0, 1)
    if 'r0' in m:
        a, c = round(m['r0'] * 65536), round(m['r1'] * 65536); n = nbits(a, c); w.u(1, 1); w.u(n, 5); w.u(a, n); w.u(c, n)
    else: w.u(0, 1)
    tx, ty = round(m['tx']), round(m['ty']); n = nbits(tx, ty) if (tx or ty) else 0; w.u(n, 5); w.u(tx, n); w.u(ty, n)
    return w.bytes()
def read_cxform_a(b, p):   # CXFORMWITHALPHA, kept raw
    r = BR(b, p); ha, hm = r.u(1), r.u(1); n = r.u(4); r.u(n * 4 * (ha + hm)); r.align(); return bytes(b[p:r.p]), r.p
def po2(t):
    """PlaceObject2 -> dict"""
    assert t[0] == 26; b = body(t); fl = b[0]; d = {'depth': struct.unpack_from('<H', b, 1)[0], 'move': bool(fl & 1)}; p = 3
    if fl & 2: d['cid'] = struct.unpack_from('<H', b, p)[0]; p += 2
    if fl & 4: d['matrix'], p = read_matrix(b, p)
    if fl & 8: d['cx'], p = read_cxform_a(b, p)
    if fl & 16: d['ratio'] = struct.unpack_from('<H', b, p)[0]; p += 2
    if fl & 32: e = b.index(b'\0', p); d['name'] = b[p:e].decode('latin1'); p = e + 1
    if fl & 64: d['clipdepth'] = struct.unpack_from('<H', b, p)[0]; p += 2
    if fl & 128: d['actions'] = bytes(b[p:]); p = len(b)
    assert p == len(b); return d
def build_po2(d):
    fl = (1 if d.get('move') else 0); out = b''
    if 'cid' in d: fl |= 2; out += struct.pack('<H', d['cid'])
    if 'matrix' in d: fl |= 4; out += write_matrix(d['matrix'])
    if 'cx' in d: fl |= 8; out += d['cx']
    if 'ratio' in d: fl |= 16; out += struct.pack('<H', d['ratio'])
    if 'name' in d: fl |= 32; out += d['name'].encode('latin1') + b'\0'
    if 'clipdepth' in d: fl |= 64; out += struct.pack('<H', d['clipdepth'])
    if 'actions' in d: fl |= 128; out += d['actions']
    return tag(26, bytes([fl]) + struct.pack('<H', d['depth']) + out, long=True)
def frames_of(S):
    assert S[-1][0] == 0; fr = [[]]
    for x in S[:-1]:
        if x[0] == 1: fr.append([])
        else: fr[-1].append(x)
    assert fr[-1] == []; return fr[:-1]
SHOWF = tag(1, b''); END = (0, b'\0\0', 2)
def label(s): return tag(43, s.encode() + b'\0')
def remove(depth): return tag(28, struct.pack('<H', depth))
def read_rect(b, p):
    r = BR(b, p); n = r.u(5); v = [r.s_(n) for _ in range(4)]; r.align(); return v, r.p   # xmin,xmax,ymin,ymax
def char_bounds(T, c, depth=0):
    t = [t for t in T if t[0] not in (0, 1, 9, 12, 26, 28, 43, 69, 77, 86, 56, 74, 73, 13, 62, 88, 59, 65, 76) and cid(t) == c][0]; b = body(t)
    if t[0] in (2, 22, 32, 83, 37, 11, 33, 46, 84, 10, 48, 75): return read_rect(b, 2)[0] if t[0] not in (10, 48, 75) else None
    if t[0] == 34:  # DefineButton2: id, flags, actionoffset, records
        p = 5; bb = None
        while b[p]:
            fl = b[p]; ch = struct.unpack_from('<H', b, p + 1)[0]; m, p = read_matrix(b, p + 5); _, p = read_cxform_a(b, p)
            assert not fl & 0x10, 'button filters'
            if fl & 0x20: p += 1
            r = char_bounds(T, ch, depth + 1)
            if r: bb = union(bb, xform(m, r))
        return bb
    if t[0] == 39:
        _, _, S = subtags(b); bb = None
        for x in S:
            if x[0] == 26:
                d = po2(x)
                if 'cid' in d and 'matrix' in d:
                    r = char_bounds(T, d['cid'], depth + 1)
                    if r: bb = union(bb, xform(d['matrix'], r))
        return bb
def xform(m, r):
    sx, sy, r0, r1 = m.get('sx', 1), m.get('sy', 1), m.get('r0', 0), m.get('r1', 0)
    pts = [(x, y) for x in r[:2] for y in r[2:]]
    xs = [sx * x + r1 * y + m['tx'] for x, y in pts]; ys = [r0 * x + sy * y + m['ty'] for x, y in pts]
    return [min(xs), max(xs), min(ys), max(ys)]
def union(a, b):
    if a is None: return b
    return [min(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), max(a[3], b[3])]
def parse_picshape(t):
    """DefineShape(1/2) that is one bitmap-filled rectangle -> dict"""
    b = body(t); sid = struct.unpack_from('<H', b, 0)[0]; rect, p = read_rect(b, 2)
    nf = b[p]; assert nf == 1; ft = b[p + 1]; assert 0x40 <= ft <= 0x43; bid = struct.unpack_from('<H', b, p + 2)[0]
    m, p = read_matrix(b, p + 4); nl = b[p]; assert nl == 0
    return dict(id=sid, rect=rect, ftype=ft, bitmap=bid, fm=m, code=t[0], shape=bytes(b[p + 1:]))
def region_of(ps):
    m = ps['fm']; assert 'r0' not in m; x0, x1, y0, y1 = ps['rect']
    return ((x0 - m['tx']) / m['sx'], (y0 - m['ty']) / m['sy'], (x1 - m['tx']) / m['sx'], (y1 - m['ty']) / m['sy'])
def build_picshape(sid, rect, ftype, bitmap, region, code=2, fills=(0, 1), order=0):
    x0, x1, y0, y1 = rect; u0, v0, u1, v1 = region
    sx = (x1 - x0) / (u1 - u0); sy = (y1 - y0) / (v1 - v0); m = dict(sx=sx, sy=sy, tx=x0 - sx * u0, ty=y0 - sy * v0)
    w = BW(); w.u(1, 4); w.u(0, 4)                 # NumFillBits=1, NumLineBits=0
    w.u(0, 1); w.u(0b00111, 5)                     # style change: FillStyle1 + FillStyle0 + MoveTo (as the game's own picture shapes)
    n = nbits(x0, y0); w.u(n, 5); w.u(x0, n); w.u(y0, n)
    w.u(fills[0], 1); w.u(fills[1], 1)              # FillStyle0, FillStyle1
    def edge(dx, dy):
        v = dx if dy == 0 else dy; n = max(nbits(v), 2); w.u(1, 1); w.u(1, 1); w.u(n - 2, 4); w.u(0, 1); w.u(1 if dy else 0, 1); w.u(v, n)
    edge(x1 - x0, 0); edge(0, y1 - y0); edge(x0 - x1, 0); edge(0, y0 - y1)
    w.u(0, 6)
    rb = BW(); n = nbits(*rect); rb.u(n, 5); [rb.u(v, n) for v in rect]
    bd = struct.pack('<H', sid) + rb.bytes() + bytes([1, ftype]) + struct.pack('<H', bitmap) + write_matrix(m) + b'\0' + w.bytes()
    return tag(code, bd)
def clone_picshape(t, newid, region):
    """copy of a one-rectangle picture shape with only its bitmap area changed (geometry bytes kept)"""
    b = body(t); _, p = read_rect(b, 2); x0, x1, y0, y1 = read_rect(b, 2)[0]
    assert b[p] == 1 and 0x40 <= b[p + 1] <= 0x43; _, q = read_matrix(b, p + 4)
    u0, v0, u1, v1 = region; sx = (x1 - x0) / (u1 - u0); sy = (y1 - y0) / (v1 - v0)
    m = dict(sx=sx, sy=sy, tx=x0 - sx * u0, ty=y0 - sy * v0)
    out = tag(t[0], struct.pack('<H', newid) + b[2:p + 4] + write_matrix(m) + b[q:])
    r2 = region_of(parse_picshape(out)); assert max(abs(a - c) for a, c in zip(r2, region)) < 0.05, (r2, region)
    return out
def build_poly(sid, pts, fill):
    """DefineShape: one closed polygon, given clockwise on screen (y down), filled with FillStyle1 = fill (fill-style bytes)"""
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]; rect = [min(xs), max(xs), min(ys), max(ys)]
    w = BW(); w.u(1, 4); w.u(0, 4)
    w.u(0, 1); w.u(0b00101, 5); x0, y0 = pts[0]; n = nbits(x0, y0); w.u(n, 5); w.u(x0, n); w.u(y0, n); w.u(1, 1)
    for (ax, ay), (bx, by) in zip(pts, pts[1:] + pts[:1]):
        dx, dy = bx - ax, by - ay; n = max(nbits(dx, dy), 2); w.u(1, 1); w.u(1, 1); w.u(n - 2, 4); w.u(1, 1); w.u(dx, n); w.u(dy, n)
    w.u(0, 6)
    rb = BW(); n = nbits(*rect); rb.u(n, 5); [rb.u(v, n) for v in rect]
    return tag(2, struct.pack('<H', sid) + rb.bytes() + bytes([1]) + fill + b'\0' + w.bytes())
