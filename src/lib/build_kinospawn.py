import sys,struct,os,math
sys.path.insert(0,'/root/tools')
import resgrp,ents,rewrite,navgraph
import kinoregion as K
from hashes import djb2
OUT=sys.argv[1]; f='levels/kino/kino_statics.group.bin'
d=bytearray(open(os.path.join(OUT,f),'rb').read())   # starts from zombie-cap-patched file
H=lambda s:djb2(s.lower()); log=[]
E={e['name']:e for e in ents.entity_items(bytes(d))}
def item(name):
    e=E[name]; return e['q'],e['q']+e['size']
def setp(name,prop,val,fmt):
    s,e=item(name); ph=struct.pack('<I',H(prop)); p=d.find(ph,s,e); hits=0
    while p>=0:
        if d[p+4:p+8]==b'\x01\x00\x00\x00' and struct.unpack_from('<I',d,p+8)[0]==struct.calcsize(fmt):
            old=struct.unpack_from(fmt,d,p+12); struct.pack_into(fmt,d,p+12,*val if isinstance(val,tuple) else (val,)); hits+=1
            log.append(f'{name}.{prop}: {old} -> {val}')
        p=d.find(ph,p+1,e)
    return hits
def floor_y(x,z):
    r=navgraph.locate(K.flat,x,250,z,ytol=120)
    if r is None:  # nearest point slightly inside the room
        best=None
        for i in K.region:
            c=K.flat[i].mean(0); dd=math.hypot(c[0]-x,c[2]-z)
            if c[1]<300 and (best is None or dd<best[0]): best=(dd,c[1])
        return float(best[1])-19.5
    return float(K.flat[r[0]][:,1].mean())-19.5
def move(name,x,z,theta):
    y=floor_y(x,z); r=math.radians(theta)/2
    s,e=item(name); b=bytes(d[s:e])
    i=b.rfind(struct.pack('<I',H('m_localPosition'))); j=b.rfind(struct.pack('<I',H('m_localRotation')))
    if 'MysteryBox' in name:  # box: entity transform is the FIRST CIsTransform (children follow)
        i=b.find(struct.pack('<I',H('m_localPosition'))); j=b.find(struct.pack('<I',H('m_localRotation')))
    struct.pack_into('<3f',d,s+i+12,x,y,z); struct.pack_into('<4f',d,s+j+12,0.0,math.sin(r),0.0,math.cos(r))
    log.append(f'moved {name} -> ({x},{y:.1f},{z}) facing {theta}')
# --- perks, Pack-a-Punch, power switch into the spawn room (model front is +Z: theta 0=+Z, 90=+X, 180=-Z, 270=-X)
move('Juggernog',-917.0,2950.0,90)
move('Doubletap',-150.0,3431.0,180)
move('Speedcola',-520.0,3611.0,180)
move('PackAPunch',-760.0,3611.0,180)
move('PowerSwitch',-360.0,3611.0,180)
# QuickRevive already in the spawn room - untouched
# --- mystery box: every box location moved to one lobby spot, and it never moves away
boxes=[n for n in E if n and n.startswith('MysteryBox_')]
for n in boxes:
    move(n,650.0,3468.0,180)
    setp(n,'m_MinWeapons',1000000,'<I'); setp(n,'m_MaxWeapons',1000000,'<I')
# --- doors: lobby doors can never be bought, power door never opens
for n in ['Lobby_To_Atrium','Lobby_To_Balcony']:
    s,e=item(n)
    # CPOI m_MaxDistance -> 0 (no prompt), cost -> 999999
    ph=struct.pack('<I',H('m_MaxDistance')); p=d.find(ph,s,e); struct.pack_into('<f',d,p+12,0.0); log.append(f'{n}.m_MaxDistance -> 0')
    setp(n,'m_Cost',999999,'<I')
setp('PowerOn_Door1','powerSwitch',H('kino_spawnroom_nopower'),'<I')
nd=bytes(d)
# --- hide the 'rubble' child of every box (insert a local position far below the floor)
CT=struct.pack('<I',H('CIsTransform'))
edits=[]
EE={e['name']:e for e in ents.entity_items(nd)}
for n in boxes:
    s=EE[n]['q']; e=s+EE[n]['size']; body=nd[s:e]
    k=body.find(b'mysterybox_rubble'); assert k>0
    p=body.find(CT+struct.pack('<I',16)+b'LFER'+CT,k)   # child CIsTransform with no props
    assert p>0 and struct.unpack_from('<II',body,p+16)==(16,0)
    pos=s+p
    prop=CT+struct.pack('<I',H('CIwFVec3'))+b'\x01\x00\x00\x00'+struct.pack('<I',H('m_localPosition'))+b'\x01\x00\x00\x00'+struct.pack('<I',12)+struct.pack('<3f',0.0,-3000.0,0.0)
    new=CT+struct.pack('<I',16+len(prop))+b'LFER'+CT+struct.pack('<I',16+len(prop))+struct.pack('<I',1)+prop
    edits.append((pos,24,new,[]))
nd=rewrite.apply(nd,edits); log.append(f'hid rubble of {len(edits)} boxes')
assert resgrp.walk(nd)['ok'] and len(ents.entity_items(nd))==len(ents.entity_items(bytes(d)))
open(os.path.join(OUT,f),'wb').write(nd)
print('\n'.join(log))
