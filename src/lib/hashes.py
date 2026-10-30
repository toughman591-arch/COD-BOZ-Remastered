M=0xffffffff
def djb2(s):
    h=5381
    for c in s.encode(): h=(h*33+c)&M
    return h
def djb2x(s):
    h=5381
    for c in s.encode(): h=((h*33)^c)&M
    return h
def sdbm(s):
    h=0
    for c in s.encode(): h=(c+(h<<6)+(h<<16)-h)&M
    return h
def fnv1(s):
    h=0x811c9dc5
    for c in s.encode(): h=((h*0x01000193)&M)^c
    return h
def fnv1a(s):
    h=0x811c9dc5
    for c in s.encode(): h=((h^c)*0x01000193)&M
    return h
def oaat(s):
    h=0
    for c in s.encode():
        h=(h+c)&M;h=(h+(h<<10))&M;h^=h>>6
    h=(h+(h<<3))&M;h^=h>>11;h=(h+(h<<15))&M;return h
FUNCS=dict(djb2=djb2,djb2x=djb2x,sdbm=sdbm,fnv1=fnv1,fnv1a=fnv1a,oaat=oaat)
