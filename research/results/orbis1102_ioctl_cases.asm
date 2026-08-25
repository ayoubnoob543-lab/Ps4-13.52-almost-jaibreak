
===== CASE DECRYPT_HDR(01) @ 0xffffffff83beac44 =====
  0xffffffff83beac44: mov rsi, qword ptr [r12]
  0xffffffff83beac48: mov rdx, qword ptr [r12 + 8]
  0xffffffff83beac4d: mov r9d, dword ptr [r12 + 0x10]
  0xffffffff83beac52: mov rdi, r15
  0xffffffff83beac55: xor ecx, ecx
  0xffffffff83beac57: xor r8d, r8d
  0xffffffff83beac5a: jmp 0xffffffff83bead8f
  0xffffffff83beac5f: mov eax, 0xc008440b
  0xffffffff83beac64: cmp rbx, rax
  0xffffffff83beac67: je 0xffffffff83beb1e6
  0xffffffff83beac6d: mov eax, 0xc010440a
  0xffffffff83beac72: cmp rbx, rax
  0xffffffff83beac75: je 0xffffffff83beb2e7
  0xffffffff83beac7b: mov eax, 0xc010440d
  0xffffffff83beac80: cmp rbx, rax
  0xffffffff83beac83: jne 0xffffffff83beb55b
  0xffffffff83beac89: mov rbx, qword ptr [r12]
  0xffffffff83beac8d: test rbx, rbx
  0xffffffff83beac90: je 0xffffffff83beb55b
  0xffffffff83beac96: cmp qword ptr [r12 + 8], 0x400
  0xffffffff83beac9f: jne 0xffffffff83beb55b
  0xffffffff83beaca5: mov r12, qword ptr [r15 + 0x30]
  0xffffffff83beaca9: mov eax, 0x280
  0xffffffff83beacae: lea rsi, [rip + 0x4b3772]
  0xffffffff83beacb5: mov rdi, qword ptr gs:[0]
  0xffffffff83beacbe: xor edx, edx
  0xffffffff83beacc0: add r12, rax
  0xffffffff83beacc3: call 0xffffffff83a3d6a0   [call → 0xffffffff83a3d6a0]
  0xffffffff83beacc8: mov edx, 0x400
  0xffffffff83beaccd: mov rdi, rbx
  0xffffffff83beacd0: mov rsi, r12
  0xffffffff83beacd3: call 0xffffffff83892000   [call → 0xffffffff83892000]
  0xffffffff83beacd8: mov r13d, eax
  0xffffffff83beacdb: test eax, eax
  0xffffffff83beacdd: jne 0xffffffff83beb55b
  0xffffffff83beace3: lea rbx, [rbp - 0x170]
  0xffffffff83beacea: mov esi, 0x80
  0xffffffff83beacef: mov rdi, rbx
  0xffffffff83beacf2: call 0xffffffff83891d50   [call → 0xffffffff83891d50]
  0xffffffff83beacf7: mov qword ptr [rbp - 0x170], 0xf
  0xffffffff83bead02: mov eax, 0x280
  0xffffffff83bead07: mov rsi, rbx
  0xffffffff83bead0a: mov rdx, rbx
  0xffffffff83bead0d: add rax, qword ptr [r15 + 0x38]
  0xffffffff83bead11: mov qword ptr [rbp - 0x168], rax
  0xffffffff83bead18: mov qword ptr [rbp - 0x160], 0x400
  0xffffffff83bead23: mov qword ptr [rbp - 0x158], 0
  0xffffffff83bead2e: mov rdi, qword ptr [r15 + 0x28]
  0xffffffff83bead32: call 0xffffffff83be37b0   [call → 0xffffffff83be37b0]
  0xffffffff83bead37: mov r13d, 5
  0xffffffff83bead3d: test eax, eax
  0xffffffff83bead3f: jne 0xffffffff83beb55b
  0xffffffff83bead45: mov edi, dword ptr [rbp - 0x16c]
  0xffffffff83bead4b: call 0xffffffff83bea860   [call → 0xffffffff83bea860]
  0xffffffff83bead50: mov r13d, eax
  0xffffffff83bead53: jmp 0xffffffff83beb55b
  0xffffffff83bead58: mov eax, 0xc0284405
  0xffffffff83bead5d: cmp rbx, rax
  0xffffffff83bead60: je 0xffffffff83beb3ab
  0xffffffff83bead66: mov eax, 0xc0284409
  0xffffffff83bead6b: cmp rbx, rax
  0xffffffff83bead6e: jne 0xffffffff83beb55b
  0xffffffff83bead74: mov rsi, qword ptr [r12]
  0xffffffff83bead78: mov rdx, qword ptr [r12 + 8]
  0xffffffff83bead7d: mov rcx, qword ptr [r12 + 0x10]
  0xffffffff83bead82: mov r8, qword ptr [r12 + 0x18]
  0xffffffff83bead87: mov r9d, dword ptr [r12 + 0x20]
  0xffffffff83bead8c: mov rdi, r15
  0xffffffff83bead8f: call 0xffffffff83beb640   [call → 0xffffffff83beb640]
  0xffffffff83bead94: mov r13d, eax
  0xffffffff83bead97: jmp 0xffffffff83beb55b
  0xffffffff83bead9c: mov rdi, r15
  0xffffffff83bead9f: call 0xffffffff83be9ce0   [call → 0xffffffff83be9ce0]
  0xffffffff83beada4: mov r13d, eax
  0xffffffff83beada7: jmp 0xffffffff83beb55b
  0xffffffff83beadac: mov rdx, qword ptr [r15 + 0x30]
  0xffffffff83beadb0: mov ecx, 0x100
  0xffffffff83beadb5: mov rsi, qword ptr [r15 + 0x28]
  0xffffffff83beadb9: mov edi, 2
  0xffffffff83beadbe: add rdx, rcx
  0xffffffff83beadc1: add rcx, qword ptr [r15 + 0x38]
  0xffffffff83beadc5: call 0xffffffff83bea640   [call → 0xffffffff83bea640]
  0xffffffff83beadca: mov r13d, eax
  0xffffffff83beadcd: test eax, eax
  0xffffffff83beadcf: jne 0xffffffff83beb55b
  0xffffffff83beadd5: movzx eax, word ptr [rip + 0x204da24]
  0xffffffff83beaddc: mov ecx, dword ptr [rip + 0x204da22]
  0xffffffff83beade2: xor r13d, r13d
  0xffffffff83beade5: mov word ptr [rip + 0x204da16], ax
  0xffffffff83beadec: mov dword ptr [rip + 0x204da16], ecx
  0xffffffff83beadf2: jmp 0xffffffff83beb55b
  0xffffffff83beadf7: movzx eax, word ptr [r12]
  0xffffffff83beadfc: mov rcx, qword ptr [r12 + 8]
  0xffffffff83beae01: mov rbx, qword ptr [r12 + 0x10]
  0xffffffff83beae06: lea rdi, [rbp - 0x170]
  0xffffffff83beae0d: mov esi, 0x80
  0xffffffff83beae12: mov word ptr [rbp - 0x1e0], ax
  0xffffffff83beae19: mov qword ptr [rbp - 0x1d0], rcx
  0xffffffff83beae20: call 0xffffffff83891d50   [call → 0xffffffff83891d50]
  0xffffffff83beae25: lea rax, [rbx + 0x3fff]
  0xffffffff83beae2c: mov r13d, 0x16
  0xffffffff83beae32: mov qword ptr [rbp - 0x170], 2
  0xffffffff83beae3d: and rax, 0xffffffffffffc000
  0xffffffff83beae43: cmp rax, 0x4000
  0xffffffff83beae49: jne 0xffffffff83beb55b
  0xffffffff83beae4f: mov rax, qword ptr gs:[0]
  0xffffffff83beae58: mov r8, qword ptr [rax + 8]
  0xffffffff83beae5c: mov rsi, qword ptr [rbp - 0x1d0]
  0xffffffff83beae63: lea rdi, [rbp - 0xf0]
  0xffffffff83beae6a: lea r9, [rbp - 0x1c8]
  0xffffffff83beae71: mov ecx, 0x61
  0xffffffff83beae76: mov edx, 1
  0xffffffff83beae7b: mov qword ptr [rbp - 0xf0], 0
  0xffffffff83beae86: call 0xffffffff83bcf780   [call → 0xffffffff83bcf780]
  0xffffffff83beae8b: mov r13d, 0xc
  0xffffffff83beae91: test eax, eax
  0xffffffff83beae93: jne 0xffffffff83beb55b
  0xffffffff83beae99: mov rax, qword ptr [rbp - 0xf0]
  0xffffffff83beaea0: movzx ecx, word ptr [rbp - 0x1e0]
  0xffffffff83beaea7: mov qword ptr [rbp - 0x168], rax
  0xffffffff83beaeae: mov qword ptr [rbp - 0x160], rbx
  …

===== CASE VERIFY_SEG_ADD(02) @ 0xffffffff83beadf7 =====
  0xffffffff83beadf7: movzx eax, word ptr [r12]
  0xffffffff83beadfc: mov rcx, qword ptr [r12 + 8]
  0xffffffff83beae01: mov rbx, qword ptr [r12 + 0x10]
  0xffffffff83beae06: lea rdi, [rbp - 0x170]
  0xffffffff83beae0d: mov esi, 0x80
  0xffffffff83beae12: mov word ptr [rbp - 0x1e0], ax
  0xffffffff83beae19: mov qword ptr [rbp - 0x1d0], rcx
  0xffffffff83beae20: call 0xffffffff83891d50   [call → 0xffffffff83891d50]
  0xffffffff83beae25: lea rax, [rbx + 0x3fff]
  0xffffffff83beae2c: mov r13d, 0x16
  0xffffffff83beae32: mov qword ptr [rbp - 0x170], 2
  0xffffffff83beae3d: and rax, 0xffffffffffffc000
  0xffffffff83beae43: cmp rax, 0x4000
  0xffffffff83beae49: jne 0xffffffff83beb55b
  0xffffffff83beae4f: mov rax, qword ptr gs:[0]
  0xffffffff83beae58: mov r8, qword ptr [rax + 8]
  0xffffffff83beae5c: mov rsi, qword ptr [rbp - 0x1d0]
  0xffffffff83beae63: lea rdi, [rbp - 0xf0]
  0xffffffff83beae6a: lea r9, [rbp - 0x1c8]
  0xffffffff83beae71: mov ecx, 0x61
  0xffffffff83beae76: mov edx, 1
  0xffffffff83beae7b: mov qword ptr [rbp - 0xf0], 0
  0xffffffff83beae86: call 0xffffffff83bcf780   [call → 0xffffffff83bcf780]
  0xffffffff83beae8b: mov r13d, 0xc
  0xffffffff83beae91: test eax, eax
  0xffffffff83beae93: jne 0xffffffff83beb55b
  0xffffffff83beae99: mov rax, qword ptr [rbp - 0xf0]
  0xffffffff83beaea0: movzx ecx, word ptr [rbp - 0x1e0]
  0xffffffff83beaea7: mov qword ptr [rbp - 0x168], rax
  0xffffffff83beaeae: mov qword ptr [rbp - 0x160], rbx
  0xffffffff83beaeb5: mov word ptr [rbp - 0x158], cx
  0xffffffff83beaebc: mov word ptr [rbp - 0x156], 0
  0xffffffff83beaec5: mov dword ptr [rbp - 0x154], 0
  0xffffffff83beaecf: jmp 0xffffffff83beafdb
  0xffffffff83beaed4: movzx eax, word ptr [r12]
  0xffffffff83beaed9: mov rbx, qword ptr [r12 + 8]
  0xffffffff83beaede: mov r12, qword ptr [r12 + 0x10]
  0xffffffff83beaee3: lea rdi, [rbp - 0x170]
  0xffffffff83beaeea: mov esi, 0x80
  0xffffffff83beaeef: mov word ptr [rbp - 0x1d0], ax
  0xffffffff83beaef6: call 0xffffffff83891d50   [call → 0xffffffff83891d50]
  0xffffffff83beaefb: lea rax, [r12 + 0x3fff]
  0xffffffff83beaf03: mov r13d, 0x16
  0xffffffff83beaf09: mov qword ptr [rbp - 0x170], 3
  0xffffffff83beaf14: and rax, 0xffffffffffffc000
  0xffffffff83beaf1a: cmp rax, 0x4000
  0xffffffff83beaf20: jne 0xffffffff83beb55b
  0xffffffff83beaf26: mov rax, qword ptr gs:[0]
  0xffffffff83beaf2f: mov r8, qword ptr [rax + 8]
  0xffffffff83beaf33: lea rdi, [rbp - 0xf0]
  0xffffffff83beaf3a: lea r9, [rbp - 0x1c8]
  0xffffffff83beaf41: mov ecx, 0x61
  0xffffffff83beaf46: mov rsi, rbx
  0xffffffff83beaf49: mov edx, 1
  0xffffffff83beaf4e: mov qword ptr [rbp - 0xf0], 0
  0xffffffff83beaf59: call 0xffffffff83bcf780   [call → 0xffffffff83bcf780]
  0xffffffff83beaf5e: mov r13d, 0xc
  0xffffffff83beaf64: test eax, eax
  0xffffffff83beaf66: jne 0xffffffff83beb55b
  0xffffffff83beaf6c: lea rdi, [rbp - 0x178]
  0xffffffff83beaf73: mov qword ptr [rbp - 0x178], 0
  0xffffffff83beaf7e: call 0xffffffff83be6fa0   [call → 0xffffffff83be6fa0]
  0xffffffff83beaf83: mov ecx, 0x4effa200
  0xffffffff83beaf88: add rcx, qword ptr [rbp - 0x178]
  0xffffffff83beaf8f: xor edx, edx
  0xffffffff83beaf91: test eax, eax
  0xffffffff83beaf93: mov rsi, qword ptr [rbp - 0xf0]
  0xffffffff83beaf9a: mov qword ptr [rbp - 0x168], rsi
  0xffffffff83beafa1: mov qword ptr [rbp - 0x160], r12
  0xffffffff83beafa8: mov qword ptr [rbp - 0x158], 0
  0xffffffff83beafb3: cmove rdx, rcx
  0xffffffff83beafb7: movzx ecx, word ptr [rbp - 0x1d0]
  0xffffffff83beafbe: mov qword ptr [rbp - 0x178], rdx
  0xffffffff83beafc5: mov word ptr [rbp - 0x150], cx
  0xffffffff83beafcc: mov word ptr [rbp - 0x14e], 0
  0xffffffff83beafd5: mov dword ptr [rbp - 0x14c], edx
  0xffffffff83beafdb: mov rdi, qword ptr [r15 + 0x28]
  0xffffffff83beafdf: lea rdx, [rbp - 0x170]
  0xffffffff83beafe6: mov rsi, rdx
  0xffffffff83beafe9: call 0xffffffff83be37b0   [call → 0xffffffff83be37b0]
  0xffffffff83beafee: mov r13d, 5
  0xffffffff83beaff4: test eax, eax
  0xffffffff83beaff6: jne 0xffffffff83beb54f
  0xffffffff83beaffc: mov edi, dword ptr [rbp - 0x16c]
  0xffffffff83beb002: call 0xffffffff83bea860   [call → 0xffffffff83bea860]
  0xffffffff83beb007: mov r13d, eax
  0xffffffff83beb00a: jmp 0xffffffff83beb54f
  0xffffffff83beb00f: movzx eax, word ptr [r12]
  0xffffffff83beb014: mov rbx, qword ptr [r12 + 8]
  0xffffffff83beb019: mov r12, qword ptr [r12 + 0x10]
  0xffffffff83beb01e: lea rdi, [rbp - 0x170]
  0xffffffff83beb025: mov esi, 0x80
  0xffffffff83beb02a: mov word ptr [rbp - 0x1d0], ax
  0xffffffff83beb031: call 0xffffffff83891d50   [call → 0xffffffff83891d50]
  0xffffffff83beb036: lea r8, [rip + 0x2054fc3]
  0xffffffff83beb03d: lea rdi, [rbp - 0x178]
  0xffffffff83beb044: lea rsi, [rbp - 0x180]
  0xffffffff83beb04b: mov r9d, 0x4000
  0xffffffff83beb051: mov rdx, rbx
  0xffffffff83beb054: mov rcx, r12
  0xffffffff83beb057: mov qword ptr [rbp - 0x170], 4
  0xffffffff83beb062: mov qword ptr [rbp - 0x178], 0
  0xffffffff83beb06d: mov qword ptr [rbp - 0x1e0], rbx
  0xffffffff83beb074: call 0xffffffff83be2fa0   [call → 0xffffffff83be2fa0]
  0xffffffff83beb079: mov r13d, eax
  0xffffffff83beb07c: test eax, eax
  0xffffffff83beb07e: jne 0xffffffff83beb55b
  0xffffffff83beb084: movzx ebx, word ptr [rbp - 0x1d0]
  0xffffffff83beb08b: lea rdx, [rip + 0x2054f6e]
  0xffffffff83beb092: lea rdi, [rbp - 0x188]
  0xffffffff83beb099: lea rsi, [rbp - 0x190]
  0xffffffff83beb0a0: mov qword ptr [rbp - 0x188], 0
  0xffffffff83beb0ab: call 0xffffffff83be2f70   [call → 0xffffffff83be2f70]
  0xffffffff83beb0b0: mov r13d, eax
  0xffffffff83beb0b3: test eax, eax
  0xffffffff83beb0b5: jne 0xffffffff83beb1da
  0xffffffff83beb0bb: mov rax, qword ptr [rbp - 0x188]
  0xffffffff83beb0c2: lea rdx, [rbp - 0x170]
  0xffffffff83beb0c9: mov rsi, rdx
  0xffffffff83beb0cc: mov qword ptr [rbp - 0x168], rax
  0xffffffff83beb0d3: mov word ptr [rbp - 0x160], bx
  …

===== CASE VERIFY_SEG(03) @ 0xffffffff83beaed4 =====
  0xffffffff83beaed4: movzx eax, word ptr [r12]
  0xffffffff83beaed9: mov rbx, qword ptr [r12 + 8]
  0xffffffff83beaede: mov r12, qword ptr [r12 + 0x10]
  0xffffffff83beaee3: lea rdi, [rbp - 0x170]
  0xffffffff83beaeea: mov esi, 0x80
  0xffffffff83beaeef: mov word ptr [rbp - 0x1d0], ax
  0xffffffff83beaef6: call 0xffffffff83891d50   [call → 0xffffffff83891d50]
  0xffffffff83beaefb: lea rax, [r12 + 0x3fff]
  0xffffffff83beaf03: mov r13d, 0x16
  0xffffffff83beaf09: mov qword ptr [rbp - 0x170], 3
  0xffffffff83beaf14: and rax, 0xffffffffffffc000
  0xffffffff83beaf1a: cmp rax, 0x4000
  0xffffffff83beaf20: jne 0xffffffff83beb55b
  0xffffffff83beaf26: mov rax, qword ptr gs:[0]
  0xffffffff83beaf2f: mov r8, qword ptr [rax + 8]
  0xffffffff83beaf33: lea rdi, [rbp - 0xf0]
  0xffffffff83beaf3a: lea r9, [rbp - 0x1c8]
  0xffffffff83beaf41: mov ecx, 0x61
  0xffffffff83beaf46: mov rsi, rbx
  0xffffffff83beaf49: mov edx, 1
  0xffffffff83beaf4e: mov qword ptr [rbp - 0xf0], 0
  0xffffffff83beaf59: call 0xffffffff83bcf780   [call → 0xffffffff83bcf780]
  0xffffffff83beaf5e: mov r13d, 0xc
  0xffffffff83beaf64: test eax, eax
  0xffffffff83beaf66: jne 0xffffffff83beb55b
  0xffffffff83beaf6c: lea rdi, [rbp - 0x178]
  0xffffffff83beaf73: mov qword ptr [rbp - 0x178], 0
  0xffffffff83beaf7e: call 0xffffffff83be6fa0   [call → 0xffffffff83be6fa0]
  0xffffffff83beaf83: mov ecx, 0x4effa200
  0xffffffff83beaf88: add rcx, qword ptr [rbp - 0x178]
  0xffffffff83beaf8f: xor edx, edx
  0xffffffff83beaf91: test eax, eax
  0xffffffff83beaf93: mov rsi, qword ptr [rbp - 0xf0]
  0xffffffff83beaf9a: mov qword ptr [rbp - 0x168], rsi
  0xffffffff83beafa1: mov qword ptr [rbp - 0x160], r12
  0xffffffff83beafa8: mov qword ptr [rbp - 0x158], 0
  0xffffffff83beafb3: cmove rdx, rcx
  0xffffffff83beafb7: movzx ecx, word ptr [rbp - 0x1d0]
  0xffffffff83beafbe: mov qword ptr [rbp - 0x178], rdx
  0xffffffff83beafc5: mov word ptr [rbp - 0x150], cx
  0xffffffff83beafcc: mov word ptr [rbp - 0x14e], 0
  0xffffffff83beafd5: mov dword ptr [rbp - 0x14c], edx
  0xffffffff83beafdb: mov rdi, qword ptr [r15 + 0x28]
  0xffffffff83beafdf: lea rdx, [rbp - 0x170]
  0xffffffff83beafe6: mov rsi, rdx
  0xffffffff83beafe9: call 0xffffffff83be37b0   [call → 0xffffffff83be37b0]
  0xffffffff83beafee: mov r13d, 5
  0xffffffff83beaff4: test eax, eax
  0xffffffff83beaff6: jne 0xffffffff83beb54f
  0xffffffff83beaffc: mov edi, dword ptr [rbp - 0x16c]
  0xffffffff83beb002: call 0xffffffff83bea860   [call → 0xffffffff83bea860]
  0xffffffff83beb007: mov r13d, eax
  0xffffffff83beb00a: jmp 0xffffffff83beb54f
  0xffffffff83beb00f: movzx eax, word ptr [r12]
  0xffffffff83beb014: mov rbx, qword ptr [r12 + 8]
  0xffffffff83beb019: mov r12, qword ptr [r12 + 0x10]
  0xffffffff83beb01e: lea rdi, [rbp - 0x170]
  0xffffffff83beb025: mov esi, 0x80
  0xffffffff83beb02a: mov word ptr [rbp - 0x1d0], ax
  0xffffffff83beb031: call 0xffffffff83891d50   [call → 0xffffffff83891d50]
  0xffffffff83beb036: lea r8, [rip + 0x2054fc3]
  0xffffffff83beb03d: lea rdi, [rbp - 0x178]
  0xffffffff83beb044: lea rsi, [rbp - 0x180]
  0xffffffff83beb04b: mov r9d, 0x4000
  0xffffffff83beb051: mov rdx, rbx
  0xffffffff83beb054: mov rcx, r12
  0xffffffff83beb057: mov qword ptr [rbp - 0x170], 4
  0xffffffff83beb062: mov qword ptr [rbp - 0x178], 0
  0xffffffff83beb06d: mov qword ptr [rbp - 0x1e0], rbx
  0xffffffff83beb074: call 0xffffffff83be2fa0   [call → 0xffffffff83be2fa0]
  0xffffffff83beb079: mov r13d, eax
  0xffffffff83beb07c: test eax, eax
  0xffffffff83beb07e: jne 0xffffffff83beb55b
  0xffffffff83beb084: movzx ebx, word ptr [rbp - 0x1d0]
  0xffffffff83beb08b: lea rdx, [rip + 0x2054f6e]
  0xffffffff83beb092: lea rdi, [rbp - 0x188]
  0xffffffff83beb099: lea rsi, [rbp - 0x190]
  0xffffffff83beb0a0: mov qword ptr [rbp - 0x188], 0
  0xffffffff83beb0ab: call 0xffffffff83be2f70   [call → 0xffffffff83be2f70]
  0xffffffff83beb0b0: mov r13d, eax
  0xffffffff83beb0b3: test eax, eax
  0xffffffff83beb0b5: jne 0xffffffff83beb1da
  0xffffffff83beb0bb: mov rax, qword ptr [rbp - 0x188]
  0xffffffff83beb0c2: lea rdx, [rbp - 0x170]
  0xffffffff83beb0c9: mov rsi, rdx
  0xffffffff83beb0cc: mov qword ptr [rbp - 0x168], rax
  0xffffffff83beb0d3: mov word ptr [rbp - 0x160], bx
  0xffffffff83beb0da: mov word ptr [rbp - 0x15e], 0
  0xffffffff83beb0e3: mov dword ptr [rbp - 0x15c], 0
  0xffffffff83beb0ed: mov rdi, qword ptr [r15 + 0x28]
  0xffffffff83beb0f1: call 0xffffffff83be37b0   [call → 0xffffffff83be37b0]
  0xffffffff83beb0f6: mov r13d, 5
  0xffffffff83beb0fc: test eax, eax
  0xffffffff83beb0fe: jne 0xffffffff83beb1ce
  0xffffffff83beb104: mov edi, dword ptr [rbp - 0x16c]
  0xffffffff83beb10a: call 0xffffffff83bea860   [call → 0xffffffff83bea860]
  0xffffffff83beb10f: mov r13d, eax
  0xffffffff83beb112: test eax, eax
  0xffffffff83beb114: jne 0xffffffff83beb1ce
  0xffffffff83beb11a: movzx eax, word ptr [rbp - 0x15e]
  0xffffffff83beb121: lea ecx, [rax - 0x13]
  0xffffffff83beb124: cmp cx, 6
  0xffffffff83beb128: jae 0xffffffff83beb598
  0xffffffff83beb12e: mov r13d, 0x16
  0xffffffff83beb134: cmp r12, 0x3e000
  0xffffffff83beb13b: jne 0xffffffff83beb1ce
  0xffffffff83beb141: lea rdi, [rbp - 0xf0]
  0xffffffff83beb148: mov esi, 0x88
  0xffffffff83beb14d: lea rax, [rbp - 0x60]
  0xffffffff83beb151: lea rbx, [rbp - 0x1c8]
  0xffffffff83beb158: mov qword ptr [rbp - 0x60], 0
  0xffffffff83beb160: mov qword ptr [rbp - 0x1c8], rdi
  0xffffffff83beb167: mov qword ptr [rbp - 0x58], rbx
  0xffffffff83beb16b: mov qword ptr [rbp - 0x1c0], rax
  0xffffffff83beb172: call 0xffffffff83891d50   [call → 0xffffffff83891d50]
  0xffffffff83beb177: mov rax, qword ptr [rbp - 0x1e0]
  0xffffffff83beb17e: mov dword ptr [rbp - 0x68], 2
  0xffffffff83beb185: mov dword ptr [rbp - 0xf0], 0x2041000
  0xffffffff83beb18f: mov dword ptr [rbp - 0xe8], 0x1f0
  0xffffffff83beb199: mov qword ptr [rbp - 0xe0], rax
  0xffffffff83beb1a0: mov qword ptr [rbp - 0xd8], rax
  …

===== CASE DECRYPT_SEG(04) @ 0xffffffff83beb00f =====
  0xffffffff83beb00f: movzx eax, word ptr [r12]
  0xffffffff83beb014: mov rbx, qword ptr [r12 + 8]
  0xffffffff83beb019: mov r12, qword ptr [r12 + 0x10]
  0xffffffff83beb01e: lea rdi, [rbp - 0x170]
  0xffffffff83beb025: mov esi, 0x80
  0xffffffff83beb02a: mov word ptr [rbp - 0x1d0], ax
  0xffffffff83beb031: call 0xffffffff83891d50   [call → 0xffffffff83891d50]
  0xffffffff83beb036: lea r8, [rip + 0x2054fc3]
  0xffffffff83beb03d: lea rdi, [rbp - 0x178]
  0xffffffff83beb044: lea rsi, [rbp - 0x180]
  0xffffffff83beb04b: mov r9d, 0x4000
  0xffffffff83beb051: mov rdx, rbx
  0xffffffff83beb054: mov rcx, r12
  0xffffffff83beb057: mov qword ptr [rbp - 0x170], 4
  0xffffffff83beb062: mov qword ptr [rbp - 0x178], 0
  0xffffffff83beb06d: mov qword ptr [rbp - 0x1e0], rbx
  0xffffffff83beb074: call 0xffffffff83be2fa0   [call → 0xffffffff83be2fa0]
  0xffffffff83beb079: mov r13d, eax
  0xffffffff83beb07c: test eax, eax
  0xffffffff83beb07e: jne 0xffffffff83beb55b
  0xffffffff83beb084: movzx ebx, word ptr [rbp - 0x1d0]
  0xffffffff83beb08b: lea rdx, [rip + 0x2054f6e]
  0xffffffff83beb092: lea rdi, [rbp - 0x188]
  0xffffffff83beb099: lea rsi, [rbp - 0x190]
  0xffffffff83beb0a0: mov qword ptr [rbp - 0x188], 0
  0xffffffff83beb0ab: call 0xffffffff83be2f70   [call → 0xffffffff83be2f70]
  0xffffffff83beb0b0: mov r13d, eax
  0xffffffff83beb0b3: test eax, eax
  0xffffffff83beb0b5: jne 0xffffffff83beb1da
  0xffffffff83beb0bb: mov rax, qword ptr [rbp - 0x188]
  0xffffffff83beb0c2: lea rdx, [rbp - 0x170]
  0xffffffff83beb0c9: mov rsi, rdx
  0xffffffff83beb0cc: mov qword ptr [rbp - 0x168], rax
  0xffffffff83beb0d3: mov word ptr [rbp - 0x160], bx
  0xffffffff83beb0da: mov word ptr [rbp - 0x15e], 0
  0xffffffff83beb0e3: mov dword ptr [rbp - 0x15c], 0
  0xffffffff83beb0ed: mov rdi, qword ptr [r15 + 0x28]
  0xffffffff83beb0f1: call 0xffffffff83be37b0   [call → 0xffffffff83be37b0]
  0xffffffff83beb0f6: mov r13d, 5
  0xffffffff83beb0fc: test eax, eax
  0xffffffff83beb0fe: jne 0xffffffff83beb1ce
  0xffffffff83beb104: mov edi, dword ptr [rbp - 0x16c]
  0xffffffff83beb10a: call 0xffffffff83bea860   [call → 0xffffffff83bea860]
  0xffffffff83beb10f: mov r13d, eax
  0xffffffff83beb112: test eax, eax
  0xffffffff83beb114: jne 0xffffffff83beb1ce
  0xffffffff83beb11a: movzx eax, word ptr [rbp - 0x15e]
  0xffffffff83beb121: lea ecx, [rax - 0x13]
  0xffffffff83beb124: cmp cx, 6
  0xffffffff83beb128: jae 0xffffffff83beb598
  0xffffffff83beb12e: mov r13d, 0x16
  0xffffffff83beb134: cmp r12, 0x3e000
  0xffffffff83beb13b: jne 0xffffffff83beb1ce
  0xffffffff83beb141: lea rdi, [rbp - 0xf0]
  0xffffffff83beb148: mov esi, 0x88
  0xffffffff83beb14d: lea rax, [rbp - 0x60]
  0xffffffff83beb151: lea rbx, [rbp - 0x1c8]
  0xffffffff83beb158: mov qword ptr [rbp - 0x60], 0
  0xffffffff83beb160: mov qword ptr [rbp - 0x1c8], rdi
  0xffffffff83beb167: mov qword ptr [rbp - 0x58], rbx
  0xffffffff83beb16b: mov qword ptr [rbp - 0x1c0], rax
  0xffffffff83beb172: call 0xffffffff83891d50   [call → 0xffffffff83891d50]
  0xffffffff83beb177: mov rax, qword ptr [rbp - 0x1e0]
  0xffffffff83beb17e: mov dword ptr [rbp - 0x68], 2
  0xffffffff83beb185: mov dword ptr [rbp - 0xf0], 0x2041000
  0xffffffff83beb18f: mov dword ptr [rbp - 0xe8], 0x1f0
  0xffffffff83beb199: mov qword ptr [rbp - 0xe0], rax
  0xffffffff83beb1a0: mov qword ptr [rbp - 0xd8], rax
  0xffffffff83beb1a7: mov qword ptr [rbp - 0xd0], 0x18
  0xffffffff83beb1b2: mov rdi, rbx
  0xffffffff83beb1b5: mov word ptr [rbp - 0xc8], 0x30
  0xffffffff83beb1be: call 0xffffffff83bd05e0   [call → 0xffffffff83bd05e0]
  0xffffffff83beb1c3: xor ecx, ecx
  0xffffffff83beb1c5: test eax, eax
  0xffffffff83beb1c7: setne cl
  0xffffffff83beb1ca: lea r13d, [rcx + rcx*4]
  0xffffffff83beb1ce: mov rdi, qword ptr [rbp - 0x190]
  0xffffffff83beb1d5: call 0xffffffff83bcfe60   [call → 0xffffffff83bcfe60]
  0xffffffff83beb1da: mov rdi, qword ptr [rbp - 0x180]
  0xffffffff83beb1e1: jmp 0xffffffff83beb556
  0xffffffff83beb1e6: mov r12, qword ptr [r12]
  0xffffffff83beb1ea: test r12, r12
  0xffffffff83beb1ed: je 0xffffffff83beb55b
  0xffffffff83beb1f3: lea rdi, [rip + 0x4b323c]
  0xffffffff83beb1fa: xor esi, esi
  0xffffffff83beb1fc: call 0xffffffff83983100   [call → 0xffffffff83983100]
  0xffffffff83beb201: mov r13d, 5
  0xffffffff83beb207: test rax, rax
  0xffffffff83beb20a: je 0xffffffff83beb55b
  0xffffffff83beb210: mov rsi, qword ptr [r15 + 0x30]
  0xffffffff83beb214: mov edx, 0x200
  0xffffffff83beb219: mov ecx, 0x90400
  0xffffffff83beb21e: mov rdi, rax
  0xffffffff83beb221: mov rbx, rax
  0xffffffff83beb224: call 0xffffffff83983250   [call → 0xffffffff83983250]
  0xffffffff83beb229: mov rdi, rbx
  0xffffffff83beb22c: mov qword ptr [rbp - 0x1d0], r12
  0xffffffff83beb233: mov r12d, eax
  0xffffffff83beb236: call 0xffffffff839831f0   [call → 0xffffffff839831f0]
  0xffffffff83beb23b: test r12d, r12d
  0xffffffff83beb23e: mov r12, qword ptr [rbp - 0x1d0]
  0xffffffff83beb245: jne 0xffffffff83beb55b
  0xffffffff83beb24b: lea rbx, [rbp - 0x170]
  0xffffffff83beb252: mov esi, 0x80
  0xffffffff83beb257: mov rdi, rbx
  0xffffffff83beb25a: call 0xffffffff83891d50   [call → 0xffffffff83891d50]
  0xffffffff83beb25f: mov qword ptr [rbp - 0x170], 0xe
  0xffffffff83beb26a: mov rsi, rbx
  0xffffffff83beb26d: mov rdx, rbx
  0xffffffff83beb270: mov rax, qword ptr [r15 + 0x38]
  0xffffffff83beb274: mov qword ptr [rbp - 0x168], rax
  0xffffffff83beb27b: add rax, 0x40
  0xffffffff83beb27f: mov qword ptr [rbp - 0x160], rax
  0xffffffff83beb286: mov qword ptr [rbp - 0x158], 0
  0xffffffff83beb291: mov rdi, qword ptr [r15 + 0x28]
  0xffffffff83beb295: call 0xffffffff83be37b0   [call → 0xffffffff83be37b0]
  0xffffffff83beb29a: mov r13d, 5
  0xffffffff83beb2a0: test eax, eax
  0xffffffff83beb2a2: jne 0xffffffff83beb55b
  0xffffffff83beb2a8: mov edi, dword ptr [rbp - 0x16c]
  0xffffffff83beb2ae: call 0xffffffff83bea860   [call → 0xffffffff83bea860]
  …
