"""Mule Kick v2: localised string 'Mule Kick' (id S_BLACKOPS_MULE_KICK) added to every language + the hash lookup."""
import sys,struct,bisect
sys.path.insert(0,'/root/work/rx'); from iwh import iwh
SRC='/root/work/v526/x/localisation/'; OUT='/root/work/mule2/data/'
ID=iwh('S_BLACKOPS_MULE_KICK'); TEXT=b'Mule Kick'
h=open(SRC+'LocaliseHashes.dat','rb').read()
assert h[:4]==b'LOC0'; n=struct.unpack_from('<H',h,4)[0]; assert len(h)==6+6*n
H=list(struct.unpack_from('<%dI'%n,h,6)); I=list(struct.unpack_from('<%dH'%n,h,6+4*n))
assert H==sorted(H) and ID not in H
p=bisect.bisect_left(H,ID); H.insert(p,ID); I.insert(p,n)
open(OUT+'LocaliseHashes.dat','wb').write(b'LOC0'+struct.pack('<H',n+1)+struct.pack('<%dI'%(n+1),*H)+struct.pack('<%dH'%(n+1),*I))
langs=['english_us','english_uk','french','german','italian','spanish']
for L in langs:
    d=open(SRC+L+'.dat','rb').read()
    tag,a,b,cnt=struct.unpack_from('<4sIII',d,0); assert tag==b'LOC0' and cnt==n
    off=list(struct.unpack_from('<%dI'%n,d,16)); enc_at=16+4*n
    enc_end=d.index(b'\0',enc_at)+1; enc=d[enc_at:enc_end]; assert enc in (b'utf-8\0',b'latin-1\0'),enc
    strings=d[enc_end:]; assert len(strings)==b, (L,len(strings),b)
    slack=a-(n+4)*4-b; assert slack>=0
    off.append(len(strings)); strings+=TEXT+b'\0'
    nb=len(strings); na=(n+1+4)*4+nb+slack
    out=struct.pack('<4sIII',b'LOC0',na,nb,n+1)+struct.pack('<%dI'%(n+1),*off)+enc+strings
    open(OUT+L+'.dat','wb').write(out); print(L,len(d),'->',len(out),'slack',slack)
print('id',hex(ID),'index',n)
