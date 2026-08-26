#pragma once

#ifndef SYSCALL_H
#define SYSCALL_H

#include "types.h"

/*
 * Repo-local adaptation of ps4-payload-sdk include/syscall.h.
 *
 * Upstream emits `.intel_syntax noprefix` and the instructions through
 * separate top-level __asm__ statements. GNU ld/gcc keeps the dialect
 * state across them, but clang's integrated assembler parses each
 * string independently and rejects the instructions. Joining everything
 * into a single asm block is byte-identical at the object level and
 * works on both compilers.
 */

#define SYSCALL(name, number)             \
  __asm__(".intel_syntax noprefix\n\t"    \
          ".globl " #name "\n"            \
          #name ":\n\t"                   \
          "mov rax, " #number "\n\t"      \
          "jmp syscall_macro\n\t"              \
          ".att_syntax prefix");

unsigned long syscall(unsigned long n, ...);

#endif
