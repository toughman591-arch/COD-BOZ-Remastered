"""Mule Kick logo textures: 'off' (machine without power) and 'lit' (power on: glowing green panel)."""
import numpy as np
from PIL import Image, ImageFilter
src=np.asarray(Image.open('/root/work/mule/src/textures/gzombie_vending_three_gun_logo_c.png').convert('RGB')).astype(float)/255
H,W,_=src.shape; yy,xx=np.mgrid[0:H,0:W]
cx,cy,R=152.0,152.0,97.0
d=np.hypot(xx-cx,yy-cy)
inside=np.clip((R-d)/2.0,0,1)                     # light circle (soft edge)
ring=np.exp(-((d-R-6)/9.0)**2)                    # glow just outside the circle
OFF=0.77                                          # vertex colour the logo had before (now 1.0) -> same look unpowered
off=src*OFF
L=src.mean(2,keepdims=True)
mint=np.array([0.80,1.00,0.82]); green=np.array([0.15,1.0,0.35])
lit=src*1.10
lit=lit*(1-inside[...,None]*0.7)+np.clip(mint*(0.55+0.55*L),0,1)*inside[...,None]*0.7   # circle glows mint
gs=(src[...,1]>src[...,0]+0.05)&(src[...,1]>src[...,2]+0.02)          # green shield pixels
lit[gs]=np.clip(src[gs]*np.array([0.7,1.45,0.8]),0,1)
lit=lit+green*ring[...,None]*0.65
lit=np.clip(lit,0,1)
Image.fromarray((off*255).astype(np.uint8)).save('logo_off.png')
Image.fromarray((lit*255).astype(np.uint8)).save('logo_lit.png')
both=Image.new('RGB',(512,256)); both.paste(Image.fromarray((off*255).astype(np.uint8)),(0,0)); both.paste(Image.fromarray((lit*255).astype(np.uint8)),(256,0)); both.save('cmp.png')
