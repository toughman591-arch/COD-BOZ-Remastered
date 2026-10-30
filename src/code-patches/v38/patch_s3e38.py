import struct,lzma
raw=bytearray(open('/root/work/v37/boz.s3e.raw','rb').read())   # v3.7 code
B=3
def put(mem,b): raw[mem+B:mem+B+len(b)]=b
def get(mem,n): return bytes(raw[mem+B:mem+B+n])
# 1) always open blackops_atitc.dz (the game picked blackops_<gpu format>.dz; on some devices that is
#    blackops_etc.dz, which made a second 345 MB copy necessary). Point the sprintf format at the
#    existing "blackops_atitc.dz" string (no %s, the extra argument is ignored).
assert get(0x3f3f12,15)==b'blackops_%s.dz\0' and get(0x3ecdf4,18)==b'blackops_atitc.dz\0'
lit=0x228914; assert struct.unpack('<I',get(lit,4))[0]==0x3f3f12-0x22889a
put(lit,struct.pack('<I',0x3ecdf4-0x22889a))
open('/root/work/v38/boz.s3e.raw','wb').write(raw)
f=[{"id":lzma.FILTER_LZMA1,"dict_size":64*1024,"lc":3,"lp":0,"pb":2}]
c=bytearray(lzma.compress(bytes(raw),format=lzma.FORMAT_ALONE,filters=f)); struct.pack_into('<Q',c,5,len(raw))
assert lzma.decompress(bytes(c),format=lzma.FORMAT_ALONE)==bytes(raw)
open('/root/work/v38/boz.s3e','wb').write(c); print('ok',len(c))
