.PHONY: check validate basic uas dtmf dtmf-rtp rtp options register cancel hold prack refer load load100 ramp regression list clean run

# make run load-50cps   or   make run PROFILE=load-50cps
ifeq ($(firstword $(MAKECMDGOALS)),run)
  RUN_EXTRA := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  ifneq ($(RUN_EXTRA),)
    PROFILE ?= $(firstword $(RUN_EXTRA))
    .PHONY: $(RUN_EXTRA)
    $(RUN_EXTRA):
	@:
  endif
endif

check:
	python3 -m sip_console check

validate:
	python3 -m sip_console validate

basic:
	python3 -m sip_console run uac-basic

uas:
	python3 -m sip_console run uas-answer --listen 5060

dtmf:
	python3 -m sip_console run dtmf

dtmf-rtp:
	python3 -m sip_console run dtmf-rfc4733

rtp:
	python3 -m sip_console run rtp-echo

options:
	python3 -m sip_console run uac-options

register:
	python3 -m sip_console run uac-register

cancel:
	python3 -m sip_console run uac-cancel

hold:
	python3 -m sip_console run uac-hold

prack:
	python3 -m sip_console run uac-prack

refer:
	python3 -m sip_console run uac-refer

# load:
# 	python3 -m sip_console load profiles/load-10cps.yaml

# load100:
# 	python3 -m sip_console load profiles/load-100cps.yaml

# ramp:
# 	python3 -m sip_console load profiles/ramp.yaml

run:
	@name="$(PROFILE)"; \
	if [ -z "$$name" ]; then \
		echo "usage: make run <profile>   e.g. make run load-50cps"; \
		echo "   or: make run PROFILE=load-50cps"; \
		exit 2; \
	fi; \
	if [ -f "$$name" ]; then f="$$name"; \
	elif [ -f "profiles/$$name.yaml" ]; then f="profiles/$$name.yaml"; \
	elif [ -f "profiles/$$name" ]; then f="profiles/$$name"; \
	else echo "ERROR: profile not found: $$name (tried profiles/$$name.yaml)"; exit 2; fi; \
	echo "Load profile: $$f"; \
	python3 -m sip_console load "$$f"

regression:
	python3 -m sip_console regression profiles/regression.yaml

list:
	python3 -m sip_console list

clean:
	rm -rf logs artifacts
	rm -f -- *.csv *.log uac-*_*.csv uac-*_*.log 2>/dev/null || true
