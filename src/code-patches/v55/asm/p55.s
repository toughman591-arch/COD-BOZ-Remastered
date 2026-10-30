    .syntax unified
    .thumb
    .section .cave,"ax",%progbits
    .thumb_func
    .global isP
    .global blx_at
    .global cave1_end
    .global cave2_end
    .global cave3_end
    .global cave4_end
    .global blxw1
    .global blxw2
@ ---- Z=1 when the current level is 'pr...' (Shi No Numa); every register kept
isP:
    push {r0}
    ldr r0, .Llm
.Lp0: add r0, pc
    ldr r0, [r0]
    cbz r0, 1f
    ldrb.w r0, [r0, #0x55]
    cmp r0, #0x70
    bne 2f
    ldr r0, .Llm2
.Lp3: add r0, pc
    ldr r0, [r0]
    ldrb.w r0, [r0, #0x56]
    cmp r0, #0x72
2:  pop {r0}
    bx lr
1:  cmp r0, #1
    pop {r0}
    bx lr
    .align 2
.Llm:  .word LM - (.Lp0 + 4)
.Llm2: .word LM - (.Lp3 + 4)

@ ---- (a) trap switch 'is powered' read: on Shi No Numa (no power switch) power it on first use
    .thumb_func
caveA:
    ldrb.w r3, [r0, #0xa4]
    cbnz r3, 9f
    push {r0, r1, r2, lr}
    bl isP
    bne 8f
    movs r3, #1
    strb.w r3, [r0, #0xa4]
    ldr r3, .Levt
.Lp1: add r3, pc
    ldr r1, [r3, #4]
    adds r0, #8
    movs r2, #0
    movs r3, #0
    sub sp, #8
    str r2, [sp]
    bl POST
    add sp, #8
    movs r3, #1
8:  pop {r0, r1, r2, pc}
9:  bx lr
    .align 2
.Levt: .word EVT - (.Lp1 + 4)

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

@ ---- (e) zipline 'open' read: Call of the Dead opens its ziplines with a map event Shi No Numa doesn't have; open it here
    .thumb_func
caveZ:
    ldrb.w r2, [r0, #0x64]
    cbnz r2, 1f
    push {lr}
    bl isP
    bne 2f
    movs r2, #1
    strb.w r2, [r0, #0x64]
2:  pop {pc}
1:  bx lr
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
@ ---- every grave dug? Z=1 yes (a grave's upgraded-ammo cost = -1 marks it dug). Keeps r4-r11.
    .thumb_func
allgraves:
    push {r4, r5, r6, lr}
    adr r5, .Lgraves
1:  ldr r0, [r5], #4
    cbz r0, 5f
    bl ENT
    cmp r0, #0
    beq 1b
    bl GETCHALK
    cmp r0, #0
    beq 1b
    ldr.w r0, [r0, #0x8c]
    adds r0, #1
    beq 1b
    pop {r4, r5, r6, pc}
5:  cmp r0, r0
    pop {r4, r5, r6, pc}
@ ---- (c) graves (the cost-0 wall buys): only once every door/debris is bought; each one digs once (its mound
@      disappears); the last grave dug gives the Wunderwaffe DG-2, the others give nothing
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
    bl hidemound
    bl allgraves
    bne 6f
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
    .align 2
.Lgraves:
    .word 0xca0be00a   @ SN_Grave_1
    .word 0xca0be00b   @ SN_Grave_2
    .word 0xca0be00c   @ SN_Grave_3
    .word 0xca0be00d   @ SN_Grave_4
    .word 0xca0be00e   @ SN_Grave_5
    .word 0xca0be00f   @ SN_Grave_6
    .word 0xca0be010   @ SN_Grave_7
    .word 0xca0be011   @ SN_Grave_8
    .word 0xca0be012   @ SN_Grave_9
    .word 0
cave2_end:
    .section .cave3,"ax",%progbits
@ ---- hide the dug grave's 'grave_mound' part (r4 = the grave's wall-buy component)
    .thumb_func
hidemound:
    push {r4, lr}
    ldr r0, [r4, #0xc]
    cbz r0, 9f
    bl HIER
    cbz r0, 9f
    ldr r1, .Lmound
    bl FINDCHILD
    cbz r0, 9f
    ldr r0, [r0, #0xc]
    cbz r0, 9f
    bl GETREND
    cbz r0, 9f
    movs r1, #0
    bl SETVIS
9:  pop {r4, pc}
    .align 2
.Lmound: .word 0xae319ffc   @ 'grave_mound'
cave3_end:
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
    .section .hookA2,"ax",%progbits
    bl caveA
    .section .hookA,"ax",%progbits
    bl caveA
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
    .section .hookE,"ax",%progbits
    bl caveZ
    .section .hookC,"ax",%progbits
    b.w caveC
