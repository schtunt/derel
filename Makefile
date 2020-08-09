export PATH += :${HOME}/Library/Python/3.8/bin/

PACKAGES := atari-py gym numpy opencv-python
PACKAGES += torch torchvision pytorch-ignite
PACKAGES += tensorboard tensorboardX tensorflow ptan
PACKAGES += ffmpeg ipython pyreadline matplotlib

OS := $(shell uname -o)
VENV := .venv

all: setup .venv
.PHONY: all

plot: runs
	@echo "Visit http://127.0.0.1:6006/ and place Ctrl-C to quit"
	tensorboard --logdir runs

runs:
	$(MAKE) plot

repl: ${VENV}
	source ${VENV}/bin/activate && ipython3
.PHONY: repl

.pip: ${VENV}
	source ${VENV}/bin/activate && pip3 install --upgrade pip
	source ${VENV}/bin/activate && pip3 install cmake wheel
	source ${VENV}/bin/activate && pip3 install --use-feature=2020-resolver $(PACKAGES)
	touch $@

${VENV}:
	python3 -m venv $@

setup: .setup .pip
.PHONY: setup

.setup.Darwin:
	xcode-select --print-path || xcode-select --install
	touch $@

.setup: .setup.$(OS)
	python3 -m pip install --user --upgrade pip setuptools wheel
	touch $@

purge:
	rm -rf .setup .setup.Darwin
	rm -rf ${VENV}
.PHONY: purge

@%: ${VENV}
	source ${VENV}/bin/activate && python3 ${@:@%=%.py}
