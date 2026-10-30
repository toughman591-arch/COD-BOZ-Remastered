"""Mule Kick v2: HUD icon in the in-game atlas + a 'Perk_MuleKick_Image' UI image (copy of Perk_Deadshot_Image)."""
import sys,struct,numpy as np
sys.path.insert(0,'/root/tools'); sys.path.insert(0,'/root/work/rx')
import grp2
from iwh import iwh
from PIL import Image
SRC='/root/work/v526/x/ingame/ingame.group.bin'; OUT='/root/work/mule2/data/ingame.group.bin'
G=grp2.parse(open(SRC,'rb').read())
TX=[L for L in G['lists'] if L[0]==iwh('CIwTexture')][0][2]
k=[i for i,t in enumerate(TX) if grp2.name(t)==0x35beca41][0]
t=bytearray(TX[k]); assert len(t)==28+1024*1024*2
X0,Y0=688,100                                   # free 57x67 cell (8 px clear margin all round)
px=np.frombuffer(bytes(t[-2097152:]),dtype='<u2').reshape(1024,1024).copy()
assert not px[Y0-8:Y0+67+8,X0-8:X0+57+8].any()
ic=np.asarray(Image.open('/root/work/mule2/icon/mule_icon_57x67.png').convert('RGBA')).astype(np.uint16)
px[Y0:Y0+67,X0:X0+57]=((ic[...,0]>>4)<<12)|((ic[...,1]>>4)<<8)|((ic[...,2]>>4)<<4)|(ic[...,3]>>4)
t[-2097152:]=px.astype('<u2').tobytes(); TX[k]=bytes(t)
UI=[L for L in G['lists'] if L[0]==iwh('CIwUIElement')][0][2]
DS=iwh('Perk_Deadshot_Image'); MK=iwh('Perk_MuleKick_Image')
src=[e for e in UI if struct.unpack_from('<I',e,4)[0]==DS]; assert len(src)==1
e=bytearray(src[0]); assert struct.unpack_from('<II',e,0)==(iwh('CIwUIImage'),DS) and struct.unpack_from('<I',e,28)[0]==DS
struct.pack_into('<I',e,4,MK); struct.pack_into('<I',e,28,MK)
assert struct.unpack_from('<I',e,20)[0]==0xbf; struct.pack_into('<I',e,20,0xdc)
u0=struct.pack('<IIhh',iwh('uv0'),iwh('CIwSVec2'),342,522); u1=struct.pack('<IIhh',iwh('uv1'),iwh('CIwSVec2'),399,589)
assert e.count(u0)==1 and e.count(u1)==1
e=e.replace(u0,struct.pack('<IIhh',iwh('uv0'),iwh('CIwSVec2'),X0,Y0)).replace(u1,struct.pack('<IIhh',iwh('uv1'),iwh('CIwSVec2'),X0+57,Y0+67))
assert struct.pack('<I',DS) not in e and not any(struct.unpack_from('<I',x,4)[0]==MK for x in UI)
UI.append(bytes(e))
out=grp2.build(G); assert grp2.build(grp2.parse(out))==out
open(OUT,'wb').write(out); print('ingame',len(out))
