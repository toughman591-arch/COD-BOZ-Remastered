"""Co-op map-name lookup also knows 'derriese' (Der Riese).
F (0x249f84) walks the run-time 4-map table; on 'not found' it now branches to X (0x400be6, in libpng's
'Unknown compression type %d' error text, next to the existing 'derriese' string at 0x400bbc) instead of the
nacht/verruck/proto cave. X hashes 'derriese', returns it on a match, else continues into the old cave (unchanged)."""
import struct, lzma, sys
SRC, DST = sys.argv[1], sys.argv[2]
cc = open(SRC, 'rb').read(); raw = bytearray(lzma.decompress(cc, format=lzma.FORMAT_ALONE)); B = 3
def put(m, b): raw[m + B:m + B + len(b)] = b
def get(m, n): return bytes(raw[m + B:m + B + n])
def hw(*h): return b''.join(struct.pack('<H', x) for x in h)
def blx_arm(src, dst):
    off = dst - ((src + 4) & ~3); assert -(1 << 24) <= off < (1 << 24) and off % 4 == 0
    S = (off >> 24) & 1; I1 = (off >> 23) & 1; I2 = (off >> 22) & 1; J1 = (1 - I1) ^ S; J2 = (1 - I2) ^ S
    return hw(0xf000 | (S << 10) | ((off >> 12) & 0x3ff), 0xc000 | (J1 << 13) | (J2 << 11) | (((off >> 2) & 0x3ff) << 1))
def bw(src, dst):
    off = dst - (src + 4); assert -(1 << 24) <= off < (1 << 24) and off % 2 == 0
    S = (off >> 24) & 1; I1 = (off >> 23) & 1; I2 = (off >> 22) & 1; J1 = (1 - I1) ^ S; J2 = (1 - I2) ^ S
    return hw(0xf000 | (S << 10) | ((off >> 12) & 0x3ff), 0x9000 | (J1 << 13) | (J2 << 11) | ((off >> 1) & 0x7ff))
def adrw_neg(at, target, rd=4):
    base = (at + 4) & ~3; imm = base - target; assert 0 < imm < 4096
    return hw(0xf2af | (((imm >> 11) & 1) << 10), (((imm >> 8) & 7) << 12) | (rd << 8) | (imm & 0xff))
HASH = 0x284eac; F = 0x249f84; CAVE = 0x1c3fe0; DRS = 0x400bbc; X = 0x400be6
# --- expected current state (v5.27+: F walks the table in place; cave = nacht/verruck/proto)
assert get(F + 0x1c, 4) == bw(F + 0x1c, CAVE + 6), get(F + 0x1c, 4).hex()
assert get(0x1c3fd0, 22) == b'nacht\0\0\0verruck\0proto\0'
assert get(DRS, 10) == b'derriese\0\0'
assert get(X - 8, 36) == b'\x89PNG\r\n\x1a\nUnknown compression type %d\0'
# --- X: r6 = wanted hash, stack holds F's push {r4-r6,lr}
x = adrw_neg(X, DRS)                       # adr.w r4, "derriese"
x += hw(0x4620) + blx_arm(X + 6, HASH)     # mov r0,r4 ; blx hash
x += hw(0x42b0, 0xbf04, 0x4620, 0xbd70)    # cmp r0,r6 ; itt eq ; moveq r0,r4 ; popeq {r4-r6,pc}
x += bw(X + len(x), CAVE + 6)              # b.w old cave (nacht / verruck / proto, unchanged)
assert len(x) == 22 and X + len(x) <= X + 28   # stays inside the 28-byte error text; the PNG signature before it is untouched
put(X, x)
put(F + 0x1c, bw(F + 0x1c, X))             # F 'not found' -> X
open(DST + '.raw', 'wb').write(raw)
fl = [{"id": lzma.FILTER_LZMA1, "dict_size": 64 * 1024, "lc": 3, "lp": 0, "pb": 2}]
out = bytearray(lzma.compress(bytes(raw), format=lzma.FORMAT_ALONE, filters=fl)); struct.pack_into('<Q', out, 5, len(raw))
assert lzma.decompress(bytes(out), format=lzma.FORMAT_ALONE) == bytes(raw)
open(DST, 'wb').write(out); print('ok', len(out))
