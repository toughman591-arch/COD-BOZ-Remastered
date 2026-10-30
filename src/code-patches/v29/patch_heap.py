# Raise the game's fixed Marmalade heap: MemSize = ExtraMemorySize + 76000000  ->  + 176000000
# (embedded icf inside boz.s3e). Total length kept identical by dropping one tab from a dev-only line just above.
import lzma,struct
src=open('/root/work/dec/assets/boz.s3e','rb').read()
raw=bytearray(lzma.decompress(src,format=lzma.FORMAT_ALONE))
assert bytes(raw)==open('/root/work/nacht/boz.s3e.raw','rb').read()
A=b'HeapAnalyserBlocks\t\t=\t100000\r\n{}\r\n[S3E]\r\nMemSize = [GAME] ExtraMemorySize + 76000000\r\n'
B=b'HeapAnalyserBlocks\t=\t100000\r\n{}\r\n[S3E]\r\nMemSize = [GAME] ExtraMemorySize + 176000000\r\n'
assert len(A)==len(B) and raw.count(A)==1
i=raw.find(A); raw[i:i+len(A)]=B
open('/root/work/v29/boz.s3e.raw','wb').write(raw)
f=[{"id":lzma.FILTER_LZMA1,"dict_size":64*1024,"lc":3,"lp":0,"pb":2}]
c=bytearray(lzma.compress(bytes(raw),format=lzma.FORMAT_ALONE,filters=f)); struct.pack_into('<Q',c,5,len(raw))
assert lzma.decompress(bytes(c),format=lzma.FORMAT_ALONE)==bytes(raw)
# same container header as the shipped file (props + size)
assert c[:13]==src[:13],(c[:13].hex(),src[:13].hex())
open('/root/work/v29/boz.s3e','wb').write(c); print('ok',len(src),len(c))
