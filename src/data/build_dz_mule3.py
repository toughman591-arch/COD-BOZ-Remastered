import sys,os,shutil
sys.path.insert(0,'/root/tools'); sys.path.insert(0,'/root/work/v39')
import dzwrite,dz
D='/root/work/mule2/data/'
rep={('levels\\kino','kino_statics.group.bin'):open('/root/work/mule3/data/kino_statics.group.bin','rb').read(),
     ('ingame','ingame.group.bin'):open(D+'ingame.group.bin','rb').read()}
for f in ['LocaliseHashes.dat','english_us.dat','english_uk.dat','french.dat','german.dat','italian.dat','spanish.dat']:
    rep[('localisation',f)]=open(D+f,'rb').read()
OUT='/root/work/out/blackops_mali_mule3.dz'
print(dzwrite.build('/root/work/out/blackops_mali_v528.dz',OUT,rep,{}))
chk='/root/work/mule3/chk'; shutil.rmtree(chk,ignore_errors=True); dz.extract(OUT,chk)
for (dn,fn),d in rep.items(): assert open(f"{chk}/{dn.replace(chr(92),'/')}/{fn}",'rb').read()==d,fn
X='/root/work/v526/x'; diff=[]
for r,_,fs in os.walk(X):
    for f in fs:
        rel=os.path.relpath(os.path.join(r,f),X)
        if open(os.path.join(r,f),'rb').read()!=open(os.path.join(chk,rel),'rb').read(): diff.append(rel)
print('changed vs v5.25-extract',diff); shutil.rmtree(chk)
print('size',os.path.getsize(OUT))
