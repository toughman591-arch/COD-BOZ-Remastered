SECTIONS {
  .hookInitMP 0x203fd6 : { *(.hookInitMP) }
  .hookLit 0x204bee : { *(.hookLit) }
  .hookImg 0x204df4 : { *(.hookImg) }
  .hookOwn 0x204f44 : { *(.hookOwn) }
  .hookShow 0x20533e : { *(.hookShow) }
  .hookDS2 0x20d152 : { *(.hookDS2) }
  .hookDS1 0x257a34 : { *(.hookDS1) }
  .hookHas 0x258234 : { *(.hookHas) }
  .hookRefill 0x2584d6 : { *(.hookRefill) }
  .hookSwap 0x259750 : { *(.hookSwap) }
  .hookGive 0x2597c8 : { *(.hookGive) }
  .hookSave 0x25c170 : { *(.hookSave) }
  .hookLoad 0x25c216 : { *(.hookLoad) }
  .mcave2 0x3d9490 : { *(.mcave2) }
  .mcave 0x400a40 : { *(.mcave) }
}
LM = 0x499cc0;
PERKMGR = 0x2050ad; HASPERK = 0x2052c7; EQUIP = 0x259449;
GIVE_CONT = 0x2597cf; SWAP_TAIL = 0x25973d; SWAP_CONT = 0x25972d;
WALLBUY_RET = 0x2557e7; BOX_RET = 0x1f3d65; NETBUY_RET = 0x2472bb;
DSSTR = 0x3e8fc6; WREFILL = 0x2570fd; REFILL_CONT = 0x2584db; HUDPTR = 0x49ab00; OWN_CONT = 0x204f49;
RESMGR = 0x4cbf90; GETRES = 0x26e6a1; LIT_CONT = 0x204bf3; HLIT = 0xed48abc1; HMACH = 0xe0c8a5af;
FINDENT = 0xf6995; RMFROM = 0x2656fd; SETVIS = 0x265a29; INITMP_STORE = 0x203fdd; INITMP_SKIP = 0x20401d;
SAVE_LOOP = 0x25c139; SAVE_DONE = 0x25c0ff; ELEMINIT = 0x257175; PUSHB = 0x25a191; FINDW = 0x2572f3; LOAD_EXIT = 0x25c259; LOAD_CONT = 0x25c21b;
