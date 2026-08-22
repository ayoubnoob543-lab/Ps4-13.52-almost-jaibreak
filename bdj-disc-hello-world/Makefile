PROJECT_ROOT := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))
SDK_ROOT := $(PROJECT_ROOT)third_party/bdj-sdk
JAVA8_HOME ?= $(SDK_ROOT)/host/jdk8
JAVAC := $(JAVA8_HOME)/bin/javac
JAR := $(JAVA8_HOME)/bin/jar
STUBS := $(SDK_ROOT)/target/lib/enhanced-stubs.zip
BDSIGNER := $(SDK_ROOT)/host/bin/bdsigner
MAKEFS := $(SDK_ROOT)/host/bin/makefs
RESOURCES := $(SDK_ROOT)/resources/AVCHD
BUILD := $(PROJECT_ROOT)build
DISC_DIR := $(BUILD)/discdir
JAR_FILE := $(DISC_DIR)/BDMV/JAR/00000.jar
ISO := $(BUILD)/bdj-hello-world.iso
SOURCES := $(shell find $(PROJECT_ROOT)src -name '*.java' -type f | sort)

.PHONY: all check-tools compile image hash clean

all: image hash

check-tools:
	@test -x "$(JAVAC)" || (echo "Missing compatible JDK8: set JAVA8_HOME"; exit 2)
	@test -f "$(STUBS)" || (echo "Missing BD-J stubs: $(STUBS)"; exit 2)
	@test -x "$(BDSIGNER)" || (echo "Missing bdsigner wrapper"; exit 2)
	@test -x "$(MAKEFS)" || (echo "Missing makefs: run 'make -C $(SDK_ROOT)/host/src/makefs_termux'"; exit 2)

compile: check-tools
	@rm -rf "$(BUILD)/classes" "$(JAR_FILE)"
	@mkdir -p "$(BUILD)/classes" "$(DISC_DIR)/BDMV/JAR"
	"$(JAVAC)" -Xlint:-options -source 1.3 -target 1.3 -cp "$(STUBS)" -d "$(BUILD)/classes" $(SOURCES)
	"$(JAR)" cf "$(JAR_FILE)" -C "$(BUILD)/classes" .
	JAVA8_HOME="$(JAVA8_HOME)" "$(BDSIGNER)" -keystore "$(SDK_ROOT)/resources/sig.ks" "$(JAR_FILE)"

image: compile
	@cp -a "$(RESOURCES)/." "$(DISC_DIR)/"
	@mkdir -p "$(DISC_DIR)/BDMV/JAR"
	"$(MAKEFS)" -m 16m -t udf -o T=bdre,v=2.50,L=BDJHELLO "$(ISO)" "$(DISC_DIR)"

hash: image
	sha256sum "$(ISO)" | tee "$(BUILD)/bdj-hello-world.iso.sha256"

clean:
	rm -rf "$(BUILD)"
