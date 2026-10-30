"""Mule Kick HUD perk icon (57x67, BOZ style: light outline + art, see-through fill), from the user's Mule Kick logo texture."""
import numpy as np
from PIL import Image, ImageDraw
SS=8; W,H=57,67
src=np.asarray(Image.open('/root/work/mule/src/textures/gzombie_vending_three_gun_logo_c.png').convert('RGB')).astype(float)/255
# shield outline + fill drawn at the BOZ icon geometry (supersampled)
def poly(inset):
    x0,x1,y0,ys,yp=3+inset,54-inset,1+inset,44,63-inset*1.4
    return [(x0*SS,y0*SS),(x1*SS,y0*SS),(x1*SS,ys*SS),(28.5*SS,yp*SS),(x0*SS,ys*SS)]
def mask(pts):
    m=Image.new('L',(W*SS,H*SS),0); ImageDraw.Draw(m).polygon(pts,fill=255)
    return np.asarray(m.resize((W,H),Image.LANCZOS)).astype(float)/255
outer=mask(poly(0)); in1=mask(poly(1.5)); in2=mask(poly(3.0)); in3=mask(poly(3.8))
alpha=np.zeros((H,W)); lum=np.zeros((H,W))
fill=in3; line1=outer-in1; line2=in2-in3
fill=in1; alpha=np.maximum(alpha,fill*0.27); lum=np.maximum(lum,fill*0.0)
alpha=np.maximum(alpha,line1*0.85); lum=np.maximum(lum,line1*0.85)
alpha=np.maximum(alpha,line2*0.45); lum=np.maximum(lum,line2*0.6)
# pistols from the logo (light pixels inside the shield), uniform scale
crop=src[123:176,113:192]                       # inside the white line, above the point
L=crop.mean(2)
g=np.clip((L-0.30)/0.40,0,1)**0.8                    # pistol art (white/grey) -> 0..1
gi=Image.fromarray((g*255).astype(np.uint8))
gw=46; gh=int(round(gw*g.shape[0]/g.shape[1]))
gs=np.asarray(gi.resize((gw,gh),Image.LANCZOS)).astype(float)/255
ox,oy=(W-gw)//2,17
reg=np.zeros((H,W)); reg[oy:oy+gh,ox:ox+gw]=gs
reg*=in3
alpha=np.maximum(alpha,0.27+reg*0.70); lum=np.maximum(lum,reg)
alpha=np.where(in1>0,alpha,np.maximum(alpha*0,line1*0.85))
alpha*=outer>0.001
# colour: the other icons are a light cyan-white at full alpha
lo=np.array([34,215,55]); hi=np.array([185,235,240])
rgb=lo[None,None]+(hi-lo)[None,None]*np.clip(lum,0,1)[...,None]
img=np.dstack([rgb,alpha[...,None]*255]).clip(0,255).astype(np.uint8)
Image.fromarray(img,'RGBA').save('mule_icon_57x67.png')
print('ok',gw,gh)
