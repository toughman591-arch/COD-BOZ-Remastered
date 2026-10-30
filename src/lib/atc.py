import numpy as np, struct
def _exp(x,b): return (x<<(8-b))|(x>>(2*b-8))
def decode_color_blocks(blk):
    # blk: (N,8) uint8 -> (N,16,3) uint8
    c0=blk[:,0].astype(np.int32)|(blk[:,1].astype(np.int32)<<8)
    c1=blk[:,2].astype(np.int32)|(blk[:,3].astype(np.int32)<<8)
    idx=blk[:,4].astype(np.uint32)|(blk[:,5].astype(np.uint32)<<8)|(blk[:,6].astype(np.uint32)<<16)|(blk[:,7].astype(np.uint32)<<24)
    C0=np.stack([_exp((c0>>10)&31,5),_exp((c0>>5)&31,5),_exp(c0&31,5)],1)
    C1=np.stack([_exp((c1>>11)&31,5),_exp((c1>>5)&63,6),_exp(c1&31,5)],1)
    mode=(c0&0x8000)!=0
    P=np.zeros((len(blk),4,3),np.int32)
    P[:,0]=np.where(mode[:,None],0,C0)
    P[:,1]=np.where(mode[:,None],np.maximum(0,C0-C1//4),(5*C0+3*C1)//8)
    P[:,2]=np.where(mode[:,None],C0,(3*C0+5*C1)//8)
    P[:,3]=C1
    sel=np.stack([(idx>>(2*i))&3 for i in range(16)],1)
    return np.take_along_axis(P,sel[:,:,None].astype(np.int64),1).astype(np.uint8)
def decode(data,w,h,alpha):
    bw,bh=max(1,(w+3)//4),max(1,(h+3)//4); n=bw*bh
    bs=16 if alpha else 8
    a=np.frombuffer(data[:n*bs],np.uint8).reshape(n,bs)
    rgb=decode_color_blocks(np.ascontiguousarray(a[:,bs-8:]))
    if alpha:
        al=np.zeros((n,16),np.uint8)
        for i in range(8):
            b=a[:,i]; al[:,2*i]=(b&15)*17; al[:,2*i+1]=(b>>4)*17
    else: al=np.full((n,16),255,np.uint8)
    px=np.concatenate([rgb,al[:,:,None]],2).reshape(bh,bw,4,4,4).transpose(0,2,1,3,4).reshape(bh*4,bw*4,4)
    return px[:h,:w]
def blocksize(w,h,alpha): return max(1,(w+3)//4)*max(1,(h+3)//4)*(16 if alpha else 8)

# ---------- encoder ----------
W=np.array([0,3/8,5/8,1.0])
def _q555(c): return np.clip(np.rint(c*31/255),0,31).astype(np.int32)
def _q565(c):
    return np.stack([np.clip(np.rint(c[:,0]*31/255),0,31),np.clip(np.rint(c[:,1]*63/255),0,63),np.clip(np.rint(c[:,2]*31/255),0,31)],1).astype(np.int32)
def _pal(e0,e1):
    C0=np.stack([_exp(e0[:,0],5),_exp(e0[:,1],5),_exp(e0[:,2],5)],1)
    C1=np.stack([_exp(e1[:,0],5),_exp(e1[:,1],6),_exp(e1[:,2],5)],1)
    return np.stack([C0,(5*C0+3*C1)//8,(3*C0+5*C1)//8,C1],1).astype(np.float32)
def encode_color_blocks(px,iters=3):
    # px (N,16,3) float32 0..255 -> (N,8) uint8
    N=len(px); mean=px.mean(1,keepdims=True); X=px-mean
    cov=np.einsum('nki,nkj->nij',X,X)
    v=np.ones((N,3),np.float32)/np.sqrt(3)
    for _ in range(8):
        v=np.einsum('nij,nj->ni',cov,v); v/=np.linalg.norm(v,axis=1,keepdims=True)+1e-9
    t=np.einsum('nki,ni->nk',X,v)
    lo=mean[:,0]+v*t.min(1)[:,None]; hi=mean[:,0]+v*t.max(1)[:,None]
    a,b=lo,hi
    best=None
    for it in range(iters+1):
        e0=_q555(a);e1=_q565(b);P=_pal(e0,e1)
        d=((px[:,:,None,:]-P[:,None,:,:])**2).sum(-1)
        sel=d.argmin(2); err=d.min(2).sum(1)
        if best is None:
            best=[e0,e1,sel,err]
        else:
            m=err<best[3]
            for k,val in enumerate([e0,e1,sel,err]): best[k][m]=val[m]
        # least squares refit
        wt=W[sel]; w0=1-wt; w1=wt
        A00=(w0*w0).sum(1);A01=(w0*w1).sum(1);A11=(w1*w1).sum(1)
        B0=np.einsum('nk,nkc->nc',w0,px);B1=np.einsum('nk,nkc->nc',w1,px)
        det=A00*A11-A01*A01; ok=np.abs(det)>1e-6
        na=np.where(ok[:,None],(A11[:,None]*B0-A01[:,None]*B1)/np.where(ok,det,1)[:,None],a)
        nb=np.where(ok[:,None],(A00[:,None]*B1-A01[:,None]*B0)/np.where(ok,det,1)[:,None],b)
        a,b=np.clip(na,0,255),np.clip(nb,0,255)
    e0,e1,sel,_=best
    c0=(e0[:,0]<<10)|(e0[:,1]<<5)|e0[:,2]
    c1=(e1[:,0]<<11)|(e1[:,1]<<5)|e1[:,2]
    idx=np.zeros(N,np.uint64)
    for i in range(16): idx|=(sel[:,i].astype(np.uint64)<<np.uint64(2*i))
    out=np.zeros((N,8),np.uint8)
    out[:,0]=c0&255;out[:,1]=c0>>8;out[:,2]=c1&255;out[:,3]=c1>>8
    for i in range(4): out[:,4+i]=((idx>>np.uint64(8*i))&np.uint64(255)).astype(np.uint8)
    return out
def to_blocks(img):
    h,w,c=img.shape; bh,bw=max(1,(h+3)//4),max(1,(w+3)//4)
    pad=np.zeros((bh*4,bw*4,c),img.dtype); pad[:h,:w]=img
    if h<4 or w<4:  # replicate for tiny mips
        pad[:]=np.resize(img,(bh*4,bw*4,c)) if False else pad
        for y in range(bh*4):
            for x in range(bw*4): pad[y,x]=img[y%h,x%w]
    return pad.reshape(bh,4,bw,4,c).transpose(0,2,1,3,4).reshape(bh*bw,16,c)
def encode(img,alpha):
    # img HxWx4 uint8
    blk=to_blocks(img.astype(np.float32))
    col=encode_color_blocks(blk[:,:,:3])
    if not alpha: return col.tobytes()
    a=np.clip(np.rint(blk[:,:,3]/17),0,15).astype(np.uint8)
    ab=(a[:,0::2]|(a[:,1::2]<<4))
    return np.concatenate([ab,col],1).tobytes()
