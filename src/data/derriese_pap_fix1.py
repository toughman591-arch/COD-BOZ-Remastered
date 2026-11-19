"""Der Riese: buying the Pack-a-Punch door (DR_Door12) crashed. It unlocks area 0x1abae938, the only area in any map with
no zombie spawn points. Give that area one spawn point (DR_ZombieSpawn02, the nearest, already active in the start area).
in: base derriese_statics, out: fixed file"""
import sys, struct; sys.path.insert(0, '/root/work/drdeb'); from entlib import *
R = tlres.parse(get('levels\\derriese', 'derriese_statics.group.bin')); L = {l['name']: l for l in R['lists']}
A = L['0xf359d21']['items']; PAP, SP = 0x1abae938, 0x3454190b
k = [i for i, x in enumerate(A) if struct.unpack_from('<I', bytes(x), 4)[0] == PAP]; assert len(k) == 1; k = k[0]
x = bytearray(bytes(A[k])); assert len(x) == 56 and struct.unpack_from('<6I', x, 0)[0::5] == (56, 44) and struct.unpack_from('<I', x, 8)[0] == 44
assert struct.unpack_from('<II', x, 48) == (4, 0)
ref = bytes(A[0]); assert struct.unpack_from('<II', ref, 48) == (24, 5) and struct.unpack_from('<I', ref, 0)[0] == 76   # layout check: bytes = 4 + 4*count
struct.pack_into('<I', x, 0, 60); struct.pack_into('<I', x, 8, 48); struct.pack_into('<I', x, 20, 48); struct.pack_into('<II', x, 48, 8, 1)
x += struct.pack('<I', SP); A[k] = bytes(x)
EL = [bytes(e) for e in L['0x78b2e3ec']['items']]; assert any(struct.unpack_from('<I', e, 4)[0] == SP and name_of(e) == 'DR_ZombieSpawn02' for e in EL)
out = tlres.write(R); open(sys.argv[1], 'wb').write(out)
R2 = tlres.parse(out); a2 = [bytes(y) for y in [l for l in R2['lists'] if l['name'] == '0xf359d21'][0]['items']]
assert a2[k] == bytes(x) and len(out) == len(get('levels\\derriese', 'derriese_statics.group.bin')) + 4
print('ok', len(out))
