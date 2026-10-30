import sys,os;sys.path.insert(0,'/root/tools')
import texlib,rewrite,resgrp
from PIL import Image
SRC,OUT=sys.argv[1],sys.argv[2]
for n in ['loading','loading_droid','loading_ipad','loading_retina']:
    f=f'loading/kino/{n}.group.bin'
    d=open(os.path.join(SRC,f),'rb').read()
    t=[t for t in texlib.records(d) if not t['alpha']][0]
    art=Image.open('/root/work/art/kino_loading_%d.png'%t['w'])
    e=rewrite.texture_edit(d,t,art,t['w'],t['h'])
    nd=rewrite.apply(d,[e]); assert len(nd)==len(d) and resgrp.walk(nd)['ok']
    os.makedirs(os.path.dirname(os.path.join(OUT,f)),exist_ok=True)
    open(os.path.join(OUT,f),'wb').write(nd)
    Image.fromarray(texlib.mip0(nd,[x for x in texlib.records(nd) if not x['alpha']][0])).convert('RGB').resize((512,512)).save(f'/root/work/art/check_{n}.jpg')
    print(n,t['w'],t['h'],t['nm'],'ok')
