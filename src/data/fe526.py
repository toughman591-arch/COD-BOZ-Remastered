"""v5.26 menu = fe519 + Shi No Numa ('proto') in co-op (online + local share the co-op map select / lobby):
 (d) co-op map select (sprite 955): 7th card (picture, SHI NO NUMA label, button) + 'Proto Select' segment
     (sends SUBJECT_MP_LEVEL_SELECT 'proto'); the card row (sprite 960) shrinks to the old 5-card width
 (e) lobby background (sprite 795): 'proto' frame
 (f) lobby vote (sprite 873): 7th vote button 'proto'; displayMapVote clears its ticks too"""
import sys,struct,json; sys.path.insert(0,'/root/work/v37'); sys.path.insert(0,'/root/work/v40')
src=open('/root/work/v40/build_fe40.py').read()
exec(src.split('SP_CARD,MP_CARD')[0].replace("open('/root/work/v37/fe37.swf','rb')","open('/root/work/v516/fe519.swf','rb')"))
Lj=json.load(open('/root/work/v55/fe_layout50.json'))
LS={k:(v[0]*KX,v[1]*KY,v[2]*KX,v[3]*KY) for k,v in Lj['LS'].items()}
out=list(T); ins={}
def label(s): return (43,swf.tag(43,s.encode()+b'\0'),2)
def remove(depth): return (28,swf.tag(28,struct.pack('<H',depth)),2)
SHOWF=(1,swf.tag(1,b''),2)
def clone_edittext(src,newid,old,new):
    b=body(T[gi(src)]); assert b.count(old)==1,(src,old)
    return (37,swf.tag(37,struct.pack('<H',newid)+b[2:].replace(old,new),long=True),6)
def clone_csm(src,newid):
    t=[t for t in T if t[0]==74 and cid(t)==src][0]; return (74,swf.tag(74,struct.pack('<H',newid)+body(t)[2:]),2)
VOTE=1417
P_MP,P_MPL,P_BTN,P_VLBL,P_VITEM,P_VOTE,P_LOBBY=range(1436,1443)
for c in (P_MP,P_MPL,P_BTN,P_VLBL,P_VITEM,P_VOTE,P_LOBBY): assert (False,c) not in IDX and (True,c) not in IDX,c
# ---- (d) co-op map select
DXV=4615
sid,fc,S=subtags(body(out[gi(955)])); assert fc==52 and S[-1][0]==0
frames=[[]]
for x in S[:-1]:
    if x[0]==1: frames.append([])
    else: frames[-1].append(x)
assert frames[-1]==[]; frames=frames[:-1]; assert len(frames)==52
used=set()
for fr in frames:
    for x in fr:
        if x[0]==26: used.add(po2(x)['depth'])
assert not used&{34,35,36,37},used
f1d={po2(x)['depth']:po2(x) for x in frames[0] if x[0]==26}
c30,l31,b32=f1d[30],f1d[31],f1d[32]; assert c30['cid']==1423 and l31['cid']==1424 and b32['cid']==1425
for d0,newd,newc,nm in ((c30,34,P_MP,None),(l31,35,P_MPL,'proto_label'),(b32,36,P_BTN,None)):
    d=dict(d0); d.pop('flags',None); d['depth']=newd; d['cid']=newc; d['matrix']=dict(d['matrix'],tx=d['matrix']['tx']+DXV)
    if nm: d['name']=nm
    frames[0].append(build_po2(d))
DEPP={30:34,31:35,33:37}
newseg=[]; nact=0
for k in range(44,52):                                     # frames 45..52 = 'Verruck Select'
    fr=[]
    for x in frames[k]:
        if x[0]==28:
            dep=struct.unpack('<H',body(x))[0]; fr.append(remove({32:36}.get(dep,dep))); continue
        if x[0]==43: assert body(x)==b'Verruck Select\0'; fr.append(label('Proto Select')); continue
        if x[0]==12:
            a=body(x); o=b'\x96.\x00\x00verruck\x00'; assert a.count(o)==1
            fr.append((12,swf.tag(12,a.replace(o,b'\x96,\x00\x00proto\x00')),2)); nact+=1; continue
        d=po2(x); d.pop('flags',None)
        if k==44 and d['depth']==27:                        # verruck's segment restores nacht's button -> ours restores verruck's
            d=dict(b32); d.pop('flags',None); fr.append(build_po2(d)); continue
        if d['depth'] in DEPP: d['depth']=DEPP[d['depth']]
        if 'matrix' in d: d['matrix']=dict(d['matrix'],tx=d['matrix']['tx']+DXV)
        fr.append(build_po2(d))
    newseg.append(fr)
assert nact==1
subs=[]
for fr in frames+newseg: subs+=fr+[SHOWF]
subs.append((0,b'\x00\x00',2))
out[gi(955)]=sprite_tag(sid,len(frames)+len(newseg),subs)
bb=bytearray(body(T[gi(1411)])); old=b'\x8c\x0d\x00Nacht Select\x00'; assert bb.count(old)==1
bb=bb.replace(old,b'\x8c\x0d\x00Proto Select\x00'); struct.pack_into('<H',bb,0,P_BTN)
ins.setdefault(gi(955),[]).extend([pic_shape(P_MP,(0,4860,0,9640),LS['MP']),clone_edittext(1410,P_MPL,b'<i>NACHT</i>',b'<i>SHI NO NUMA</i>'),
                                   clone_csm(1410,P_MPL),(34,swf.tag(34,bytes(bb),long=True),6)])
# card row: 7 cards in the width the 6 had (which was the original 5-card width)
W6=(9830+DXV+4860)-(-8964); W7=(9830+2*DXV+4860)-(-8964); C6=(-8964+9830+DXV+4860)/2; C7=(-8964+9830+2*DXV+4860)/2; CY=(-5588+4123)/2
sid9,fc9,S9=subtags(body(out[gi(960)])); n=0; S92=[]
for x in S9:
    if x[0]==26:
        d=po2(x)
        if d['depth']==11 and 'matrix' in d:
            m=d['matrix']; d.pop('flags'); k=m['sx']*W6/W7
            d['matrix']=dict(m,sx=k,sy=k,tx=round(m['tx']+m['sx']*C6-k*C7),ty=round(m['ty']+m['sy']*CY-k*CY)); x=build_po2(d); n+=1
    S92.append(x)
assert n>=1; out[gi(960)]=sprite_tag(sid9,fc9,S92); print('row matrices',n)
# ---- (e) lobby background
sid7,fc7,S7=subtags(body(out[gi(795)])); assert fc7==7 and S7[-1][0]==0
S7=S7[:-1]+[label('proto'),build_po2(dict(depth=11,cid=P_LOBBY,move=True)),SHOWF,(0,b'\x00\x00',2)]
out[gi(795)]=sprite_tag(sid7,8,S7)
ins.setdefault(gi(795),[]).append(pic_shape(P_LOBBY,(6360,14280,2989,11929),sub_region(LS['BG'],0.18,0,0.82,1)))
# ---- (f) lobby vote: 7th button
sidk,fck,SK=subtags(body(out[gi(1413)])); outk=[]
for x in SK:
    if x[0]==26:
        d=po2(x); d.pop('flags',None)
        if d.get('cid')==VOTE: d['cid']=P_VOTE
        if d.get('cid')==1412: d['cid']=P_VLBL; d['name']='proto_lbl'
        outk.append(build_po2(d))
    else: outk.append(x)
vitem=sprite_tag(P_VITEM,fck,outk)
sidv,fcv,SV=subtags(body(out[gi(873)]))
ORDER=['kino','deadops','ascension','callofthedead','nacht','verruck','proto']; X0,X1=7391,15858; SC0=0.76; SC=SC0*((X1-X0)/6)/((X1-X0)/4)
outv=[]; nacht_po=None; used=set()
for x in SV:
    if x[0]==26:
        d=po2(x); d.pop('flags',None); used.add(d['depth'])
        if d.get('name')=='nacht': nacht_po=dict(d)
        if d.get('name') in ORDER:
            i=ORDER.index(d['name']); d['matrix']=dict(d['matrix'],sx=SC,sy=SC,tx=round(X0+i*(X1-X0)/6))
        outv.append(build_po2(d)); continue
    outv.append(x)
assert 73 not in used
a=bytearray(nacht_po['actions']); p=6; recs=[]
while True:
    fl=struct.unpack_from('<I',a,p)[0]
    if fl==0: break
    sz=struct.unpack_from('<I',a,p+4)[0]; recs.append([fl,bytes(a[p+8:p+8+sz])]); p+=8+sz
done=0
for r in recs:
    o=b'\x96\x28\x00\x00nacht\x00'
    if o in r[1]: r[1]=r[1].replace(o,b'\x96\x28\x00\x00proto\x00'); done+=1
assert done==1
na=bytes(a[:6])+b''.join(struct.pack('<II',fl,len(c))+c for fl,c in recs)+b'\0\0\0\0'
vpo=dict(nacht_po,depth=73,cid=P_VITEM,name='proto',actions=na,matrix=dict(nacht_po['matrix'],sx=SC,sy=SC,tx=round(X0+6*(X1-X0)/6)))
endi=max(i for i,x in enumerate(outv) if x[0]==1); outv.insert(endi,build_po2(vpo))
out[gi(873)]=sprite_tag(sidv,fcv,outv)
ins.setdefault(gi(873),[]).extend([pic_shape(P_VOTE,(-1240,1200,-1694,1586),LS['SP']),clone_edittext(1412,P_VLBL,b'<i>Nacht</i>',b'<i>Shi No Numa</i>'),
                                   clone_csm(1412,P_VLBL),vitem])
from asedit import patch_displayMapVote_add
mv=[i for i,t in enumerate(out) if t[0]==12 and b'showVoteButtons' in body(t)]; assert len(mv)==1
out[mv[0]]=(12,swf.tag(12,patch_displayMapVote_add(body(out[mv[0]]),'nacht','proto'),long=True),6)
final=[]
for i,t in enumerate(out): final+=ins.get(i,[]); final.append(t)
from label_as import add_label_text
for spr,path in ((961,['mp_map_select','level_select_buttons','proto_label']),(884,['lobby','mapVote','proto','proto_lbl'])):
    i=[k for k,t in enumerate(final) if t[0]==39 and cid(t)==spr][0]
    sid,fc,S=subtags(body(final[i])); n=0
    for k,x in enumerate(S):
        if x[0]==12 and b'S_LEVEL_KINO' in body(x):
            S[k]=(12,swf.tag(12,add_label_text(body(x),path,'SHI NO NUMA'),long=True),6); n+=1
    assert n==1,(spr,n); final[i]=sprite_tag(sid,fc,S)
res=swf.build(h,final); open('/root/work/v526/fe/fe526.swf','wb').write(res)
print('fe526',len(res),len(T),'->',len(final))
