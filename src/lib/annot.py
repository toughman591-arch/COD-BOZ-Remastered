import sys,struct,pickle
D=pickle.load(open('/root/tools/hashdict.pkl','rb'))
def annot(d,start=0,end=None,minlen=0):
    end=end or len(d)
    out=[]
    for p in range(start,end-3):
        v=struct.unpack_from('<I',d,p)[0]
        if v in D and len(D[v])>=minlen: out.append((p,D[v]))
    return out
if __name__=='__main__':
    d=open(sys.argv[1],'rb').read()
    s=int(sys.argv[2]) if len(sys.argv)>2 else 0
    e=int(sys.argv[3]) if len(sys.argv)>3 else len(d)
    for p,n in annot(d,s,e,4):
        print(p,n,d[p+4:p+16].hex(' '))
