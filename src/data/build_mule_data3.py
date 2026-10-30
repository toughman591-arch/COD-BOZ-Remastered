"""Mule Kick test data: Kino statics (Mali) + the Mule Kick machine.
 - model 'mule_kick_machine' from the user's OBJ (zombie_vending_three_gun) + its 2 textures (body 512, logo 256);
   glass panel left out. Static entity in the Atrium's north-east niche (between the boarded window and the east wall),
   back to the wall, front to the room.
 - perk entity 'MuleKick' = Kino's Speed Cola perk entity (its animated machine hidden, like Verruckt's perks),
   perk type 0 (the game code turns type 0 on Kino into Mule Kick), 4000 points, same buy spot rules."""
import sys,struct,math,glob,numpy as np
sys.path.insert(0,'/root/tools'); sys.path.insert(0,'/root/work/mk2/tools'); sys.path.insert(0,'/root/work/v39'); sys.path.insert(0,'/root/work/mule'); sys.path.insert(0,'/root/work/v526')
import grp2,ent2,iwm,texlib,atc,objload
from maliconv import conv_bytes
from hashes import djb2
from PIL import Image
H=lambda s: djb2(s.lower())
def lst(G,c): return grp2.find(G,c)[2]
SRC='/root/work/v526/x/levels/kino/kino_statics.group.bin'; OUT='/root/work/mule3/data/kino_statics.group.bin'
KS=grp2.parse(open(SRC,'rb').read())
# ---------------- textures (ATC templates from the original data -> Mali conversion, the proven pipeline)
def tpl(f,h):
    g=grp2.parse(open(f,'rb').read()); return [t for t in lst(g,'CIwTexture') if grp2.name(t)==h][0]
def make_tex(img,name,tf,th):
    t=bytearray(tpl(tf,th)); r=texlib.records(bytes(t))[0]; W=r['w']
    assert img.size==(W,r['h'])
    struct.pack_into('<I',t,0,H(name)); o=r['pix']
    for lv,sz in enumerate(r['sizes']):
        w_=max(1,W>>lv); h_=max(1,r['h']>>lv)
        enc=atc.encode(np.asarray(img.convert('RGB').resize((w_,h_),Image.LANCZOS)),False); assert len(enc)==sz,(lv,len(enc),sz)
        t[o:o+sz]=enc; o+=sz
    out,st=conv_bytes(bytes(t)); return out,st
TX='/root/work/mule/src/textures/'
body=Image.open(TX+'gzombie_vending_three_gun_c.png'); logo=Image.open(TX+'gzombie_vending_three_gun_logo_c.png')
tb,s1=make_tex(body,'mule_kick_body_tex','/root/work/dz/levels/kino/bonusroom1_shared.group.bin',0x0ae4987a)
tl,s2=make_tex(Image.open('/root/work/mule3/logo_off.png'),'mule_kick_logo_tex','/root/work/dz/levels/kino/stage_shared.group.bin',0xde742bae)
tlit,s3=make_tex(Image.open('/root/work/mule3/logo_lit.png'),'mule_kick_logo_lit_tex','/root/work/dz/levels/kino/stage_shared.group.bin',0xde742bae)
print('textures',s1[:1],s2[:1])
# ---------------- materials: template = Verruckt's static Speed Cola model's material (Mali, opaque, lit like the map)
VE=grp2.parse(open('/root/work/v526/x/levels/verruck/verruck_env.group.bin','rb').read())
vm={grp2.name(m):m for m in lst(VE,'CIwModel')}[0xd317fb1a]
nmat=struct.unpack_from('<I',vm,len(vm)-4*0-4)[0]
mats_v=None
for k in range(1,12):
    n=struct.unpack_from('<I',vm,len(vm)-4*k-4)[0]
    if n==k: mats_v=list(struct.unpack_from('<%dI'%k,vm,len(vm)-4*k)); break
assert mats_v,'template materials'
MT={grp2.name(m):m for m in lst(VE,'CIwMaterial')}
tm=bytearray(MT[mats_v[0]]); assert struct.unpack_from('<I',tm,33)[0] in {grp2.name(t) for t in lst(VE,'CIwTexture')}
def make_mat(name,tex):
    m=bytearray(tm); struct.pack_into('<I',m,0,H(name)); struct.pack_into('<I',m,33,H(tex)); return bytes(m)
mb=make_mat('mule_kick_body_mat','mule_kick_body_tex'); ml=make_mat('mule_kick_logo_mat','mule_kick_logo_tex')
# ---------------- model
V,VT,VN,F=objload.load('/root/work/mule/src/source/zombie_vending_three_gun_LOD_1.obj')
S=0.85; Q=8                                   # machine scale (perk-machine height) ; position precision x8, entity scale 1/8
P=np.c_[V[:,0],V[:,2],-V[:,1]]*S              # OBJ (x right, y back, z up, front -y) -> game (x, y up, z front)
N=np.c_[VN[:,0],VN[:,2],-VN[:,1]]*2-np.array([1,1,1])*0  # VN stored as 0..1
N=np.c_[VN[:,0]*2-1,VN[:,2]*2-1,-(VN[:,1]*2-1)]
groups=[('mtl_zombie_vending_three_gun',0),('mtl_zombie_vending_three_gun_logo',1),('mtl_zombie_vending_three_gun_logo_off',1)]
# one game vertex per OBJ (v,vt,vn) corner
key={}; PV=[];UV=[];CC=[]; lists={0:[],1:[]}
L=np.array([0.25,0.8,0.55]); L/=np.linalg.norm(L)
for g,mi in groups:
    for tri in F[g]:
        for v,t,n in tri:
            k=(v,t,n)
            if k not in key:
                key[k]=len(PV); PV.append(np.round(P[v]*Q).astype(int))
                u,vv=VT[t]; UV.append([int(round(u*4096)),int(round((1-vv)*4096))])
                nn=N[n]/ (np.linalg.norm(N[n])+1e-9); s=int(round(255*(0.45+0.4*max(0.0,float(nn@L))+0.1)))
                CC.append([255]*3+[255] if mi==1 else [min(s,255)]*3+[255])   # logo: white (shade baked into logo_off)
            lists[mi].append(key[k])
PV=np.array(PV); UV=np.array(UV); CC=np.array(CC)
assert np.abs(PV).max()<32767 and np.abs(UV).max()<32767, (np.abs(PV).max(),np.abs(UV).max())
NMOD=H('mule_kick_machine')
model=iwm.encode(NMOD,0x20000,PV,None,UV,None,CC,[(0,np.array(lists[0])),(1,np.array(lists[1]))],[H('mule_kick_body_mat'),H('mule_kick_logo_mat')],minimal=True)
x_=iwm.decode(iwm.walk(model)); assert x_['P'].shape[0]==len(PV)
print('model verts',len(PV),'tris',(len(lists[0])+len(lists[1]))//3,'bounds',(PV.min(0)/Q).round(),(PV.max(0)/Q).round())
# ---------------- placement: Atrium NE niche
FLOOR=197.35; WALLZ=2357.0; XC=-1496.0
def quat_yaw(deg): r=math.radians(deg)/2; return (0.0,math.sin(r),0.0,math.cos(r))
back=float(-P[:,2].min())                    # model back distance behind its origin
POS_M=(XC,FLOOR-float(P[:,1].min()),WALLZ-1.0-back)   # yaw 180: model +z (front) -> world -z (into the room)
# static model entity: Verruckt's static Speed Cola env entity as the template
ve=[e for e in lst(VE,'CIsEntitySpec') if (lambda p: p and abs(p[0]-28511.66)<1 and abs(p[2]+1783.85)<1)(ent2.get(e,'m_localPosition','<3f'))][0]
em=ent2.setf(ve,'m_localPosition','<3f',*POS_M); em=ent2.setf(em,'m_localRotation','<4f',*quat_yaw(180)); em=ent2.setf(em,'m_localScale','<3f',1/Q,1/Q,1/Q)
c,q=ent2.find_prop(em,'assets','CIsRenderableModel'); a=bytearray(em[q['val']:q['val']+q['vsize']])
assert a.count(struct.pack('<I',0xd317fb1a))==2; a=a.replace(struct.pack('<I',0xd317fb1a),struct.pack('<I',NMOD))
em=ent2.set_value(em,'assets',bytes(a),'CIsRenderableModel'); em=struct.pack('<I',H('mule_kick_static_ent'))+em[4:]
_n,_cs,_end=ent2.comps(em); assert not any(c['cls']==H('CIsNamed') for c in _cs)
sc0=[e for e in lst(KS,'CIsEntitySpec') if ent2.name(e)=='Speedcola'][0]
_scn=[c for c in ent2.comps(sc0)[1] if c['cls']==H('CIsNamed')][0]
em=em[:_end]+sc0[_scn['hdr']:_scn['end']]+em[_end:]; em=em[:4]+struct.pack('<I',_n+1)+em[8:]
em=ent2.rename(em,'MuleKickMachine'); assert ent2.name(em)=='MuleKickMachine' and ent2.comps(em)[2]==len(em)-4
# perk entity: Kino's Speed Cola, animated machine hidden (Verruckt's hidden-asset form), type 0, 4000
KE=lst(KS,'CIsEntitySpec'); sc=[e for e in KE if ent2.name(e)=='Speedcola'][0]
VS=grp2.parse(open('/root/work/v526/verruck_statics.group.bin','rb').read())
vsc=[e for e in lst(VS,'CIsEntitySpec') if ent2.name(e)=='Speedcola'][0]
c,q=ent2.find_prop(vsc,'assets','CIsRenderableModel'); hidden_assets=vsc[q['val']:q['val']+q['vsize']]
pe=ent2.rename(sc,'MuleKick')
pe=ent2.set_value(pe,'assets',hidden_assets,'CIsRenderableModel')
pe=ent2.setf(pe,'m_localPosition','<3f',XC,FLOOR,WALLZ-1.0); pe=ent2.setf(pe,'m_localRotation','<4f',*quat_yaw(180))
pe=ent2.setf(pe,'m_PerkType','<I',0,comp_cls='CPerk'); pe=ent2.setf(pe,'m_perkSinglePCost','<I',4000,comp_cls='CPerk')
pe=ent2.setf(pe,'perkName','<I',0xd9e26eb9,comp_cls='CPerk')   # S_BLACKOPS_MULE_KICK (build_loc.py)
pe=ent2.set_value(pe,'m_perkJingle',b'\0','CPerk')   # no jingle
_n,_cs,_end=ent2.comps(pe); _se=[c for c in _cs if c['cls']==H('CSoundEmitter')][0]
pe=pe[:_se['hdr']]+pe[_se['end']:]; pe=pe[:4]+struct.pack('<I',_n-1)+pe[8:]   # no machine sound
assert not any(c['cls']==H('CSoundEmitter') for c in ent2.comps(pe)[1]) and ent2.comps(pe)[2]==len(pe)-4
pe=ent2.setf(pe,'m_halfAxis','<3f',70.0,126.0,46.0,comp_cls='CIsCollisionBox'); pe=ent2.setf(pe,'m_Offset','<3f',0.0,126.0,46.0,comp_cls='CIsCollisionBox')
for e_ in (pe,):
    n_,cs_,end_=ent2.comps(e_); assert end_==len(e_)-4,(end_,len(e_))
KE.append(pe); KE.append(em)
# resources (before the entities): textures, materials, model
lst(KS,'CIwTexture').extend([tb,tl,tlit]); lst(KS,'CIwMaterial').extend([mb,ml])
names=[c for c,_,l in KS['lists']]
if H('CIwModel') not in names:
    i=names.index(H('CIwMaterial'))+1
    hdr=[h for c,h,l in grp2.parse(open('/root/work/v526/x/levels/verruck/verruck_env.group.bin','rb').read())['lists'] if c==H('CIwModel')][0]
    KS['lists'].insert(i,(H('CIwModel'),hdr,[model]))
else: lst(KS,'CIwModel').append(model)
out=grp2.build(KS); assert grp2.build(grp2.parse(out))==out
open(OUT,'wb').write(out); print('kino_statics',len(out),'perk at',(XC,FLOOR,WALLZ-1),'model at',POS_M)
