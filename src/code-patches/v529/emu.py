"""Run the co-op map-name lookup F (Thumb, 0x249f84) of a boz.s3e image in unicorn: returns the string F gives back."""
import lzma, struct, sys
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_ARM
from unicorn.arm_const import *
B = 3; HASH = 0x284eac; F = 0x249f84; STOP = 0x7ff00000; SCR = 0x7fe00000; STK = 0x7fd00000
def load(path):
    cc = open(path, 'rb').read(); raw = lzma.decompress(cc, format=lzma.FORMAT_ALONE); return raw[B:]
def mk(img):
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB); size = (len(img) + 0xfffff) & ~0xfffff
    mu.mem_map(0, size); mu.mem_write(0, img)
    for a in (STOP, SCR, STK): mu.mem_map(a, 0x100000)
    return mu
def call(mu, addr, thumb, r0):
    mu.reg_write(UC_ARM_REG_SP, STK + 0xff000); mu.reg_write(UC_ARM_REG_LR, STOP | 1); mu.reg_write(UC_ARM_REG_R0, r0)
    mu.emu_start(addr | (1 if thumb else 0), STOP, count=200000); return mu.reg_read(UC_ARM_REG_R0)
TBL = 0x453cec
def fill_tbl(mu, img):   # the 4-map table is filled at run time: simulate it (kino, ascension, deadops, callofthedead, NULL)
    import struct
    ptrs = [img.find(n + b'\0') for n in (b'kino', b'ascension', b'deadops', b'callofthedead')]
    mu.mem_write(TBL, struct.pack('<5I', *ptrs, 0))
def cstr(mu, p):
    b = bytes(mu.mem_read(p, 32)); return b.split(b'\0')[0]
def lookup(img, name):
    mu = mk(img); fill_tbl(mu, img); mu.mem_write(SCR, name + b'\0'); h = call(mu, HASH, False, SCR)
    r = call(mu, F, True, h); return (cstr(mu, r) if r else None), h
if __name__ == '__main__':
    img = load(sys.argv[1])
    for n in sys.argv[2:]: print(n, '->', lookup(img, n.encode()))
