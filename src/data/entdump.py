import sys,re,struct; sys.path.insert(0,'/root/tools')
import grp2,ent2
from hashes import djb2
code=open('/root/work/v526/code/code526.bin','rb').read()
D={}
for m in re.finditer(rb'[\x20-\x7e]{2,}',code):
    s=m.group().decode(); D.setdefault(djb2(s.lower()),s)
def nm(h): return D.get(h,hex(h))
def dump(path,filt=None):
    g=grp2.parse(open(path,'rb').read())
    for e in grp2.find(g,'CIsEntitySpec')[2]:
        n=ent2.name(e)
        if filt and not filt(n or ''): continue
        _,cs,_=ent2.comps(e); print('==',n,[nm(c['cls']) for c in cs])
        for c in cs:
            for q in ent2.props(e,c):
                v=e[q['val']:q['val']+q['vsize']]
                print('   ',nm(c['cls']),nm(q['prop']),nm(q['type']),v.hex() if len(v)<=40 else v[:40].hex()+'...')
if __name__=='__main__':
    import fnmatch
    dump(sys.argv[1],lambda n:any(k.lower() in n.lower() for k in sys.argv[2].split(',')))
