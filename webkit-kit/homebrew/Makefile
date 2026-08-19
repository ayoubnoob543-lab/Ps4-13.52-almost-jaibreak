SHELL := /bin/sh
CC ?= cc
CPPFLAGS ?= -Iinclude
CFLAGS ?= -std=c11 -O2 -Wall -Wextra -Werror -pedantic
BUILD_DIR ?= build/host
TARGET := $(BUILD_DIR)/homebrew-safe-smoke
BROWSER_TARGET := $(BUILD_DIR)/minimal-browser
SOURCES := src/orbis_webkit_stub.c src/homebrew_smoke.c
BROWSER_SOURCES := src/orbis_webkit_stub.c src/oss_webkit_bridge.c src/homebrew_browser.c src/minimal_browser_main.c

.PHONY: all host-smoke clean

all: host-smoke minimal-browser-smoke

$(BUILD_DIR):
	mkdir -p $@

$(TARGET): $(SOURCES) include/orbis_webkit_stub.h | $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) $(SOURCES) -o $@

host-smoke: $(TARGET)
	$(TARGET) > $(BUILD_DIR)/smoke-output.txt
	grep -q 'profile=host-safe' $(BUILD_DIR)/smoke-output.txt
	grep -q '\"sony_modules\":false' $(BUILD_DIR)/smoke-output.txt

$(BROWSER_TARGET): $(BROWSER_SOURCES) include/homebrew_browser.h include/orbis_webkit_stub.h include/oss_webkit_bridge.h | $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -pthread $(BROWSER_SOURCES) -o $@

minimal-browser-smoke: $(BROWSER_TARGET)
	$(BROWSER_TARGET) > $(BUILD_DIR)/minimal-browser-output.txt
	grep -q 'homebrew-minimal-browser' $(BUILD_DIR)/minimal-browser-output.txt
	grep -q 'webkit=unavailable' $(BUILD_DIR)/minimal-browser-output.txt
	grep -q 'oss-source-not-configured' $(BUILD_DIR)/minimal-browser-output.txt

clean:
	rm -rf build

# No PS4 target is provided until a legal OpenOrbis installation and sysroot
# are supplied externally. This Makefile never references proprietary modules.
