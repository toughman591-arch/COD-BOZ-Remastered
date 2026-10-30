import sys,struct,pickle
sys.path.insert(0,'/root/tools')
import resgrp
D=pickle.load(open('/root/tools/hashdict.pkl','rb'))
NAMEPROP=bytes.fromhex('460c9b7c')  # 'name' prop hash
def entity_items(d):
    g=resgrp.walk(d);out=[]
    for L in g['lists']:
        if L['cls']!='CIsEntitySpec': continue
        for q,fl,s in L['items']:
            body=d[q+5:q+s]
            h=struct.unpack_from('<I',body,0)[0]
            # components
            comps=[];p=0
            while True:
                p=body.find(b'LFER',p)
                if p<0: break
                comps.append(D.get(struct.unpack_from('<I',body,p+4)[0],hex(struct.unpack_from('<I',body,p+4)[0])));p+=4
            n=body.find(NAMEPROP)
            name=None
            if n>=0:
                ln=struct.unpack_from('<I',body,n+8)[0]; name=body[n+12:n+12+ln].rstrip(b'\0').decode('latin1')
            out.append(dict(q=q,size=s,hash=h,hname=D.get(h),name=name,comps=comps))
    return out
