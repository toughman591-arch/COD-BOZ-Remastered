import sys,struct,os,math
sys.path.insert(0,'/root/tools')
import resgrp,ents
from hashes import djb2
SRC='/root/work/dz'; OUT=sys.argv[1]
f='levels/tutorial/tutorial_statics.group.bin'
base=os.path.join(OUT,f) if os.path.exists(os.path.join(OUT,f)) else os.path.join(SRC,f)
d=bytearray(open(base,'rb').read())
kino=open(os.path.join(SRC,'levels/kino/kino_statics.group.bin'),'rb').read()
H=lambda s:djb2(s.lower())
log=[]
def set_prop(buf,start,end,prop,value,fmt='<I'):
    ph=struct.pack('<I',H(prop));p=buf.find(ph,start,end);n=0
    while p>=0:
        if buf[p+4:p+8]==b'\x01\x00\x00\x00':
            sz=struct.unpack_from('<I',buf,p+8)[0]
            assert sz==struct.calcsize(fmt)
            old=struct.unpack_from(fmt,buf,p+12)[0]; struct.pack_into(fmt,buf,p+12,value); n+=1
            log.append(f'{prop}: {old} -> {value}')
        p=buf.find(ph,p+1,end)
    assert n==1,(prop,n)
g=resgrp.walk(bytes(d))
def item_by_hash(cls,h):
    L=[l for l in g['lists'] if l['cls']==cls][0]
    for q,fl,s in L['items']:
        if struct.unpack_from('<I',d,q+5)[0]==h: return q,s
    raise KeyError(hex(h))
# 1) tutorial spawner tuning (same-size edits)
q,s=item_by_hash('CTutorialConfig',H('Tutorial_config'))
set_prop(d,q,q+s,'maxActiveZombies',24)
set_prop(d,q,q+s,'zombieSpawnIntervalMS',2000)
set_prop(d,q,q+s,'zombieHealth',150)
# 2) last lesson (grenade + kill zombies) becomes endless survival
q,s=item_by_hash('CTutorialSession',0x0dbbcd3b)
set_prop(d,q,q+s,'m_ZombieKillLimit',65000)
set_prop(d,q,q+s,'repeatinstructionTimeMS',3600000)
# 3) append perk machines, Pack-a-Punch and power switch copied from Kino
KE={e['name']:e for e in ents.entity_items(kino)}
POS=struct.pack('<I',H('m_localPosition'));ROT=struct.pack('<I',H('m_localRotation'))
def yaw(theta):
    r=math.radians(theta)/2; return (0.0,math.sin(r),0.0,math.cos(r))
FLOOR=196.309
place={  # name: (x,z,theta)  theta: 0 faces -Z, 90 +X, 180 +Z, 270 -X
 'QuickRevive':None,                    # same spot as in Kino (this lobby)
 'Juggernog':(-883.0,2900.0,90),
 'Doubletap':(-750.0,2793.0,180),
 'Speedcola':(-600.0,3608.0,0),
 'PackAPunch':(600.0,2729.0,180),
 'PowerSwitch':(-378.0,3617.0,0),
}
# Our own power switch gets a new unique name, so only the new perks/PaP listen to it.
# The tutorial's own power-linked objects (teleporter mainframe, trap switch, PowerOn_Door1)
# keep waiting for the original 'powerSwitch', which never exists here - same as before.
NEWPS='PowerSwTut1'; NEWPS_H=H(NEWPS); OLDPS_H=H('powerSwitch')
assert len(NEWPS)==len('PowerSwitch')
new=b''
for name,pl in place.items():
    e=KE[name]; item=bytearray(kino[e['q']:e['q']+e['size']]); item[0]=0
    if name=='PowerSwitch':
        assert struct.unpack_from('<I',item,5)[0]==OLDPS_H
        struct.pack_into('<I',item,5,NEWPS_H)
        k=item.find(b'PowerSwitch\0'); assert k>0; item[k:k+11]=NEWPS.encode()
    else:
        ps=struct.pack('<I',H('powerSwitch'))
        p=item.find(ps)
        while p>=0:
            if item[p+4:p+12]==b'\x01\x00\x00\x00\x04\x00\x00\x00' and struct.unpack_from('<I',item,p+12)[0]==OLDPS_H:
                struct.pack_into('<I',item,p+12,NEWPS_H)
            p=item.find(ps,p+1)
        assert struct.pack('<I',NEWPS_H) in item
    if pl:
        x,z,t=pl
        i=item.rfind(POS); j=item.rfind(ROT)
        struct.pack_into('<3f',item,i+12,x,FLOOR,z)
        struct.pack_into('<4f',item,j+12,*yaw(t))
    new+=bytes(item); log.append(f'added {name} at {pl or "Kino position"}')
L=[l for l in g['lists'] if l['cls']=='CIsEntitySpec'][0]
first_q=L['items'][0][0]; cnt_off=first_q-5
assert struct.unpack_from('<I',d,cnt_off)[0]==L['cnt']
lq,lf,ls=L['items'][-1]; ins=lq+ls
struct.pack_into('<I',d,cnt_off,L['cnt']+len(place))
ro=g['res_off']+4; struct.pack_into('<I',d,ro,struct.unpack_from('<I',d,ro)[0]+len(new))
d[ins:ins]=new
nd=bytes(d)
g2=resgrp.walk(nd); assert g2['ok']
E2=ents.entity_items(nd); assert len(E2)==L['cnt']+len(place)
os.makedirs(os.path.dirname(os.path.join(OUT,f)),exist_ok=True)
open(os.path.join(OUT,f),'wb').write(nd)
print('\n'.join(log)); print('size delta',len(nd)-len(open(base,'rb').read()))
