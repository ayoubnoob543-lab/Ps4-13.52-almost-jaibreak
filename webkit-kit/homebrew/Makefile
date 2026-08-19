SHELL := /bin/sh
CC ?= cc
CPPFLAGS ?= -Iinclude
CFLAGS ?= -std=c11 -O2 -Wall -Wextra -Werror -pedantic
BUILD_DIR ?= build/host
TARGET := $(BUILD_DIR)/homebrew-safe-smoke
SOURCES := src/orbis_webkit_stub.c src/homebrew_smoke.c

.PHONY: all host-smoke clean

all: host-smoke

$(BUILD_DIR):
	mkdir -p $@

$(TARGET): $(SOURCES) include/orbis_webkit_stub.h | $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) $(SOURCES) -o $@

host-smoke: $(TARGET)
	$(TARGET) > $(BUILD_DIR)/smoke-output.txt
	grep -q 'profile=host-safe' $(BUILD_DIR)/smoke-output.txt
	grep -q '"sony_modules":false' $(BUILD_DIR)/smoke-output.txt

clean:
	rm -rf build

# No PS4 target is provided until a legal OpenOrbis installation and sysroot
# are supplied externally. This Makefile never references proprietary modules.
