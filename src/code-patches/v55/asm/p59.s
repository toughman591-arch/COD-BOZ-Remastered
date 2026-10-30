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
    .global cave5_end
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
    bl trigsp
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
@ ---- v5.14: the intro triggers only in single player ([level manager]+0x208 = 1 in online/local co-op)
    .thumb_func
trigsp:
    push {r0, lr}
    ldr r0, .Llm4
.Lp4: add r0, pc
    ldr r0, [r0]
    cbz r0, 1f
    ldrb.w r0, [r0, #0x208]
    cbnz r0, 2f
1:  pop.w {r0, lr}
    b.w trig
2:  pop {r0, pc}
    .align 2
.Llm4: .word LM - (.Lp4 + 4)
@ ---- v5.15: character voice list. Call of the Dead in single player uses the game's own (unused) CharacterSoundListCotd
@      = trejo|rooker|englund|smg; Ascension keeps ...Asce, everything else ...Kino. Entered from 0x1cbc04 (replaces
@      strcmp(level, "ascension")) with r0 = level name, r3 = &level manager pointer.
    .thumb_func
caveVOICE:
    ldrb r0, [r0]
    cmp r0, #0x63
    bne 1f
    ldr r1, [r3]
    ldrb.w r1, [r1, #0x208]
    cbnz r1, 1f
    ldr r0, .Lcotdl
.Lp5: add r0, pc
    b.w K14
1:  subs r0, #0x61
    b.w K08
    .align 2
.Lcotdl: .word CSTR - (.Lp5 + 4)
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
    .word 0xca0be00a   @ SN_Grave_1 (Peter McCain)
    .word 0
    .align 2
.Lstr: .asciz "blackops-music/boz_c.mp3"
       .asciz "blackops-music/boz_k.mp3"
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
@ ---- (h) HUD prompt for a wall buy (hook 0x1da0ae): Peter's grave (the cost-0 wall buy on Shi No Numa) shows no
@      prompt; once every door/debris is bought, looking at it digs it up (the buy runs: caveC -> Wunderwaffe)
    .thumb_func
caveH:
    push {r4, lr}
    bl GETCHALK
    mov r4, r0
    cbz r0, 9f
    ldr.w r1, [r4, #0x84]
    cbnz r1, 9f
    bl isP
    bne 9f
    ldr.w r1, [r4, #0x8c]
    adds r1, #1
    beq 8f
    bl alldoors
    bne 8f
    mov r0, r4
    bl BUY
    mov.w r1, #-1
    str.w r1, [r4, #0x8c]
8:  movs r4, #0
9:  mov r0, r4
    pop {r4, pc}
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
    .section .hookS,"ax",%progbits
    b.w caveVOICE
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
    .section .hookH,"ax",%progbits
    bl caveH
    .section .hookC,"ax",%progbits
    b.w caveC
    .section .cave5,"ax",%progbits
@ ---- (v) level load (weapon-set lookup, once per map): Call of the Dead -> 'blackops-music/boz_c.mp3', Kino ->
@      'blackops-music/boz_k.mp3' through the music manager; the APK's audio code turns those into the intro video /
@      the 7 s loading clip (tap to skip) and holds the game until they end. Every register kept.
    .thumb_func
trig:
    push {r0, r1, r2, r3, r4, lr}
    ldr r1, .Lsb
.Lq4: add r1, pc
    ldrb r2, [r5, #1]
    cmp r0, #0x63
    bne 1f
    cmp r2, #0x61
    beq 5f
    b 9f
1:  cmp r0, #0x6b
    bne 9f
    cmp r2, #0x69
    bne 9f
    adds r1, #25
5:  sub sp, #8
    mov.w r2, #0x3f800000
    str r2, [sp]
    movs r2, #0
    str r2, [sp, #4]
    movs r2, #1
    ldr r0, .Lmm
.Lq3: add r0, pc
    ldr r0, [r0]
    movs r3, #1   @ v5.10: start now (stop the menu music) instead of queueing behind it
    bl PLAY
    add sp, #8
9:  pop {r0, r1, r2, r3, r4, pc}
    .align 2
.Lsb: .word .Lstr - (.Lq4 + 4)
.Lmm: .word MM - (.Lq3 + 4)
cave5_end:
