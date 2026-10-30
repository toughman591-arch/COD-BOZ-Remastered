"""v5.6 game code (v5.5 + (h): Peter's grave: no prompt, dug up by looking at it once every door is bought; one grave) (on v5.0's boz.s3e): Shi No Numa ('proto') only, except (r).
 (a) trap switches power on by themselves on Shi No Numa (no power switch there): the switch's 'is powered' reads, in
     its use (0x24065c) and in the HUD prompt (0x1dab40), power it on with the powerTurnOn event (as v5.3).
 (b) weapon/arms set: 'proto' loads callofthedead's weapons (Wunderwaffe DG-2), at the 3 places the set name is built.
 (c) graves = the cost-0 wall buys: only after every door/debris is bought; each digs once (its 'grave_mound' part is
     hidden); the LAST grave dug gives the Wunderwaffe (hook 0x2557ce).
 (e) zipline: Call of the Dead's zipline 'open' flag is set on first use (0x25d640).
 (r) radios (all maps, v4.2 radio code): the track digit now cycles 1,2,3,4 -- track 4 is silence, i.e. 'off'.
v5.3's box-map crash was data (the dot), not code. Assembled from asm/p56.s with llvm-mc + ld.lld."""
import struct,lzma,subprocess,os
os.chdir('/root/work/v55/asm')
subprocess.run('llvm-mc -triple=thumbv7-none-eabi -filetype=obj p56.s -o p56.o && ld.lld -T p56.ld p56.o -o p56.elf 2>/dev/null',shell=True,check=True)
raw=bytearray(open('/root/work/v50/code/boz.s3e.raw','rb').read()); B=3
v40=open('/root/work/v40/boz.s3e.raw','rb').read()
def put(mem,b): raw[mem+B:mem+B+len(b)]=b
def get(mem,n): return bytes(raw[mem+B:mem+B+n])
def hw(*h): return b''.join(struct.pack('<H',x) for x in h)
syms={}
for l in subprocess.run(['llvm-nm','p56.elf'],capture_output=True,text=True).stdout.split('\n'):
    if l.strip(): a,t,n=l.split(); syms[n]=int(a,16)
secs={}
for l in subprocess.run(['llvm-readelf','-S','p56.elf'],capture_output=True,text=True).stdout.split('\n'):
    p=l.replace('[ ','[').split()
    if len(p)>6 and p[1].startswith('.cave') or len(p)>6 and p[1].startswith('.hook'):
        secs[p[1]]=(int(p[3],16),int(p[4],16),int(p[5],16))
elf=open('p56.elf','rb').read()
# ---- checks: hook sites hold what we expect, dead regions are pristine
assert get(0x24065c,4)==hw(0xf890,0x30a4)
assert get(0x1cbc40,8)==hw(0x286e,0xd306,0xbf00,0xbf00)
assert get(0x2557ce,4)==hw(0x4620,0xf8d4) and get(0x2557d2,2)==hw(0x5080)
assert get(0x25d640,4)==hw(0xf890,0x2064)
assert get(0x1dab40,4)==hw(0xf890,0x30a4)
assert get(0x1da0ae,4)==hw(0xf07b,0xfc43)      # bl GETCHALK in the HUD's wall-buy prompt
assert get(0x1cbc4e,4)==hw(0xf1d6,0xea94)      # the original blx strcpy
for a in (0x1e1e4c,0x1e1edc): assert get(a,8)==hw(0x286e,0xd306,0xbf00,0xbf00) and get(a+0xe,4)==hw(0xf1c0,0xe98e if a==0x1e1e4c else 0xe946)
DEAD={'.cave':(0xe48f0,0xe49dc),'.cave2':(0xec3e8,0xec4d4),'.cave3':(0x1b6488,0x1b64f8),'.cave4':(0x26fb44,0x26fba8)}
for n,(a,e) in DEAD.items():
    assert get(a,e-a)==v40[a+B:e+B]; assert n in ('.cave3','.cave4') or get(a,4)==hw(0xe92d,0x47f0)
    va,off,sz=secs[n]; assert va==a and a+sz<=e,(n,hex(a+sz),hex(e))
for n,(va,off,sz) in secs.items(): put(va,elf[off:off+sz])
assert syms['cave3_end']<=0x1b64f8 and syms['cave4_end']<=0x26fba8
assert get(0x26fb42,2)==hw(0xb570)   # the dead vector-resize function's first instruction (its body is the cave)
# ---- blx strcpy (ARM) in cave (b)
for sym in ('blx_at','blxw1','blxw2'):
    A=syms[sym]-4; T=0x3a2178; off=T-((A+4)&~3); assert off%4==0 and -(1<<24)<=off<(1<<24) and get(A,4)==hw(0xf000,0xc000)
    S=(off>>24)&1; I1=(off>>23)&1; I2=(off>>22)&1; J1=(1-I1)^S; J2=(1-I2)^S
    put(A,hw(0xf000|(S<<10)|((off>>12)&0x3ff),0xc000|(J1<<13)|(J2<<11)|(((off>>2)&0x3ff)<<1)))
# ---- (r) radio cycle 1..4 (RADIO cave from v4.2: adds r2,#1; cmp r2,#'4'; it cs; movcs r2,#'1')
assert get(0x1b62f0,8)==hw(0x3201,0x2a34,0xbf28,0x2231),get(0x1b62e8,16).hex()
put(0x1b62f2,hw(0x2a35))
os.makedirs('/root/work/v55/code',exist_ok=True)
open('/root/work/v55/code/boz.s3e.raw','wb').write(raw); open('/root/work/v55/code/code56.bin','wb').write(raw[B:])
f=[{"id":lzma.FILTER_LZMA1,"dict_size":64*1024,"lc":3,"lp":0,"pb":2}]
cc=bytearray(lzma.compress(bytes(raw),format=lzma.FORMAT_ALONE,filters=f)); struct.pack_into('<Q',cc,5,len(raw))
assert lzma.decompress(bytes(cc),format=lzma.FORMAT_ALONE)==bytes(raw)
open('/root/work/v55/code/boz.s3e','wb').write(cc)
print('ok',len(cc),{n:(hex(v),sz) for n,(v,o,sz) in secs.items()})
