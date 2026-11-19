"""Der Riese Pack-a-Punch door, 2nd try (5R's spawn fix alone did not stop the crash).
DR_Door12 is the only Der Riese door with its own animation set (0x91e0b69d, 'open' anim kept in the level file)
and the only one unlocking the Pack-a-Punch zone. Make it exactly a Kino door: Kino's door animation set 0xdfbe538c
(the combination Kino's own doors use), and unlock only the start zone like every other Der Riese door.
in: 5R statics (spawn fix kept), out: fixed file"""
import sys, struct; sys.path.insert(0, '/root/work/drdeb'); from entlib import *
from propdump import comps
R = tlres.parse(open(sys.argv[1], 'rb').read()); L = {l['name']: l for l in R['lists']}
EL = L['0x78b2e3ec']['items']; k = [i for i, e in enumerate(EL) if name_of(bytes(e)) == 'DR_Door12']; assert len(k) == 1; k = k[0]
x = bytearray(bytes(EL[k]))
def poff(comp, prop): return [(p[4], p[3]) for c in comps(bytes(x)) if c[0] == comp for p in c[2] if p[1] == prop][0]
o, s = poff('CIsASMAnimator', 'ASM'); assert s == 4 and struct.unpack_from('<I', x, o)[0] == 0x91e0b69d; struct.pack_into('<I', x, o, 0xdfbe538c)
o, s = poff('CDoor', 'm_AreasUnlock'); assert struct.unpack_from('<3I', x, o) == (2, 0x721a06e4, 0x1abae938); struct.pack_into('<I', x, o + 8, 0x721a06e4)
assert len(x) == len(EL[k]); EL[k] = bytes(x)
out = tlres.write(R); open(sys.argv[2], 'wb').write(out); print('ok', len(out))
