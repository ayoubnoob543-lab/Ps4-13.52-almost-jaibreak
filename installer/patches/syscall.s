.intel_syntax noprefix

.extern __error

.text

.globl syscall
syscall:
	xor rax, rax

.globl syscall_macro
syscall_macro:
	mov r10, rcx
	syscall
	jb _error
	ret

_error:
	cmp qword ptr __error[rip], 0
	jz _end
	push rax
	call __error[rip]
	pop rcx
	mov [rax], ecx
	mov rax, -1
	mov rdx, -1

_end:
	ret

/* Repo-local adaptation of ps4-payload-sdk source/syscall.s.
   Upstream used GNU-as-tolerated `movq reg, imm` in Intel syntax; LLVM's
   integrated assembler requires plain `mov` there. Semantics identical. */
