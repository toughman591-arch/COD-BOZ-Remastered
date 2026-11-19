"""Five intro trigger: the single-player intro hook picks 'boz_c' for maps starting 'ca', 'boz_k' for 'ki'; add 'pe'
(pentagon = Five) -> blackops-music/boz_f.mp3. New check lives in libpng's never-shown 'Incompatible libpng version...'
error text (0x400a0a), reached from the old 'is it k?' test."""
import struct, lzma, sys
SRC, DST = sys.argv[1], sys.argv[2]
raw = bytearray(lzma.decompress(open(SRC, 'rb').read(), format=lzma.FORMAT_ALONE)); B = 3
def put(m, b): raw[m + B:m + B + len(b)] = b
def get(m, n): return bytes(raw[m + B:m + B + n])
def hw(*h): return b''.join(struct.pack('<H', x) for x in h)
def bw(src, dst, link=False):
    off = dst - (src + 4); assert -(1 << 24) <= off < (1 << 24) and off % 2 == 0
    S = (off >> 24) & 1; I1 = (off >> 23) & 1; I2 = (off >> 22) & 1; J1 = (1 - I1) ^ S; J2 = (1 - I2) ^ S
    return hw(0xf000 | (S << 10) | ((off >> 12) & 0x3ff), (0xd000 if link else 0x9000) | (J1 << 13) | (J2 << 11) | ((off >> 1) & 0x7ff))
def adrw(at, target, rd):
    base = (at + 4) & ~3; imm = target - base; assert 0 <= imm < 4096
    return hw(0xf20f | (((imm >> 11) & 1) << 10), (((imm >> 8) & 7) << 12) | (rd << 8) | (imm & 0xff))
HOOK = 0x1b632e; CAVE = 0x400a0a
assert get(HOOK, 4) == hw(0x286b, 0xd110), get(HOOK, 4).hex()          # cmp r0,#'k' ; bne 0x1b6354
assert get(0x1b6332, 2) == hw(0x2a69) and get(0x1b6338, 2) == hw(0xb082) and get(0x1b6354, 2) == hw(0xbd1f)
TXT = b'Incompatible libpng version in application and library\0'; assert get(0x400a09, len(TXT)) == TXT
S = b'blackops-music/boz_f.mp3\0'
c = CAVE; code = b''
def emit(b):
    global code; code += b
emit(hw(0x286b))                      # cmp r0, #'k'
emit(hw(0xd101))                      # bne.n +2 (skip the b.w)
emit(bw(c + len(code), 0x1b6332))     # b.w -> old 'i' test
emit(hw(0x2870))                      # cmp r0, #'p'
emit(hw(0xd105))                      # bne.n exit
emit(hw(0x2a65))                      # cmp r2, #'e'
emit(hw(0xd103))                      # bne.n exit
str_at = c + 28
emit(adrw(c + len(code), str_at, 1))  # adr.w r1, "blackops-music/boz_f.mp3"
emit(bw(c + len(code), 0x1b6338))     # b.w -> play it (same as boz_c/boz_k)
assert len(code) == 24
emit(bw(c + len(code), 0x1b6354))     # exit: no intro
assert len(code) == 28 and c + 28 + len(S) <= 0x400a40
put(CAVE, code + S); put(HOOK, bw(HOOK, CAVE))
# bne.n offsets: from 0x400a0c, target 0x400a12 = +2 ; 0x400a14 -> exit 0x400a26: (0x400a26-(0x400a14+4))/2=7?
open(DST + '.raw', 'wb').write(raw)
fl = [{"id": lzma.FILTER_LZMA1, "dict_size": 64 * 1024, "lc": 3, "lp": 0, "pb": 2}]
out = bytearray(lzma.compress(bytes(raw), format=lzma.FORMAT_ALONE, filters=fl)); struct.pack_into('<Q', out, 5, len(raw))
assert lzma.decompress(bytes(out), format=lzma.FORMAT_ALONE) == bytes(raw); open(DST, 'wb').write(out); print('ok')
