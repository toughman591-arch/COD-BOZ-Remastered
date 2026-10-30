"""v5.26 Mali data = v5.25 data + Shi No Numa env (no log frame) + statics (electric trap only), Verruckt Speed Cola, co-op menu."""
import sys,os,shutil
sys.path.insert(0,'/root/tools'); sys.path.insert(0,'/root/work/v39')
import grp2,dzwrite,dz
import build_mali as BM
src=open('/root/work/v44/build_mali46.py').read(); exec(src[src.index('def merge'):src.index("O='/root/work/v42/out'")])
rep={}
env=open('/root/work/v516/proto_env_final_525.group.bin','rb').read(); assert not BM.has_atc(env)
rep[('levels\\proto','proto_env.group.bin')]=env
d,st=merge('levels/kino/kino_statics.group.bin',open('/root/work/v55/out/levels/proto/proto_statics.group.bin','rb').read()); print('proto statics',st)
rep[('levels\\proto','proto_statics.group.bin')]=d
rep[('levels\\verruck','verruck_statics.group.bin')]=open('/root/work/v526/verruck_statics.group.bin','rb').read()
rep[('frontend','fe_v4_cs4_swf.bin')]=open('/root/work/v526/fe/fe526.swf','rb').read()
OUT='/root/work/out/blackops_mali_v528.dz'
print(dzwrite.build('/root/work/out/blackops_mali_v525.dz',OUT,rep,{}))
chk='/root/work/v526/chk'; shutil.rmtree(chk,ignore_errors=True); dz.extract(OUT,chk)
for (dn,fn),dd in rep.items(): assert open(f"{chk}/{dn.replace(chr(92),'/')}/{fn}",'rb').read()==dd,fn
X='/root/work/v526/x'; n=diff=0
for r,_,fs in os.walk(X):
    for f in fs:
        rel=os.path.relpath(os.path.join(r,f),X); n+=1
        if open(os.path.join(r,f),'rb').read()!=open(os.path.join(chk,rel),'rb').read(): diff+=1; print('changed',rel)
n2=sum(len(fs) for _,_,fs in os.walk(chk)); print('files',n,n2,'changed',diff); shutil.rmtree(chk)
print('size',os.path.getsize(OUT),hex(os.path.getsize(OUT)))
