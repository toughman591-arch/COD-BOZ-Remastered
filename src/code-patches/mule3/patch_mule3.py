"""Mule Kick v3 (lit machine, online off, saved 3rd gun; max ammo, own icon/name, perk loss takes the 3rd gun): game code on top of v5.29's boz.s3e (asm/mule.s, linked with asm/mule.ld)."""
import struct,lzma,subprocess,os
os.chdir('/root/work/mule3/asm')
subprocess.run('llvm-mc -triple=thumbv7-none-eabi -filetype=obj mule.s -o mule.o && ld.lld -T mule.ld mule.o -o mule.elf 2>/dev/null',shell=True,check=True)
raw=bytearray(open('/root/work/v526/code/boz.s3e.raw','rb').read()); B=3
def put(mem,b): raw[mem+B:mem+B+len(b)]=b
def get(mem,n): return bytes(raw[mem+B:mem+B+n])
def hw(*h): return b''.join(struct.pack('<H',x) for x in h)
secs={}
for l in subprocess.run(['llvm-readelf','-S','mule.elf'],capture_output=True,text=True).stdout.split('\n'):
    p=l.replace('[ ','[').split()
    if len(p)>6 and (p[1].startswith('.mcave') or p[1].startswith('.hook')): secs[p[1]]=(int(p[3],16),int(p[4],16),int(p[5],16))
elf=open('mule.elf','rb').read()
assert get(0x2597c8,6)==hw(0xf8d4,0x21e0,0x42aa)
assert get(0x259750,6)==hw(0xf8d4,0x11e4,0xe7ea)
assert get(0x258234,4)==hw(0x2000,0xe001)
assert get(0x257a34,4)==hw(0xf7ad,0xfc47) and get(0x20d152,4)==hw(0xf7f8,0xf8b8)
assert get(0x400a40,0x40)==b'Application uses deprecated png_write_init() and should be recom'
assert get(0x204df4,6)==hw(0x4808,0x4478,0x4770)
assert get(0x204f44,4)==hw(0x7a03,0x60c1)
assert get(0x20533e,4)==hw(0x460d,0x4616)
assert get(0x2584d6,4)==hw(0x4b03,0x447b)
assert get(0x3d948c,0xd0)==open('/root/work/rx/orig.s3e.unpacked','rb').read()[0x3d948c+3:0x3d948c+3+0xd0] and get(0x3d948c,8)==b'unsuppor'
assert get(0x204bee,4)==hw(0xf8d4,0x00c8)
assert get(0x203fd6,6)==hw(0xf8d4,0x3088,0xb1fb)
assert get(0x25c170,4)==hw(0x3504,0x2d14)
assert get(0x25c216,4)==hw(0x2d05,0xd01e)
va2,off2,sz2=secs['.mcave2']; assert va2==0x3d9490 and va2+sz2<=0x3d975c
va,off,sz=secs['.mcave']; assert va==0x400a40 and va+sz<=0x400bde, hex(va+sz)
assert get(0x400bde,8)==b'\x89PNG\r\n\x1a\n'
for n,(va,off,sz) in secs.items(): put(va,elf[off:off+sz])
open('/root/work/mule3/code/boz.s3e.raw','wb').write(raw)
f=[{"id":lzma.FILTER_LZMA1,"dict_size":64*1024,"lc":3,"lp":0,"pb":2}]
cc=bytearray(lzma.compress(bytes(raw),format=lzma.FORMAT_ALONE,filters=f)); struct.pack_into('<Q',cc,5,len(raw))
assert lzma.decompress(bytes(cc),format=lzma.FORMAT_ALONE)==bytes(raw)
open('/root/work/mule3/code/boz.s3e','wb').write(cc); print('ok',len(cc),{n:(hex(v),sz) for n,(v,o,sz) in secs.items()})
