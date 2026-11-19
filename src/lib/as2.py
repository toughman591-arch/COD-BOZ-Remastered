"""Tiny AS2 bytecode tools: parse records, insert bytes with branch / block-size fix-ups, rewrite push strings."""
import struct
def records(a, p=0, end=None):
    end = len(a) if end is None else end; out = []
    while p < end:
        c = a[p]
        if c >= 0x80: n = struct.unpack_from('<H', a, p + 1)[0]; out.append((p, c, bytes(a[p + 3:p + 3 + n]))); p += 3 + n
        else: out.append((p, c, b'')); p += 1
        if c == 0 and end == len(a): break
    return out
def blocks(a):
    """(field_pos, start, size) for every DefineFunction/DefineFunction2/With block"""
    out = []
    for p, c, d in records(a):
        st = p + 3 + len(d)
        if c in (0x9b, 0x8e): out.append((st - 2, st, struct.unpack_from('<H', a, st - 2)[0]))
        if c == 0x94: out.append((p + 3, st, struct.unpack_from('<H', a, p + 3)[0]))
        assert c != 0x8f, 'try blocks not handled'
    return out
def insert(a, pos, new):
    a = bytearray(a); L = len(new); R = records(a)
    assert pos in [r[0] for r in R] + [len(a)], 'not a record boundary'
    fix = []
    for p, c, d in R:
        if c in (0x99, 0x9d):
            E = p + 5; T = E + struct.unpack_from('<h', a, p + 3)[0]
            E2 = E + (L if E > pos else 0); T2 = T + (L if T > pos else 0); fix.append((p + 3, T2 - E2, p >= pos))
    bl = [(f, s, n + (L if s <= pos < s + n else 0), f >= pos) for f, s, n in blocks(a)]
    for f, v, after in fix: struct.pack_into('<h', a, f, v)
    for f, s, n, after in bl: struct.pack_into('<H', a, f, n)
    return bytes(a[:pos]) + new + bytes(a[pos:])
def pool(a):
    for p, c, d in records(a):
        if c == 0x88:
            n = struct.unpack_from('<H', d, 0)[0]; return d[2:].split(b'\0')[:n]
    return []
def push_items(d):
    out = []; p = 0
    while p < len(d):
        t = d[p]; p += 1
        if t == 0: e = d.index(b'\0', p); out.append((0, d[p:e])); p = e + 1
        elif t in (1,): out.append((t, d[p:p + 4])); p += 4
        elif t in (2, 3): out.append((t, b''))
        elif t == 4: out.append((t, d[p:p + 1])); p += 1
        elif t == 5: out.append((t, d[p:p + 1])); p += 1
        elif t == 6: out.append((t, d[p:p + 8])); p += 8
        elif t == 7: out.append((t, d[p:p + 4])); p += 4
        elif t == 8: out.append((t, d[p:p + 1])); p += 1
        elif t == 9: out.append((t, d[p:p + 2])); p += 2
        else: raise ValueError(t)
    return out
def push_bytes(items):
    d = b''.join(bytes([t]) + (v + b'\0' if t == 0 else v) for t, v in items); return b'\x96' + struct.pack('<H', len(d)) + d
def strings_of(items, cp):
    out = []
    for t, v in items:
        if t == 0: out.append(v)
        elif t == 8: out.append(cp[v[0]])
        elif t == 9: out.append(cp[struct.unpack('<H', v)[0]])
        else: out.append(None)
    return out
def rewrite(seg, cp, mapping):
    """copy of a straight-line action segment with push strings replaced (constant-pool refs become literals)"""
    out = b''
    for p, c, d in records(seg):
        assert c not in (0x99, 0x9d, 0x9b, 0x8e, 0x94, 0x8f), hex(c)
        if c == 0x96:
            items = push_items(d); new = []
            for (t, v), s in zip(items, strings_of(items, cp)):
                if s is not None and s in mapping: new.append((0, mapping[s]))
                elif s is not None and t in (8, 9): new.append((t, v))
                else: new.append((t, v))
            out += push_bytes(new)
        else: out += bytes([c]) + (struct.pack('<H', len(d)) + d if c >= 0x80 else b'')
    return out
def dis(a, cp=None):
    cp = pool(a) if cp is None else cp
    for p, c, d in records(a):
        s = ''
        if c == 0x96: s = strings_of(push_items(d), cp)
        if c in (0x99, 0x9d): s = struct.unpack('<h', d)[0]
        print(p, hex(c), s)
