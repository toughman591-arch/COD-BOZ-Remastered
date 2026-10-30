
    .syntax unified
    .thumb
    .section .cave,"ax",%progbits
    .thumb_func
    .global blx_at
    .global cave1_end
    .global cave2_end
    .global cave4_end
    .global blxw1
    .global blxw2
@ ---- (b) weapon/arms set: 'proto' loads callofthedead's set (it has the Wunderwaffe DG-2)
    .thumb_func
caveB:
    cmp r0, #0x70
    bne 1f
    ldrb r1, [r5, #1]
    cmp r1, #0x72
    bne 2f
    ldr r1, .Lcotd
.Lp2: add r1, pc
    mov r0, r5
    .inst.w 0xf000c000   @ blx strcpy (filled in by patch_s3e51.py)
blx_at:
    b.w W52
1:  cmp r0, #0x6e
    bhs 2f
    b.w W52
2:  b.w W48
    .align 2
.Lcotd: .word COTD - (.Lp2 + 4)

cave1_end:
    .section .cave2,"ax",%progbits

@ ---- every door/debris of Shi No Numa bought? Z=1 yes. Keeps r4-r11.
    .thumb_func
alldoors:
    push {r4, r5, r6, lr}
    adr r5, .Ltab
1:  ldr r0, [r5], #4
    cbz r0, 5f
    bl ENT
    cmp r0, #0
    beq 1b
    bl GETDOOR
    cmp r0, #0
    beq 1b
    ldr.w r0, [r0, #0x9c]
    cmp r0, #2
    beq 1b
    pop {r4, r5, r6, pc}
5:  cmp r0, r0
    pop {r4, r5, r6, pc}
@ ---- (c) Wunderwaffe grave (the only cost-0 wall buy): every door bought, once
    .thumb_func
caveC:
    ldr.w r3, [r4, #0x84]
    cbnz r3, 7f
    ldr.w r3, [r4, #0x8c]
    adds r3, #1
    beq 6f
    bl alldoors
    bne 6f
    mov.w r3, #-1
    str.w r3, [r4, #0x8c]
7:  mov r0, r4
    ldr.w r5, [r4, #0x80]
    b.w RESUME
6:  b.w FAIL
    .align 2
.Ltab:
    .word 0x601c9a1f   @ SN_Debris01
    .word 0x4c849a9b   @ SN_Door02
    .word 0x4c849a9c   @ SN_Door03
    .word 0x4c849a9d   @ SN_Door04
    .word 0x4c849a9e   @ SN_Door05
    .word 0x4c849a9f   @ SN_Door06
    .word 0x4c849aa0   @ SN_Door07
    .word 0x4c849aa1   @ SN_Door08
    .word 0x4c849aa2   @ SN_Door09
    .word 0x4c849aba   @ SN_Door10
    .word 0
cave2_end:

    .section .cave4,"ax",%progbits
@ ---- (b2,b3) the same weapon-set name is rebuilt when the game looks up the loaded weapons_<set> and
@      weapon_projectiles_<set> groups (buffer on the stack): 'proto' -> callofthedead there too
    .macro WSET n, keep, kino
    .thumb_func
caveW\n:
    cmp r0, #0x70
    bne 1f
    ldrb.w r1, [sp, #1]
    cmp r1, #0x72
    bne 2f
    ldr r1, .Lc\n
.Lq\n: add r1, pc
    mov r0, sp
    .inst.w 0xf000c000
blxw\n:
    b.w \keep
1:  cmp r0, #0x6e
    bhs 2f
    b.w \keep
2:  b.w \kino
    .align 2
.Lc\n: .word COTD - (.Lq\n + 4)
    .endm
    WSET 1, WK1, WN1
    WSET 2, WK2, WN2
cave4_end:
    .section .hookB,"ax",%progbits
    b.w caveB
    nop
    nop
    .section .hookW1,"ax",%progbits
    b.w caveW1
    nop
    nop
    .section .hookW2,"ax",%progbits
    b.w caveW2
    nop
    nop
    .section .hookC,"ax",%progbits
    b.w caveC
