import struct,sys
sys.path.insert(0,'/root/tools')
from hashes import djb2
def build_group(name,lists,children=(),header=bytes.fromhex('3d0307010000'),members_tail=b'\x01\x00\x00\x00'):
    """lists: [(class_name, [payload_bytes,...])], payload = item bytes after [flag][size].
       children: [(path, childname)] -> ResGroupChildPaths entries like kino groups."""
    out=bytearray(header)
    nm=name.encode()+b'\0'
    out+=struct.pack('<I',djb2('resgroupmembers'))+struct.pack('<I',4+len(nm)+len(members_tail))+nm+members_tail
    if children:
        out+=b'\x00'
        body=bytearray(struct.pack('<B',len(children)))
        for path,cn in children:
            body+=path.encode()+b'\0'+bytes.fromhex('0000000000100000')+struct.pack('<I',djb2(cn))
        out+=struct.pack('<I',djb2('resgroupchildpaths'))+struct.pack('<I',4+len(body))+body
    res=bytearray(struct.pack('<I',len(lists)))
    for cls,items in lists:
        res+=struct.pack('<II',djb2(cls.lower()),len(items))+b'\x01'
        for k,p in enumerate(items):
            if isinstance(p,tuple): fb,p=p
            else: fb=1 if k==0 else 0
            res+=bytes([fb])+struct.pack('<I',len(p)+5)+p
        res+=b'\x00'
    out+=struct.pack('<I',djb2('resgroupresources'))+struct.pack('<I',4+len(res))+res
    out+=b'\x00\x00\x00\x00'
    return bytes(out)
