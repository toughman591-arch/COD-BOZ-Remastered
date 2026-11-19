"""Co-op menus: the 4 World at War maps (Nacht, Verrueckt, Shi No Numa, Der Riese) on the co-op map select and the lobby vote.
Their cards/vote buttons were defined but not placed in this menu; Der Riese is new. in: menu swf, out: menu swf"""
import sys, struct; sys.path.insert(0, '/root/work/coop'); from swflib import *; import as2
SRC, DST = sys.argv[1], sys.argv[2]
h, T = load(SRC); out = list(T); ins = {}
def gi(c, codes=None): return [i for i, t in enumerate(T) if t[0] not in (0, 1, 9, 12, 26, 28, 43, 69, 77, 86, 56, 73, 13, 62, 88, 59, 65, 76, 74) and cid(t) == c and (codes is None or t[0] in codes)][0]
def csm(c): return [i for i, t in enumerate(T) if t[0] == 74 and cid(t) == c][0]
def withid(t, newid): return tag(t[0], struct.pack('<H', newid) + body(t)[2:], long=t[2] == 6)
def clone_text(c, newid, old, new):
    b = body(T[gi(c)]); assert b.count(old) == 1, (c, old); return tag(37, struct.pack('<H', newid) + b[2:].replace(old, new), long=True)
used_ids = {cid(t) for t in T if t[0] not in (0, 1, 9, 12, 26, 28, 43, 69, 77, 86, 56, 73, 13, 62, 88, 59, 65, 76, 74)}
P_MP, P_MPL, P_BTN, P_VLBL, P_VITEM, P_VPIC, P_LOBBY = range(1451, 1458)
assert not used_ids & set(range(1451, 1458))
KX, KY = 2.760, 2.883                                      # atlas 403 pixels per SWF bitmap unit
def reg(x0, y0, x1, y1): return (x0 / KX, y0 / KY, x1 / KX, y1 / KY)
# ---------------- shapes / texts / buttons
mp_dr = clone_picshape(T[gi(1436)], P_MP, reg(189, 814, 290, 1014))         # Der Riese tall picture (atlas, unused till now)
mp_vr = clone_picshape(T[gi(1423)], 1423, reg(627, 4, 753, 254))           # Verrueckt card: its old tile now holds the Shangri-La card
lobby_dr = clone_picshape(T[gi(1442)], P_LOBBY, reg(262, 297, 452, 511))   # Der Riese wide picture
vpic_dr = clone_picshape(T[gi(1441)], P_VPIC, region_of(parse_picshape(T[gi(1443)])))  # vote button = solo card picture (as the others)
out[gi(1423)] = mp_vr
lbl_dr = clone_text(1437, P_MPL, b'<i>SHI NO NUMA</i>', b'<i>DER RIESE</i>'); lbl_dr_csm = withid(T[csm(1437)], P_MPL)
bb = body(T[gi(1438)]); old = b'\x8c\x0d\x00Proto Select\x00'; assert bb.count(old) == 1
btn_dr = tag(34, struct.pack('<H', P_BTN) + bb[2:].replace(old, b'\x8c\x0d\x00Riese Select\x00'), long=True)
vlbl_dr = clone_text(1439, P_VLBL, b'<i>Shi No Numa</i>', b'<i>Der Riese</i>'); vlbl_dr_csm = withid(T[csm(1439)], P_VLBL)
sid, fc, S = subtags(body(T[gi(1440)])); SV = []
for x in S:
    if x[0] == 26:
        d = po2(x)
        if d.get('cid') == 1441: d['cid'] = P_VPIC
        if d.get('cid') == 1439: d['cid'] = P_VLBL; d['name'] = 'derriese_lbl'
        x = build_po2(d)
    SV.append(x)
vitem_dr = sprite_tag(P_VITEM, fc, SV)
# ---------------- (1) co-op map select (sprite 955): place the 4 cards, fix the select segments, add 'Riese Select'
DXV = 4615; SHIFT = 40000; OFF = SHIFT                     # page 2: WaW card i = BO1 card i slot + SHIFT (off screen on page 1)
WAW = [('nacht', 1414, 1410, 1411, (24, 26, 27)), ('verruck', 1423, 1424, 1425, (30, 31, 32)),
       ('proto', 1436, 1437, 1438, (34, 35, 36)), ('derriese', P_MP, P_MPL, P_BTN, (38, 39, 40))]
sid, fc, S = subtags(body(T[gi(955)])); F = frames_of(S); assert fc == 60 and len(F) == 60
dep_used = {po2(x)['depth'] for fr in F for x in fr if x[0] == 26}; assert not dep_used & {24, 26, 27, 30, 31, 32, 34, 35, 36, 38, 39, 40, 41}
f1 = {po2(x)['depth']: po2(x) for x in F[0] if x[0] == 26}
kcard, klbl = f1[1], f1[3]; assert kcard['cid'] == 936 and klbl['cid'] == 937
kbtn = [po2(x) for x in F[9] if x[0] == 26 and po2(x)['depth'] == 4][0]; assert kbtn['cid'] == 954
def mv(m, dx): return dict(m, tx=m['tx'] + dx)
BTN = {}
for i, (nm, c_card, c_lbl, c_btn, (dc, dl, db)) in enumerate(WAW):
    dx = OFF + i * DXV
    F[0].append(build_po2(dict(depth=dc, cid=c_card, matrix=mv(kcard['matrix'], dx))))
    F[0].append(build_po2(dict(depth=dl, cid=c_lbl, matrix=mv(klbl['matrix'], dx), name=nm + '_label')))
    BTN[nm] = dict(depth=db, cid=c_btn, matrix=mv(kbtn['matrix'], dx), cx=kbtn['cx'])
    F[0].append(build_po2(BTN[nm]))
lab = {k: [i for i, fr in enumerate(F) if any(x[0] == 43 and body(x) == k.encode() + b'\0' for x in fr)][0] for k in ('Nacht Select', 'Verruck Select', 'Proto Select')}
assert lab == {'Nacht Select': 36, 'Verruck Select': 44, 'Proto Select': 52}, lab
def seg_fix(k, own, prev):                                 # each 'X Select' removes X's button and restores the previous card's
    fr = [remove(BTN[own]['depth'])]
    if prev: fr.append(build_po2(dict(BTN[prev], ratio=k)))
    F[k] = fr + F[k]
seg_fix(36, 'nacht', None); seg_fix(44, 'verruck', 'nacht'); seg_fix(52, 'proto', 'verruck')
new = []
for k in range(52, 60):
    fr = []
    for x in F[k]:
        if x[0] == 28:
            dep = struct.unpack('<H', body(x))[0]; fr.append(remove({36: 40}.get(dep, dep))); continue
        if x[0] == 43: assert body(x) == b'Proto Select\0'; fr.append(label('Riese Select')); continue
        if x[0] == 12:
            a = body(x); cp = as2.pool(a); assert b'proto' in a
            fr.append(tag(12, as2.rewrite(a, cp, {b'proto': b'derriese'}), long=True)); continue
        d = po2(x)
        if d['depth'] == 32 and d.get('cid') == 1425: fr.append(build_po2(dict(BTN['proto'], ratio=60))); continue   # restore proto's button
        if d['depth'] == 37: d['depth'] = 41
        if 'matrix' in d: d['matrix'] = mv(d['matrix'], DXV)
        fr.append(build_po2(d))
    new.append(fr)
assert sum(1 for fr in new for x in fr if x[0] == 12) == 1
for fr in F[36:] + new:                                    # WaW segments: highlights (25/33/37/41) and the tick (23) follow the cards
    for j, x in enumerate(fr):
        if x[0] == 26:
            d = po2(x)
            if d['depth'] in (23, 25, 33, 37, 41) and 'matrix' in d: d['matrix'] = mv(d['matrix'], SHIFT - 18794); fr[j] = build_po2(d)
subs = []
for fr in F + new: subs += fr + [SHOWF]
out[gi(955)] = sprite_tag(sid, len(F) + len(new), subs + [END])
# card row (sprite 960): two pages. Page 1 = the 4 BO1 maps (as the original game), page 2 = REZURRECTION (the 4 WaW maps).
# The title banner becomes a REZURRECTION arrow: tapping it slides the card row by SHIFT (frame 22) or back (frame 21).
P_ARB, P_ARW, P_HIT, P_RZB = 1458, 1459, 1460, 1461
assert not used_ids & {P_ARB, P_ARW, P_HIT, P_RZB}
sid9, fc9, S9 = subtags(body(T[gi(960)])); assert fc9 == 20; F9 = frames_of(S9)
def setmember_text(inst, txt):   # inst.text = txt   (inst is a child of this timeline)
    return (as2.push_bytes([(0, inst)]) + b'\x1c' + as2.push_bytes([(0, b'text'), (0, txt)]) + b'\x4f')
def doaction(code): return tag(12, code + b'\0', long=True)
RZ, BO = b'REZURRECTION', b'BLACK OPS'
# title text: smaller so REZURRECTION fits the banner (same font, colour, italic)
ti = gi(959); tb = bytearray(body(T[ti])); r_, p_ = read_rect(bytes(tb), 2)
assert tb[p_:p_ + 2] == b'\x8d\x23' and struct.unpack_from('<H', tb, p_ + 4)[0] == 760
struct.pack_into('<H', tb, p_ + 4, 680)
old = b'size="38" color="#000000" letterSpacing="4.000000" kerning="0"><i>SELECT MAP</i>'; assert tb.count(old) == 1
tb = bytes(tb).replace(old, b'size="34" color="#000000" letterSpacing="3.000000" kerning="0"><i>REZURRECTION</i>')
out[ti] = tag(37, tb, long=True)
# arrow head on the right end of the banner (banner 958 local: x -2950..4630, y -671..1629), black edge + banner paper inside
bt = body(T[gi(958)]); _, q = read_rect(bt, 2); assert bt[q] == 2 and bt[q + 1] == 0x41 and struct.unpack_from('<H', bt, q + 2)[0] == 0xffff
_, q2 = read_matrix(bt, q + 4); assert bt[q2] == 0x41 and struct.unpack_from('<H', bt, q2 + 1)[0] == 83
_, q3 = read_matrix(bt, q2 + 3); paper = bytes(bt[q2:q3])                          # fill style 2 of the banner (bitmap 83 + matrix)
arb = build_poly(P_ARB, [(4560, -1150), (6150, 479), (4560, 2108)], b'\x00\x00\x00\x00')
arw = build_poly(P_ARW, [(4560, -930), (5930, 479), (4560, 1888)], paper)
hit = build_poly(P_HIT, [(-2950, -1150), (6150, -1150), (6150, 2108), (-2950, 2108)], b'\x00\x00\x00\x00')
# button: on(press) play the menu sound (copied from a card button) and flip the page
cb = body(T[gi(1438)]); k0 = cb.index(b'\x96\x18\x00\x00menu_press\x00'); k1 = cb.index(b'\x8c\x0d\x00Proto Select')
snd = cb[k0:k1]; assert snd.endswith(b'\x52\x17')
GF = lambda fr: b'\x81\x02\x00' + struct.pack('<H', fr)
cond = as2.push_bytes([(0, b''), (1, struct.pack('<f', 4.0))]) + b'\x22' + as2.push_bytes([(1, struct.pack('<f', 22.0))]) + b'\x49'
then_ = GF(20) + b'\x07'                                    # on page 2 -> frame 21 (page 1)
else_ = GF(21) + b'\x07' + b'\x99\x02\x00' + struct.pack('<h', len(then_))   # else -> frame 22 (page 2)
act = snd + cond + b'\x9d\x02\x00' + struct.pack('<h', len(else_)) + else_ + then_ + b'\0'
I0 = write_matrix(dict(tx=0, ty=0))
rec = (bytes([0x07]) + struct.pack('<HH', P_ARB, 1) + I0 + b'\x00' + bytes([0x07]) + struct.pack('<HH', P_ARW, 2) + I0 + b'\x00'
       + bytes([0x08]) + struct.pack('<HH', P_HIT, 3) + I0 + b'\x00' + b'\x00')   # arrow drawn by the button; whole banner+arrow is the touch area
btn = tag(34, struct.pack('<HBH', P_RZB, 0, 2 + len(rec)) + rec + struct.pack('<HH', 0, 0x0004) + act, long=True)
rec_chk = btn[1][btn[2]:]; assert struct.unpack_from('<H', rec_chk, 3)[0] == 2 + len(rec)
# timeline
S92 = []
for k, fr in enumerate(F9):
    m36 = [po2(x)['matrix'] for x in fr if x[0] == 26 and po2(x)['depth'] == 36]; assert len(m36) == 1
    nf = []
    for x in fr:
        if k == 19 and x[0] == 12: assert body(x) == b'\x07\x00'; nf.append(doaction(setmember_text(b'select_map', RZ) + b'\x07')); continue
        nf.append(x)
    for dep, c in ((46, P_RZB),):
        nf.append(build_po2(dict(depth=dep, cid=c, matrix=m36[0])) if k == 0 else build_po2(dict(depth=dep, move=True, matrix=m36[0])))
    S92 += nf + [SHOWF]
m11 = [po2(x)['matrix'] for x in F9[19] if x[0] == 26 and po2(x)['depth'] == 11][0]; assert 'sx' not in m11
S92 += [doaction(setmember_text(b'select_map', RZ) + b'\x07'), build_po2(dict(depth=11, move=True, matrix=m11)), SHOWF]
S92 += [doaction(setmember_text(b'select_map', BO) + b'\x07'), build_po2(dict(depth=11, move=True, matrix=mv(m11, -SHIFT))), SHOWF, END]
out[gi(960)] = sprite_tag(sid9, 22, S92)
ins.setdefault(gi(960), []).extend([arb, arw, hit, btn])
# ---------------- (2) lobby background (795): 'derriese' frame
sid7, fc7, S7 = subtags(body(T[gi(795)])); assert fc7 == 8
out[gi(795)] = sprite_tag(sid7, 9, S7[:-1] + [label('derriese'), build_po2(dict(depth=11, cid=P_LOBBY, move=True)), SHOWF, END])
# (3) lobby vote: left as the original game (4 Black Ops maps only)
# ---------------- (4) scripts: Der Riese tick clearing + labels
def add_after(a, key_strings, mapping):
    """copy the statement that pushes key_strings[-1] (a SetMember-terminated straight run) and insert it right after itself"""
    cp = as2.pool(a); R = as2.records(a)
    hit = [i for i, (p, c, d) in enumerate(R) if c == 0x96 and key_strings[0] in as2.strings_of(as2.push_items(d), cp)]
    assert len(hit) == 1, (key_strings, len(hit)); i = hit[0]
    s = i
    while not (R[s][1] == 0x96 and as2.strings_of(as2.push_items(R[s][2]), cp)[-1] == key_strings[1]): s -= 1
    e = i
    while R[e][1] != 0x4f: e += 1
    seg = a[R[s][0]:R[e][0] + 1]; newseg = as2.rewrite(seg, cp, mapping); assert newseg != seg
    return as2.insert(a, R[e][0] + 1, newseg)
for spr, key, first, mp in ((961, b'proto_label', b'mp_map_select', {b'proto_label': b'derriese_label', b'SHI NO NUMA': b'DER RIESE'}),):
    i = gi(spr); s_, f_, S_ = subtags(body(out[i])); n = 0
    for k, x in enumerate(S_):
        if x[0] == 12 and b'S_LEVEL_KINO' in body(x): S_[k] = tag(12, add_after(body(x), (key, first), mp), long=True); n += 1
    assert n == 1; out[i] = sprite_tag(s_, f_, S_)
i = gi(961); s_, f_, S_ = subtags(body(out[i])); n = 0
for kk, x in enumerate(S_):
    if x[0] == 12 and b'S_MENU_SELECT_MAP' in body(x):
        a_ = body(x); cp = as2.pool(a_); R = as2.records(a_)
        h_ = [j for j, (p, c, d) in enumerate(R) if c == 0x96 and b'S_MENU_SELECT_MAP' in as2.strings_of(as2.push_items(d), cp)]; assert len(h_) == 1
        j = h_[0]
        while R[j][1] != 0x17: j += 1                      # end of the localiseText(...) call statement
        st = (as2.push_bytes([(0, b'_root')]) + b'\x1c' + as2.push_bytes([(0, b'MultiConnectionType')]) + b'\x4e' + as2.push_bytes([(0, b'mp_map_select')]) + b'\x4e'
              + as2.push_bytes([(0, b'select_map')]) + b'\x4e' + as2.push_bytes([(0, b'text'), (0, b'REZURRECTION')]) + b'\x4f')
        S_[kk] = tag(12, as2.insert(a_, R[j][0] + 1, st), long=True); n += 1
assert n == 1; out[i] = sprite_tag(s_, f_, S_)
# ---------------- definitions before their users
ins.setdefault(gi(955), []).extend([mp_dr, lbl_dr, lbl_dr_csm, btn_dr])
ins.setdefault(gi(795), []).append(lobby_dr)
final = []
for i, t in enumerate(out): final += ins.get(i, []); final.append(t)
res = build(h, final); open(DST, 'wb').write(res); print('menu ok', len(res), len(T), '->', len(final))
