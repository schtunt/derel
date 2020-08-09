export PATH += :${HOME}/Library/Python/3.8/bin/

PACKAGES := atari-py gym numpy opencv-python
PACKAGES += torch torchvision pytorch-ignite
PACKAGES += tensorboard tensorboardX tensorflow ptan
PACKAGES += ffmpeg ipython pyreadline matplotlib

OS := $(shell uname -s)
VENV := .venv

all: setup .venv .derelhose
.PHONY: all

.derelhose:
	git pull --recurse-submodules=on-demand

plot: runs
	@echo "Visit http://127.0.0.1:6006/ and place Ctrl-C to quit"
	tensorboard --logdir runs
.PHONY: plot
runs: @plot

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

clean:
	rm -rf runs
.PHONY: clean

purge: clean
	rm -rf .setup .setup.Darwin
	rm -rf .derelhose
	rm -rf ${VENV}
.PHONY: purge

@%: ${VENV}
	source ${VENV}/bin/activate && python3 ${@:@%=%.py}
