SHELL := /bin/sh
CC ?= cc
CPPFLAGS ?= -Iinclude
CFLAGS ?= -std=c11 -O2 -Wall -Wextra -Werror -pedantic
JSC_CFLAGS ?= $(shell pkg-config --cflags javascriptcoregtk-4.1 2>/dev/null)
JSC_LIBS ?= $(shell pkg-config --libs javascriptcoregtk-4.1 2>/dev/null)
WEBKIT_CFLAGS ?= $(shell pkg-config --cflags webkit2gtk-4.1 2>/dev/null)
WEBKIT_LIBS ?= $(shell pkg-config --libs webkit2gtk-4.1 2>/dev/null)
JSC_DEFINE := $(if $(JSC_LIBS),-DHOMEBREW_HAVE_JSC,)
BUILD_DIR ?= build/host
TARGET := $(BUILD_DIR)/homebrew-safe-smoke
BROWSER_TARGET := $(BUILD_DIR)/minimal-browser
MODERN_TARGET := $(BUILD_DIR)/modern-webkitgtk-smoke
SOURCES := src/orbis_webkit_stub.c src/homebrew_smoke.c
BROWSER_SOURCES := src/orbis_webkit_stub.c src/oss_webkit_bridge.c src/homebrew_browser.c src/minimal_browser_main.c
MODERN_SOURCES := src/modern_webkitgtk_smoke.c

.PHONY: all host-smoke minimal-browser-smoke modern-webkit-smoke clean

all: host-smoke minimal-browser-smoke modern-webkit-smoke

$(BUILD_DIR):
	mkdir -p $@

$(TARGET): $(SOURCES) include/orbis_webkit_stub.h | $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) $(SOURCES) -o $@

host-smoke: $(TARGET)
	$(TARGET) > $(BUILD_DIR)/smoke-output.txt
	grep -q 'profile=host-safe' $(BUILD_DIR)/smoke-output.txt
	grep -q '\"sony_modules\":false' $(BUILD_DIR)/smoke-output.txt

$(BROWSER_TARGET): $(BROWSER_SOURCES) include/homebrew_browser.h include/orbis_webkit_stub.h include/oss_webkit_bridge.h | $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) $(JSC_DEFINE) $(JSC_CFLAGS) -pthread $(BROWSER_SOURCES) $(JSC_LIBS) -o $@

minimal-browser-smoke: $(BROWSER_TARGET)
	$(BROWSER_TARGET) > $(BUILD_DIR)/minimal-browser-output.txt
	grep -q 'homebrew-minimal-browser' $(BUILD_DIR)/minimal-browser-output.txt
	grep -q 'webkit=unavailable' $(BUILD_DIR)/minimal-browser-output.txt
	grep -q 'jsc-host-available' $(BUILD_DIR)/minimal-browser-output.txt
	grep -q '"engine":"JavaScriptCore-GTK-host","passed":true' $(BUILD_DIR)/minimal-browser-output.txt

$(MODERN_TARGET): $(MODERN_SOURCES) fixtures/page1.html fixtures/page2.html | $(BUILD_DIR)
	@test -n "$(WEBKIT_LIBS)" || (echo 'webkit2gtk-4.1 development package is required' >&2; exit 1)
	$(CC) $(CPPFLAGS) $(CFLAGS) $(WEBKIT_CFLAGS) $(MODERN_SOURCES) $(WEBKIT_LIBS) -o $@

modern-webkit-smoke: $(MODERN_TARGET)
	rm -rf /tmp/webkit-kit-modern-smoke
	mkdir -p /tmp/webkit-kit-modern-smoke
	cp fixtures/page1.html fixtures/page2.html /tmp/webkit-kit-modern-smoke/
	xvfb-run -a -s '-screen 0 1280x800x24' $(MODERN_TARGET) > $(BUILD_DIR)/modern-webkitgtk-output.txt
	grep -q 'stage=1 result=yes|yes|clicked|120px|40px' $(BUILD_DIR)/modern-webkitgtk-output.txt
	grep -q 'stage=2 result={"url":true,"dom":"navigation-ok","js":true}' $(BUILD_DIR)/modern-webkitgtk-output.txt

clean:
	rm -rf build

# No PS4 target is provided until a legal OpenOrbis installation and sysroot
# are supplied externally. This Makefile never references proprietary modules.
