import sys,struct,pickle
sys.path.insert(0,'/root/tools')
from hashes import djb2
D=pickle.load(open('/root/tools/hashdict.pkl','rb'))
RES=struct.pack('<I',djb2('resgroupresources'))
def walk(d):
    p=d.find(RES);sz=struct.unpack_from('<I',d,p+4)[0]
    q=p+8;n=struct.unpack_from('<I',d,q)[0];q+=4
    lists=[]
    for i in range(n):
        ch,cnt=struct.unpack_from('<II',d,q);X=d[q+8];q+=9
        items=[]
        for j in range(cnt):
            s=struct.unpack_from('<I',d,q+1)[0]; items.append((q,d[q],s)); q+=s
        T=d[q];q+=1
        lists.append(dict(cls=D.get(ch,hex(ch)),cnt=cnt,items=items))
    return dict(res_off=p,res_size=sz,end=q,ok=(q==p+4+sz),lists=lists)
