import struct,lzma
raw=bytearray(open('/root/work/bin/boz.s3e.raw','rb').read())
B=3
def put(mem,hexs):
    b=bytes.fromhex(hexs); raw[mem+B:mem+B+len(b)]=b
def expect(mem,hexs):
    b=bytes.fromhex(hexs); assert raw[mem+B:mem+B+len(b)]==b,(hex(mem),raw[mem+B:mem+B+len(b)].hex(),hexs)
# halfwords little-endian
def hw(*h): return ''.join(struct.pack('<H',x).hex() for x in h)
# Site A 0x1cbc3c: ldr r1,=tutorial; mov r0,r5; add r1,pc; blx strcmp; cbnz r0,skip
expect(0x1cbc3c, hw(0x498e,0x4628,0x4479)+'d6f15ae9'+hw(0xb920))
put(0x1cbc3c, hw(0x6828,0xb2c0,0x2870,0xd306,0xbf00,0xbf00))   # ldr r0,[r5]; uxtb; cmp #'p'; bcc skip; nop; nop
# Site B 0x1e1e46
expect(0x1e1e46, hw(0x491a,0x4668,0x447e,0x4479)+'e4f735f9'+hw(0xb120))
put(0x1e1e46, hw(0x9800,0xb2c0,0x447e,0x2870,0xd306,0xbf00,0xbf00))
# Site C 0x1e1ed6
expect(0x1e1ed6, hw(0x491a,0x4668,0x447e,0x4479)+'e4f7edf8'+hw(0xb120))
put(0x1e1ed6, hw(0x9800,0xb2c0,0x447e,0x2870,0xd306,0xbf00,0xbf00))
# Site D 0x1c4000: SINGLEPLAYER_START only accepted the 5 stock maps (bne -> return). Let any registered map start.
expect(0x1c3ffe, hw(0x4580,0xd110,0xe017))
put(0x1c4000, hw(0xbf00))
open('/root/work/ow/boz.s3e.raw','wb').write(raw)
f=[{"id":lzma.FILTER_LZMA1,"dict_size":64*1024,"lc":3,"lp":0,"pb":2}]
c=bytearray(lzma.compress(bytes(raw),format=lzma.FORMAT_ALONE,filters=f))
struct.pack_into('<Q',c,5,len(raw))
open('/root/work/ow/boz.s3e','wb').write(c)
assert lzma.decompress(bytes(c),format=lzma.FORMAT_ALONE)==bytes(raw)
print('ok',len(c))
