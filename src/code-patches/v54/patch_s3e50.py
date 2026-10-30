"""v5.0 game code (on v4.2's boz.s3e): on the 'proto' level (Shi No Numa) every perk machine starts powered
(Shi No Numa has no power switch). Hook at the perk init's solo Quick Revive check (0x203fe2):
  type 5 (Quick Revive)          -> the original solo Quick Revive path, unchanged
  level name starts with 'pr'    -> powered = 1 and the same 'powered' event the power switch sends
  anything else                  -> unchanged (no power until the switch)
The cave is written over the easter-egg co-op state reader (0x1b6438), which v4.2 already made unreachable."""
import struct,lzma
raw=bytearray(open('/root/work/v42/code/boz.s3e.raw','rb').read()); B=3
def put(mem,b): raw[mem+B:mem+B+len(b)]=b
def get(mem,n): return bytes(raw[mem+B:mem+B+n])
def hw(*h): return b''.join(struct.pack('<H',x) for x in h)
def bl(src,dst,link=True):
    off=dst-(src+4); assert -(1<<24)<=off<(1<<24) and off%2==0
    S=(off>>24)&1; I1=(off>>23)&1; I2=(off>>22)&1; J1=(1-I1)^S; J2=(1-I2)^S
    return hw(0xf000|(S<<10)|((off>>12)&0x3ff), (0xd000 if link else 0x9000)|(J1<<13)|(J2<<11)|((off>>1)&0x7ff))
def bw(src,dst): return bl(src,dst,False)
def bcond_w(src,dst,cond):
    off=dst-(src+4); assert -(1<<20)<=off<(1<<20) and off%2==0
    S=(off>>20)&1; J2=(off>>19)&1; J1=(off>>18)&1
    return hw(0xf000|(S<<10)|(cond<<6)|((off>>12)&0x3f), 0x8000|(J1<<13)|(J2<<11)|((off>>1)&0x7ff))
HOOK=0x203fe2; QR=0x203fea; OUT=0x20401c; POST=0xfa778; LM=0x499cc0; CAVE=0x1b6438; CAVE_END=0x1b64f8
# ---- checks
assert get(HOOK,8)==hw(0xf8d4,0x30b0,0x2b05,0xd118)          # ldr.w r3,[r4,#0xb0]; cmp r3,#5; bne 0x20401c
assert get(QR,0x1e)==hw(0x2301,0xf884,0x307d,0xf884,0x307c,0x4628,0x4b32,0x4642,0xf8cd,0x8000,0x447b,0x69d9,0x4643)+bl(0x204004,POST)
lit=struct.unpack('<I',get(0x2040c0,4))[0]; EVT=(lit+0x204002)&0xffffffff   # the original's r3 (event table) before ldr r1,[r3,#0x1c]
assert get(0x1b657e,4)==hw(0xbf00,0xbf00)                     # v4.2: reader call removed
assert get(CAVE,4)==hw(0x4b2d,0xe92d)                         # reader still there, unreferenced
# ---- cave
c=bytearray(); at=lambda: CAVE+len(c); fix=[]
c+=hw(0xf8d4,0x30b0)                 # ldr.w r3,[r4,#0xb0]     perk type
c+=hw(0x2b05)                        # cmp   r3,#5
c+=bcond_w(at(),QR,0)                # beq.w Quick Revive path
fix.append((at(),LM)); c+=hw(0x4b00) # ldr   r3,[pc,#lit]
fa=at(); c+=hw(0x447b)               # add   r3,pc
fix[-1]=(fix[-1][0],fa,LM)
c+=hw(0x681b)                        # ldr   r3,[r3]           level manager
c+=hw(0x2b00)                        # cmp   r3,#0
c+=bcond_w(at(),OUT,0)               # beq.w out
c+=hw(0xf893,0x2055)                 # ldrb.w r2,[r3,#0x55]    level name[0]
c+=hw(0x2a70)                        # cmp   r2,#'p'
c+=bcond_w(at(),OUT,1)               # bne.w out
c+=hw(0xf893,0x2056)                 # ldrb.w r2,[r3,#0x56]    level name[1]
c+=hw(0x2a72)                        # cmp   r2,#'r'
c+=bcond_w(at(),OUT,1)               # bne.w out
c+=hw(0x2301)                        # movs  r3,#1
c+=hw(0xf884,0x307c)                 # strb.w r3,[r4,#0x7c]    powered
fix.append((at(),)); c+=hw(0x4b00)   # ldr   r3,[pc,#lit]
fa2=at(); c+=hw(0x447b)              # add   r3,pc
fix[-1]=(fix[-1][0],fa2,EVT)
c+=hw(0x4628)                        # mov   r0,r5             this+0x20 (event target)
c+=hw(0x4642)                        # mov   r2,r8             0 in solo
c+=hw(0xf8cd,0x8000)                 # str.w r8,[sp]
c+=hw(0x69d9)                        # ldr   r1,[r3,#0x1c]     'powered' event
c+=hw(0x4643)                        # mov   r3,r8
c+=bl(at(),POST)                     # bl    post event (as the power switch handler does)
c+=bw(at(),OUT)                      # b.w   out (light / rest of init)
if at()%4: c+=hw(0xbf00)
for ldr_at,add_at,val in fix:
    la=at(); c+=struct.pack('<I',(val-(add_at+4))&0xffffffff)
    imm=la-((ldr_at+4)&~3); assert imm%4==0 and 0<=imm<1024
    struct.pack_into('<H',c,ldr_at-CAVE,0x4b00|(imm>>2))
assert at()<=CAVE_END,hex(at())
put(CAVE,bytes(c)); put(HOOK,bw(HOOK,CAVE))
import os; os.makedirs('/root/work/v54/code',exist_ok=True)
open('/root/work/v54/code/boz.s3e.raw','wb').write(raw); open('/root/work/v54/code/code50.bin','wb').write(raw[B:])
f=[{"id":lzma.FILTER_LZMA1,"dict_size":64*1024,"lc":3,"lp":0,"pb":2}]
cc=bytearray(lzma.compress(bytes(raw),format=lzma.FORMAT_ALONE,filters=f)); struct.pack_into('<Q',cc,5,len(raw))
assert lzma.decompress(bytes(cc),format=lzma.FORMAT_ALONE)==bytes(raw)
open('/root/work/v54/code/boz.s3e','wb').write(cc); print('ok',len(cc),'cave',hex(CAVE),'-',hex(at()),'EVT',hex(EVT))
