PS4SDK  ?= $(abspath $(CURDIR)/../third_party/ps4-payload-sdk)
LIBPS4  := $(PS4SDK)/libPS4

CC	:= gcc
OBJCOPY	:= objcopy
RM	:= rm
ODIR	:= build
SDIR	:= source
IDIR	:= include
IDIRS	 = -I$(CURDIR)/$(SDK_COPY)/include -I$(IDIR)
LDIRS	:= -L$(ODIR)
MAPFILE := $(shell basename $(CURDIR)).map
TARGET  := $(shell basename $(CURDIR)).bin

# Compiler flags
OPTIMIZATION := -Os
STANDARDS    := -std=c11 -fno-builtin -nostartfiles -nostdlib
WARNINGS     := -Wno-unused-const-variable -Wall -Wextra -Wno-error=implicit-int -Wno-error=int-conversion -Wno-error=incompatible-pointer-types -Wno-error=implicit-function-declaration # -Werror

# PS4 payloads are x86_64 (BTVER2). Detect how to invoke the compiler:
# 1) native x86_64 toolchain, or 2) clang-style driver with an explicit target.
PROBE_SRC := int main(void){return 0;}
X86_NATIVE := $(shell printf '$(PROBE_SRC)' | $(CC) -m64 -march=btver2 -mabi=sysv -mcmodel=small -x c -fsyntax-only - >/dev/null 2>&1 && echo yes)
X86_CLANG  := $(shell printf '$(PROBE_SRC)' | $(CC) --target=x86_64-unknown-freebsd13.0 -fuse-ld=lld -m64 -march=btver2 -mabi=sysv -mcmodel=small -x c -fsyntax-only - >/dev/null 2>&1 && echo yes)
ifneq ($(X86_NATIVE),yes)
  ifneq ($(X86_CLANG),yes)
    $(error no x86_64-capable compiler found for BTVER2 payload build)
  endif
  XARCH   := --target=x86_64-unknown-freebsd13.0 -fuse-ld=lld
  # clang's integrated assembler rejects AT&T snippets under -masm=intel,
  # and every inline asm site here is AT&T anyway; drop the flag in this mode.
  MASMINTEL :=
  OBJCOPY := $(if $(shell command -v llvm-objcopy >/dev/null 2>&1 && echo yes),llvm-objcopy,objcopy)
  AR      := $(if $(shell command -v llvm-ar >/dev/null 2>&1 && echo yes),llvm-ar,ar)
else
  XARCH :=
  MASMINTEL := -masm=intel
endif

CFLAGS       = $(IDIRS) $(OPTIMIZATION) $(STANDARDS) $(WARNINGS) $(MASMINTEL) -march=btver2 -mtune=btver2 -m64 -mabi=sysv -mcmodel=small -fpie $(XARCH) -ffunction-sections -fdata-sections

# Linker flags
LFLAGS	:= $(LDIRS) -Xlinker -T $(LIBPS4)/linker.x -Xlinker -Map=$(MAPFILE) -Wl,--build-id=none -Wl,--gc-sections -Wl,-z,noexecstack

# Source files discovery
CFILES	:= $(wildcard $(SDIR)/*.c)
SFILES	:= $(wildcard $(SDIR)/*.s)
OBJS	:= $(patsubst $(SDIR)/%.c, $(ODIR)/%.o, $(CFILES)) $(patsubst $(SDIR)/%.s, $(ODIR)/%.o, $(SFILES))
DEPS	:= $(OBJS:.o=.d)

# Libraries
LIBS	:= -lPS4

# Include dependency files
-include $(DEPS)

# Main targets
.PHONY: all
all: $(TARGET)

# Main build target
# Build the pinned SDK library from a local copy so the submodule tree stays
# pristine. Command-line variables override the copied Makefile on purpose;
# the flag string mirrors upstream libPS4/Makefile plus the x86_64 mode.
# The copy patches `typedef uint16_t wchar_t` to the ABI-correct builtin int,
# which both gcc and clang predefine; upstream's line breaks clang builds.
SDK_COPY   := build/sdk-libps4
SDKLIB     := $(ODIR)/libPS4.a

# The SDK's own inline asm is Intel syntax in every mode; kpayload's is AT&T.
SDK_CFLAGS := -I$(CURDIR)/$(SDK_COPY)/include -Os -std=c11 -ffunction-sections -fdata-sections -fno-builtin -nostartfiles -nostdlib -Wall -Wextra -Wno-error=implicit-int -Wno-error=int-conversion -Wno-error=incompatible-pointer-types -Wno-error=implicit-function-declaration -march=btver2 -mtune=btver2 -m64 -mabi=sysv -mcmodel=small -fpie -fPIC $(XARCH)

.PHONY: $(SDKLIB)
$(SDKLIB):
	@rm -rf $(SDK_COPY)
	@mkdir -p $(SDK_COPY)
	@cp -r $(LIBPS4)/. $(SDK_COPY)/
	@sed 's/^typedef uint16_t wchar_t;/typedef int wchar_t;/' \
		$(LIBPS4)/include/types.h > $(SDK_COPY)/include/types.h
	@cp -f patches/syscall.h $(SDK_COPY)/include/syscall.h
	@cp -f patches/syscall.s $(SDK_COPY)/source/syscall.s
	@$(MAKE) -C $(SDK_COPY) CC="$(CC)" AR="$(AR)" CFLAGS="$(SDK_CFLAGS)"
	@cp -f $(SDK_COPY)/libPS4.a $@

$(TARGET): $(SDKLIB) $(ODIR) $(OBJS)
	@echo "Linking $(TARGET)..."
	@$(CC) $(LIBPS4)/crt0.s $(ODIR)/*.o -o temp.t $(CFLAGS) $(LFLAGS) $(LIBS)
	@$(OBJCOPY) -O binary temp.t $(TARGET)
	@$(RM) -f temp.t
	@echo "Build complete: $(TARGET)"

# Compile source files with dependency generation
$(ODIR)/%.o: $(SDIR)/%.c | $(ODIR)
	@echo "Compiling $<..."
	@$(CC) -MMD -MP -c -o $@ $< $(CFLAGS)

$(ODIR)/%.o: $(SDIR)/%.s | $(ODIR)
	@echo "Assembling $<..."
	@$(CC) -MMD -MP -c -o $@ $< $(CFLAGS)

# Create build directory
$(ODIR):
	@mkdir -p $@

# Utility targets
.PHONY: clean info help

clean:
	@echo "Cleaning build artifacts..."
	@$(RM) -rf $(TARGET) $(MAPFILE) $(ODIR) temp.t

info:
	@echo "Build Configuration:"
	@echo "  Target: $(TARGET)"
	@echo "  CC: $(CC)"
	@echo "  CFLAGS: $(CFLAGS)"
	@echo "  Source files: $(words $(CFILES)) C files, $(words $(SFILES)) assembly files"
	@echo "  Object files: $(words $(OBJS)) files"

help:
	@echo "Available targets:"
	@echo "  all     - Build the project (default)"
	@echo "  clean   - Remove build artifacts"
	@echo "  info    - Show build configuration"
	@echo "  help    - Show this help message"

.INTERMEDIATE: temp.t
