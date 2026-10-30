import numpy as np
def _twiddle(ys,xs,y,x):
    mn=min(xs,ys); tw=0; sb=1; db=1; sh=0
    while sb<mn:
        if y&sb: tw|=db
        if x&sb: tw|=db<<1
        sb<<=1; db<<=2; sh+=1
    mx=max(x,y)>>sh
    return tw|(mx<<(2*sh))
def _colA(c):
    op=(c&0x8000)!=0
    r=np.where(op,(c&0x7c00)>>10,((c&0xf00)>>7)|((c&0xf00)>>11))
    g=np.where(op,(c&0x3e0)>>5,((c&0xf0)>>3)|((c&0xf0)>>7))
    b=np.where(op,(c&0x1e)|((c&0x1e)>>4),((c&0xe)<<1)|((c&0xe)>>2))
    a=np.where(op,0xf,(c&0x7000)>>11)
    return np.stack([r,g,b,a],-1).astype(np.int64)
def _colB(c):
    op=(c&0x80000000)!=0
    r=np.where(op,(c&0x7c000000)>>26,((c&0xf000000)>>23)|((c&0xf000000)>>27))
    g=np.where(op,(c&0x3e00000)>>21,((c&0xf00000)>>19)|((c&0xf00000)>>23))
    b=np.where(op,(c&0x1f0000)>>16,((c&0xf0000)>>15)|((c&0xf0000)>>19))
    a=np.where(op,0xf,(c&0x70000000)>>27)
    return np.stack([r,g,b,a],-1).astype(np.int64)
def decode4(data,w,h):
    """PVRTC1 4bpp -> RGBA uint8 (h,w,4)"""
    bw=max(w//4,2); bh=max(h//4,2)
    words=np.frombuffer(data,dtype='<u4',count=bw*bh*2).reshape(-1,2).astype(np.int64)
    idx=np.array([[_twiddle(bh,bw,y,x) for x in range(bw)] for y in range(bh)])
    mod=words[:,0][idx]; col=words[:,1][idx]          # (bh,bw)
    A=_colA(col); B=_colB(col)                           # (bh,bw,4)
    mode=(col&1)
    # per-pixel modulation (bh*4, bw*4)
    sh=np.arange(16)*2
    mv=((mod[...,None]>>sh)&3).reshape(bh,bw,4,4)       # [by,bx,py,px]
    mv=mv.transpose(0,2,1,3).reshape(bh*4,bw*4)
    md=np.repeat(np.repeat(mode,4,0),4,1)
    rep0=np.array([0,3,5,8]); rep1=np.array([0,4,4,8])
    m=np.where(md==0,rep0[mv],rep1[mv]); punch=(md==1)&(mv==2)
    # bilinear upscale of A,B: block centers at (b*4+2)
    H,W=bh*4,bw*4
    yy=np.arange(H); xx=np.arange(W)
    def up(C):
        out=np.zeros((H,W,4),np.int64)
        # pixel (y,x): word quad P at block ((y-2)//4,(x-2)//4) wrap, frac (y-2)%4,(x-2)%4
        by=((yy-2)//4)%bh; fy=(yy-2)%4; bx=((xx-2)//4)%bw; fx=(xx-2)%4
        by1=(by+1)%bh; bx1=(bx+1)%bw
        P=C[by][:,bx]; Q=C[by][:,bx1]; R=C[by1][:,bx]; S=C[by1][:,bx1]
        fx_=fx[None,:,None]; fy_=fy[:,None,None]
        res=(P*(4-fx_)*(4-fy_)+Q*fx_*(4-fy_)+R*(4-fx_)*fy_+S*fx_*fy_)   # = value*16 scale
        rgb=(res[...,:3]>>6)+(res[...,:3]>>1)
        a=(res[...,3:]>>4)+res[...,3:]
        return np.concatenate([rgb,a],-1)
    UA=up(A); UB=up(B)
    out=(UA*(8-m[...,None])+UB*m[...,None])//8
    out[...,3]=np.where(punch,0,out[...,3])
    return np.clip(out,0,255).astype(np.uint8)[:h,:w]
