import glob,os,sys,re
sys.path.insert(0,'/root/tools')
import tex
from hashes import djb2
X='/root/work/ximg/ximages'
def cands(fn):
    n=fn[:-4]
    base=None
    if n.startswith('~-g'): base=n[3:]
    elif not n.startswith('~'): base=n
    if not base or '~' in base: return None,[]
    base=base.split('#')[0]
    c={base}
    for suf in ['_c','_d','_col','_dif']:
        if base.endswith(suf): c.add(base[:-len(suf)])
    out=set()
    for b in c:
        for v in [b,b+'.tga',b+'.png',b+'.dds',b+'.bmp',b+'_atitc',b+'_dxt']: out.add(v.lower())
    return base,out
alltex={}
for f in glob.glob('/root/work/dz/**/*.group.bin',recursive=True):
    d=open(f,'rb').read()
    for t in tex.scan(d):
        t['file']=os.path.relpath(f,'/root/work/dz'); alltex.setdefault(t['hash'],[]).append(t)
print('unique tex hashes',len(alltex))
matches={}
for fn in sorted(os.listdir(X)):
    base,cs=cands(fn)
    for c in cs:
        h=djb2(c)
        if h in alltex:
            matches[fn]=(c,alltex[h])
for fn,(c,ts) in matches.items():
    print(fn,'->',c,[(t['file'],t['w'],t['h'],hex(t['glf'])) for t in ts])
print(len(matches))
