    .syntax unified
    .thumb
@ ===== Mule Kick (test build, solo Kino only) =====
@ The weapon manager keeps 2 weapons: [mgr+0x1e0] = in hand, [mgr+0x1e4] = the other one. Mule Kick adds a hidden
@ third slot (MVAR). It is active only in single player, on Kino, while the player has perk type 0 (the Mule Kick
@ machine is a perk machine of type 0; Kino has no other type-0 machine). Losing the perk (going down) empties MVAR.
    .section .mcave,"ax",%progbits
    .thumb_func
@ ---- Z=1 + r0 = &MVAR when Mule Kick is active for the weapon manager in r4. Keeps r1-r3.
muleOn:
    push {r1, r2, r3, lr}
    ldr r0, .Lm_lm
.Lp_lm: add r0, pc
    ldr r0, [r0]
    cbz r0, 8f
    ldrb.w r1, [r0, #0x208]
    cbnz r1, 8f
    ldrb.w r1, [r0, #0x55]
    cmp r1, #0x6b              @ 'k'
    bne 8f
    ldrb.w r1, [r0, #0x56]
    cmp r1, #0x69              @ 'i'
    bne 8f
    ldr r0, [r4, #0xc]
    cbz r0, 8f
    bl PERKMGR
    cbz r0, 8f
    ldr r1, [r0, #0x58]
    lsls r1, r1, #31           @ perk type 0 bit -> N/Z
    beq 8f
    adr r0, MVAR
    cmp r0, r0
    pop {r1, r2, r3, pc}
8:  adr r0, MVAR
    movs r1, #0
    str r1, [r0]
    movs r1, #1
    cmp r1, #0
    pop {r1, r2, r3, pc}
    .align 2
.Lm_lm: .word LM - (.Lp_lm + 4)

@ ---- give weapon (core 0x25977c, slot type 0) from a wall buy / the mystery box with 2 guns already:
@      the other gun goes to the Mule Kick slot first, so the new gun becomes the 3rd instead of replacing one.
    .thumb_func
caveGive:
    push {r0, r1, r2, r3}
    ldr r0, [sp, #0x2c]        @ who called give (return address, thumb bit set)
    ldr r1, .Lg1
.Lq1: add r1, pc
    cmp r0, r1
    beq 1f
    ldr r1, .Lg2
.Lq2: add r1, pc
    cmp r0, r1
    beq 1f
    ldr r1, .Lg3
.Lq3: add r1, pc
    cmp r0, r1
    bne 9f
1:  bl muleOn
    bne 9f
    ldr.w r1, [r4, #0x1e0]
    cbz r1, 9f
    cmp r1, r5
    beq 9f
    ldr.w r2, [r4, #0x1e4]
    cbz r2, 9f
    cmp r2, r5
    beq 9f
    ldr r3, [r0]
    cbnz r3, 9f
    str r2, [r0]               @ MVAR = the other gun
    movs r2, #0
    str.w r2, [r4, #0x1e4]
9:  pop {r0, r1, r2, r3}
    ldr.w r2, [r4, #0x1e0]
    cmp r2, r5
    b.w GIVE_CONT
    .align 2
.Lg1: .word (WALLBUY_RET) - (.Lq1 + 4)
.Lg2: .word (BOX_RET) - (.Lq2 + 4)
.Lg3: .word (NETBUY_RET) - (.Lq3 + 4)

@ ---- swap button (0x259750): with 3 guns, cycle in-hand -> other -> Mule slot
    .thumb_func
caveSwap:
    ldr.w r1, [r4, #0x1e4]
    bl muleOn
    bne 7f
    ldr r2, [r0]
    cbz r2, 7f
    cbnz r1, 3f
    mov r1, r2                 @ no other gun but one in the Mule slot: take that one
    movs r2, #0
    str r2, [r0]
    b 7f
3:  ldr.w r3, [r4, #0x1e0]
    str r3, [r0]               @ Mule slot = gun in hand
    str.w r2, [r4, #0x1e4]     @ other = old Mule slot gun
    mov r0, r4
    movs r2, #1
    bl EQUIP                   @ in hand = old other gun
    b.w SWAP_TAIL
7:  b.w SWAP_CONT

@ ---- 'has weapon' (0x258218): the Mule slot gun counts as owned (wall buy = ammo, box won't offer it)
    .thumb_func
caveHas:
    mov r1, r0
    bl muleOn
    bne 1f
    ldr r0, [r0]
    cmp r0, r1
    bne 1f
    movs r0, #1
    pop {r4, pc}
1:  movs r0, #0
    pop {r4, pc}

@ ---- Deadshot perk checks: on Kino the type-0 perk is Mule Kick, so no Deadshot aim effect there
    .thumb_func
caveDS:
    ldr r2, .Lm_lm2
.Lp_lm2: add r2, pc
    ldr r2, [r2]
    cbz r2, 1f
    ldrb.w r3, [r2, #0x55]
    cmp r3, #0x6b
    bne 1f
    ldrb.w r3, [r2, #0x56]
    cmp r3, #0x69
    bne 1f
    movs r0, #0
    bx lr
1:  b.w HASPERK
    .align 2
.Lm_lm2: .word LM - (.Lp_lm2 + 4)
MVAR: .word 0
mcave_end:

    .section .hookGive,"ax",%progbits
    b.w caveGive
    nop
    .section .hookSwap,"ax",%progbits
    b.w caveSwap
    nop
    .section .hookHas,"ax",%progbits
    b.w caveHas
    .section .hookDS1,"ax",%progbits
    bl caveDS
    .section .hookDS2,"ax",%progbits
    bl caveDS

@ ===== Mule Kick v2: Max Ammo, own HUD icon and name, losing the perk takes the 3rd gun =====
    .section .mcave2,"ax",%progbits
@ ---- Z=1 when the current level is Kino. Clobbers r0, r1.
    .thumb_func
isKino:
    ldr r0, .Lm_lm3
.Lp_lm3: add r0, pc
    ldr r0, [r0]
    cbz r0, 1f
    ldrb.w r1, [r0, #0x55]
    cmp r1, #0x6b              @ 'k'
    bne 2f
    ldrb.w r1, [r0, #0x56]
    cmp r1, #0x69              @ 'i'
2:  bx lr
1:  cmp r0, #1                 @ no level: Z=0
    bx lr
    .align 2
.Lm_lm3: .word LM - (.Lp_lm3 + 4)

@ ---- PerkImageName case 0 (0x204df4): on Kino perk type 0 is Mule Kick
    .thumb_func
caveImg:
    push {r1, r2, r3, lr}
    bl isKino
    bne 1f
    adr r0, MULESTR
    pop {r1, r2, r3, pc}
1:  ldr r0, .Lds1
.Lpd1: add r0, pc
    pop {r1, r2, r3, pc}
    .align 2
.Lds1: .word DSSTR - (.Lpd1 + 4)

@ ---- PerkManager_ShowIcon (0x20533e, replaces mov r5,r1 / mov r6,r2): same swap for the icon name
    .thumb_func
caveShow:
    push {r0, r1, r2, lr}
    mov r5, r1
    mov r6, r2
    bl isKino
    bne 1f
    ldr r0, .Lds2
.Lpd2: add r0, pc
    cmp r5, r0
    bne 1f
    adr r5, MULESTR
1:  pop {r0, r1, r2, pc}
    .align 2
.Lds2: .word DSSTR - (.Lpd2 + 4)

@ ---- WeaponManager_RefillAll (0x2584d6, after the 5 slots): Max Ammo also refills the Mule Kick gun
    .thumb_func
caveRefill:
    bl muleOn
    bne 1f
    ldr r0, [r0]
    cbz r0, 1f
    movs r1, #0
    bl WREFILL
1:  ldr r3, .Lhud
.Lph: add r3, pc
    b.w REFILL_CONT
    .align 2
.Lhud: .word HUDPTR - (.Lph + 4)

@ ---- PerkManager_SetOwned (0x204f44): perk type 0 (Mule Kick) gone -> the 3rd gun is gone too
    .thumb_func
caveOwn:
    ldrb r3, [r0, #8]
    str r1, [r0, #0xc]
    lsls r2, r1, #31
    bne 1f
    ldr r2, .Lmv
.Lpmv: add r2, pc
    mov.w ip, #0
    str.w ip, [r2]
1:  b.w OWN_CONT

@ ===== Mule Kick v3: lit machine, online off, 3rd gun in saved games =====
@ ---- CPerk power on (0x204bee, replaces ldr.w r0,[r4,#0xc8]): Mule Kick on Kino -> logo material uses the lit texture
    .thumb_func
caveLit:
    push {r0, r5, r6, lr}
    ldr.w r3, [r4, #0xb0]
    cbnz r3, 9f
    bl isKino
    bne 9f
    ldr r0, .Lrm1
.Lprm1: add r0, pc
    ldr r0, [r0]
    cbz r0, 9f
    mov r6, r0
    ldr r1, .Lhmat
    adr r2, SMAT
    movs r3, #2
    bl GETRES
    cbz r0, 9f
    mov r5, r0
    mov r0, r6
    ldr r1, .Lhlit
    adr r2, STEX
    movs r3, #2
    bl GETRES
    cbz r0, 9f
    str r0, [r5, #0x2c]
9:  pop {r0, r5, r6, lr}
    ldr.w r0, [r4, #0xc8]
    b.w LIT_CONT
    .align 2
.Lrm1: .word RESMGR - (.Lprm1 + 4)
.Lhmat: .word 0x2cacdb8a           @ mule_kick_logo_mat
.Lhlit: .word HLIT                 @ mule_kick_logo_lit_tex
SMAT: .asciz "CIwMaterial"
STEX: .asciz "CIwTexture"
    .align 2

@ ---- CPerk::Init online branch (0x203fd6): online, Mule Kick (type 0 on Kino) can't be bought and its machine is hidden
    .thumb_func
caveInitMP:
    ldr.w r3, [r4, #0xb0]
    cbnz r3, 1f
    bl isKino
    bne 1f
    movs r3, #0
    strb.w r3, [r4, #0x7f]
    ldr r0, .Lhmach
    bl FINDENT
    cbz r0, 1f
    bl RMFROM
    cbz r0, 1f
    movs r1, #0
    bl SETVIS
1:  ldr.w r3, [r4, #0x88]
    cbz r3, 2f
    b.w INITMP_STORE
2:  b.w INITMP_SKIP
    .align 2
.Lhmach: .word HMACH                @ MuleKickMachine

@ ---- weapon save (0x25c170, end of the slot loop): + marker + the Mule Kick gun
    .thumb_func
caveSave:
    adds r5, #4
    cmp r5, #0x14
    beq 1f
    b.w SAVE_LOOP
1:  bl muleOn
    bne 9f
    ldr.w r9, [r0]
    cmp.w r9, #0
    beq 9f
    add.w r8, sp, #0x20
    mov r0, r8
    bl ELEMINIT
    ldr r0, .Lmagic1
    str r0, [sp, #0x24]
    add r0, sp, #0x14
    mov r1, r8
    bl PUSHB
    mov r0, r8
    bl ELEMINIT
    ldr.w r3, [r9, #0x5c]
    str r3, [sp, #0x24]
    ldr.w r3, [r9, #0x2c]
    str r3, [sp, #0x28]
    ldr.w r3, [r9, #0x30]
    str r3, [sp, #0x2c]
    ldr.w r3, [r9, #0x3c]
    cbz r3, 2f
    ldr r2, [r3, #0x2c]
    str r2, [sp, #0x30]
    ldr r3, [r3, #0x30]
    str r3, [sp, #0x34]
2:  add r0, sp, #0x14
    mov r1, r8
    bl PUSHB
9:  b.w SAVE_DONE
    .align 2
.Lmagic1: .word 0x454c554d         @ 'MULE'

@ ---- weapon load (0x25c216, replaces cmp r5,#5 / beq): the marker entry restores the Mule Kick gun, then stops
    .thumb_func
caveLoad:
    movs r0, #0x18
    mla r6, r0, r5, r3
    ldr r1, [r6, #4]
    ldr r0, .Lmagic2
    cmp r1, r0
    bne 2f
    adds r0, r5, #1
    cmp r0, r2
    bcs 3f
    bl isKino
    bne 3f
    ldrb.w r1, [r0, #0x208]
    cbnz r1, 3f
    adds r6, #0x18
    mov r0, r4
    ldr r1, [r6, #4]
    bl FINDW
    cbz r0, 3f
    ldr r1, [r6, #8]
    str r1, [r0, #0x2c]
    ldr r1, [r6, #0xc]
    str r1, [r0, #0x30]
    ldr r2, [r0, #0x3c]
    cbz r2, 4f
    ldr r1, [r6, #0x10]
    str r1, [r2, #0x2c]
    ldr r1, [r6, #0x14]
    str r1, [r2, #0x30]
4:  ldr r1, .Lmv3
.Lpmv3: add r1, pc
    str r0, [r1]
3:  b.w LOAD_EXIT
2:  cmp r5, #5
    beq 3b
    b.w LOAD_CONT
    .align 2
.Lmagic2: .word 0x454c554d
.Lmv3: .word MVAR - (.Lpmv3 + 4)
    .align 2
.Lmv: .word MVAR - (.Lpmv + 4)
MULESTR: .asciz "Perk_MuleKick_Image"
    .align 2

    .section .hookImg,"ax",%progbits
    b.w caveImg
    .section .hookShow,"ax",%progbits
    bl caveShow
    .section .hookRefill,"ax",%progbits
    b.w caveRefill
    .section .hookOwn,"ax",%progbits
    b.w caveOwn

    .section .hookLit,"ax",%progbits
    b.w caveLit
    .section .hookInitMP,"ax",%progbits
    b.w caveInitMP
    .section .hookSave,"ax",%progbits
    b.w caveSave
    .section .hookLoad,"ax",%progbits
    b.w caveLoad
