"""Map name 'CALL OF / THE DEAD: / Director's / Cut' (4 lines, lower-case letters the menu font draws badly) ->
'CALL OF / THE DEAD'. Same string slot: the rest is padded with zero bytes, so the file size and the string offsets stay."""
import sys; sys.path.insert(0, '/root/work/drdeb'); from entlib import *
OLD = b"\0CALL OF\nTHE DEAD:\nDirector's\nCut\0"; NEW = b"\0CALL OF\nTHE DEAD\0"
for nm in ('english_us.dat', 'english_uk.dat'):
    b = get('localisation', nm); assert b.count(OLD) == 1, nm
    out = b.replace(OLD, NEW + b'\0' * (len(OLD) - len(NEW))); assert len(out) == len(b)
    open(sys.argv[1] + '/' + nm, 'wb').write(out); print(nm, 'ok')
