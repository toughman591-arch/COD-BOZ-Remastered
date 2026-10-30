"""v4.2 game code (on v4.0's boz.s3e): Nacht radio cycles WaW radio tracks 1-2-3, each looping.
The easter-egg manager's 'slashed' handler now calls RADIO (written over the egg manager's co-op state-sync writer,
whose two calls are removed: easter-egg progress is no longer copied to players who join mid-game).
RADIO: if the group name is 'blackops-music/nacht_radio<d>.mp3' -> d = 1,2,3,1,...; play it looping (repeat 0) with a
crossfade; otherwise -> the original group-complete check (0x1b6298), unchanged for Kino / Ascension / Call of the Dead."""
import struct,lzma,subprocess
raw=bytearray(open('/root/work/v40/boz.s3e.raw','rb').read()); B=3
def put(mem,b): raw[mem+B:mem+B+len(b)]=b
def get(mem,n): return bytes(raw[mem+B:mem+B+n])
def hw(*h): return b''.join(struct.pack('<H',x) for x in h)
def bl(src,dst):
    off=dst-(src+4); assert -(1<<24)<=off<(1<<24) and off%2==0
    S=(off>>24)&1; I1=(off>>23)&1; I2=(off>>22)&1; J1=(1-I1)^S; J2=(1-I2)^S
    return hw(0xf000|(S<<10)|((off>>12)&0x3ff), 0xd000|(J1<<13)|(J2<<11)|((off>>1)&0x7ff))
def bcond_w(src,dst,cond):
    off=dst-(src+4); assert -(1<<20)<=off<(1<<20) and off%2==0
    S=(off>>20)&1; J2=(off>>19)&1; J1=(off>>18)&1
    return hw(0xf000|(S<<10)|(cond<<6)|((off>>12)&0x3f), 0x8000|(J1<<13)|(J2<<11)|((off>>1)&0x7ff))
F_ORIG=0x1b6298; PLAY=0x1f319c; A=0x1b62d8; MM=0x49cad4
# ---- checks: we are patching what we think we are
assert get(0x1b655e,4)==bl(0x1b655e,F_ORIG), get(0x1b655e,4).hex()
assert get(0x1b656e,4)==bl(0x1b656e,0x1b62d8), get(0x1b656e,4).hex()
assert get(0x1b657e,4)==bl(0x1b657e,0x1b6438), get(0x1b657e,4).hex()
assert get(0x1b62ca,4)==bl(0x1b62ca,PLAY)
assert get(A,6)==hw(0xb5f8,0x4607,0x4b1e)                           # start of the state-sync writer
lit=struct.unpack('<I',get(0x1b62d4,4))[0]; assert lit+0x1b62c4==MM   # music manager global used by the original code
# ---- RADIO
c=bytearray(); at=lambda: A+len(c)
c+=hw(0x68cb)                       # ldr  r3,[r1,#0xc]      group name
c+=hw(0x7d5a)                       # ldrb r2,[r3,#21]
c+=hw(0x2a72)                       # cmp  r2,#'r'
c+=bcond_w(at(),F_ORIG,1)           # bne.w original check
c+=hw(0x7e5a)                       # ldrb r2,[r3,#25]
c+=hw(0x2a6f)                       # cmp  r2,#'o'
c+=bcond_w(at(),F_ORIG,1)           # bne.w original check
c+=hw(0xb510)                       # push {r4,lr}
c+=hw(0xb082)                       # sub  sp,#8
c+=hw(0x7e9a)                       # ldrb r2,[r3,#26]        digit
c+=hw(0x3201)                       # adds r2,#1
c+=hw(0x2a34)                       # cmp  r2,#'4'
c+=hw(0xbf28)                       # it   cs
c+=hw(0x2231)                       # movcs r2,#'1'
c+=hw(0x769a)                       # strb r2,[r3,#26]
c+=hw(0xf04f,0x527e)                # mov.w r2,#0x3f800000   volume 1.0
c+=hw(0x9200)                       # str  r2,[sp]
c+=hw(0x2200)                       # movs r2,#0             repeat 0 = loop forever
c+=hw(0x9201)                       # str  r2,[sp,#4]        no lock
c+=hw(0x4619)                       # mov  r1,r3             name
ldr_at=at(); c+=hw(0x4800)          # ldr  r0,[pc,#imm]  (fixed below)
add_at=at(); c+=hw(0x4478)          # add  r0,pc
c+=hw(0x6800)                       # ldr  r0,[r0]           music manager
c+=hw(0x2300)                       # movs r3,#0             crossfade into the new track
c+=bl(at(),PLAY)                    # bl   CMusicManager::Play
c+=hw(0xb002)                       # add  sp,#8
c+=hw(0xbd10)                       # pop  {r4,pc}
if at()%4: c+=hw(0xbf00)
lit_at=at(); c+=struct.pack('<I',MM-(add_at+4))
imm=(lit_at-((ldr_at+4)&~3)); assert imm%4==0 and 0<=imm<1024; struct.pack_into('<H',c,ldr_at-A,0x4800|(imm>>2))
assert at()<=0x1b6360,hex(at())
put(A,bytes(c))
put(0x1b655e,bl(0x1b655e,A))                                        # slashed -> RADIO
put(0x1b656e,hw(0xbf00,0xbf00)); put(0x1b657e,hw(0xbf00,0xbf00))    # no easter-egg state sync (writer / reader)
open('/root/work/v42/code/boz.s3e.raw','wb').write(raw); open('/root/work/v42/code/code42.bin','wb').write(raw[B:])
f=[{"id":lzma.FILTER_LZMA1,"dict_size":64*1024,"lc":3,"lp":0,"pb":2}]
cc=bytearray(lzma.compress(bytes(raw),format=lzma.FORMAT_ALONE,filters=f)); struct.pack_into('<Q',cc,5,len(raw))
assert lzma.decompress(bytes(cc),format=lzma.FORMAT_ALONE)==bytes(raw)
open('/root/work/v42/code/boz.s3e','wb').write(cc); print('ok',len(cc),'RADIO',hex(A),'-',hex(at()))
