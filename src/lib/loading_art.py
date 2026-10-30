import numpy as np, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps, ImageChops
X='/root/work/ximg/ximages/'
W,H=1024,768
rng=np.random.default_rng(115)
def load(n): return Image.open(X+n).convert('RGBA')
def tile(img,w,h):
    out=Image.new('RGBA',(w,h))
    for y in range(0,h,img.size[1]):
        for x in range(0,w,img.size[0]): out.paste(img,(x,y))
    return out
# wall base: plaster wallpaper, darkened + desaturated
wall=tile(load('~-gberlin_wall_plaster_wallpaper14_c.png').resize((384,384)),W,H).convert('RGB')
wall=ImageEnhance.Color(wall).enhance(0.35); wall=ImageEnhance.Brightness(wall).enhance(0.38)
canvas=wall.convert('RGBA')
# chalk map on a dark board, center-left
chalk=load('theater_chalkmap_c.png').convert('RGB').resize((470,470))
board=Image.new('RGBA',(500,500),(10,10,10,255)); board.paste(chalk,(15,15))
board=ImageEnhance.Brightness(board.convert('RGB')).enhance(0.9).convert('RGBA')
board=board.rotate(-3,resample=Image.BICUBIC,expand=True,fillcolor=(0,0,0,0))
sh=Image.new('RGBA',board.size,(0,0,0,0)); sh.putalpha(board.split()[3].point(lambda a:int(a*0.7))); sh=sh.filter(ImageFilter.GaussianBlur(14))
canvas.alpha_composite(sh,(214,82)); canvas.alpha_composite(board,(200,70))
# posters pinned on the right
pst=load('~-gtheater_poster_1_c.png')  # 512x256 three posters
for i,(ang,x,y) in [(0,(4,770,48)),(1,(-3,790,300))]:
    pw=pst.size[0]//3; p=pst.crop((i*pw,0,(i+1)*pw,pst.size[1])).resize((140,215))
    p=ImageEnhance.Brightness(p).enhance(0.8)
    pr=p.rotate(ang,resample=Image.BICUBIC,expand=True)
    s=Image.new('RGBA',pr.size,(0,0,0,0));s.putalpha(pr.split()[3].point(lambda a:int(a*0.6)));s=s.filter(ImageFilter.GaussianBlur(8))
    canvas.alpha_composite(s,(x+8,y+10));canvas.alpha_composite(pr,(x,y))
# red velvet curtains on the edges
vel=load('~-gtheater_red_velvet_c.png').convert('RGB')
vel=ImageEnhance.Brightness(vel).enhance(0.75)
for side in (0,1):
    cw=120; c=tile(vel.resize((cw,384)).convert('RGBA'),cw,H)
    # folds: vertical sine shading
    xs=np.arange(cw); fold=(0.55+0.45*np.sin(xs/cw*np.pi*5+side))**1.4
    a=np.asarray(c,np.float32); a[...,:3]*=fold[None,:,None]
    mask=np.clip((1-xs/cw)*1.6,0,1)**0.8 if side==0 else np.clip((xs/cw)*1.6,0,1)**0.8
    a[...,3]=255*mask[None,:]
    c=Image.fromarray(a.astype(np.uint8),'RGBA')
    canvas.alpha_composite(c,(0 if side==0 else W-cw,0))
# lighting: warm spot from top center + vignette
yy,xx=np.mgrid[0:H,0:W]
spot=np.exp(-(((xx-470)/430)**2+((yy-250)/360)**2))
vign=np.clip(1-0.75*(((xx-W/2)/(W/1.25))**2+((yy-H/2)/(H/1.15))**2),0,1)
a=np.asarray(canvas.convert('RGB'),np.float32)
light=(0.45+0.85*spot)[...,None]*np.array([1.06,0.98,0.86])
a=a*light*vign[...,None]
# bottom fade to black for the title area
fade=np.clip((yy-470)/260,0,1)**1.3
a=a*(1-0.88*fade[...,None])
img=Image.fromarray(np.clip(a,0,255).astype(np.uint8))
# title
d=ImageDraw.Draw(img)
fb=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf',118)
fs=ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-Black.otf',26)
fm=ImageFont.truetype('/usr/share/fonts/opentype/inter/InterDisplay-Medium.otf',20)
title='KINO DER TOTEN'
tl=Image.new('L',(1400,160),0); ImageDraw.Draw(tl).text((0,0),title,font=fb,fill=255)
bb=tl.getbbox(); tl=tl.crop(bb); tl=tl.resize((int(tl.size[0]*0.80),tl.size[1]))  # extra condense
# grunge erosion
noise=Image.fromarray((rng.random((tl.size[1],tl.size[0]))*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))
er=np.asarray(noise)>70
ta=np.asarray(tl,np.float32)*np.where(er,1.0,0.25)
tl=Image.fromarray(ta.astype(np.uint8))
tx,ty=62,610
shadow=tl.filter(ImageFilter.GaussianBlur(6))
img.paste((0,0,0),(tx+4,ty+5),shadow)
img.paste((226,219,203),(tx,ty),tl)
# red rule + small caps line above
d.rectangle([tx,ty-22,tx+86,ty-16],fill=(150,18,14))
d.text((tx+100,ty-34),'ZOMBIES',font=fs,fill=(205,198,184))
d.text((tx+2,ty+tl.size[1]+16),'BERLIN, GERMANY  //  GROUP 935',font=fm,fill=(150,146,138))
# film grain + slight sepia crush
a=np.asarray(img,np.float32)
g=rng.normal(0,9,(H,W,1))
a=a+g
lum=a.mean(2,keepdims=True); a=lum+(a-lum)*0.85
img=Image.fromarray(np.clip(a,0,255).astype(np.uint8))
img.save('/root/work/art/kino_loading_master.png')
# 1024x1024 atlas: art in top 1024x768, bottom filled with original fill color
atl=Image.new('RGB',(1024,1024),(24,28,24)); atl.paste(img,(0,0)); atl.save('/root/work/art/kino_loading_1024.png')
# 512 atlas: 480x320 region (3:2 crop of 4:3 master)
crop=img.crop((0,85,1024,85+683)).resize((480,320),Image.LANCZOS)
a5=Image.new('RGB',(512,512),(24,28,24)); a5.paste(crop,(0,0)); a5.save('/root/work/art/kino_loading_512.png')
img.resize((800,600),Image.LANCZOS).save('/root/work/art/preview.jpg',quality=90)
