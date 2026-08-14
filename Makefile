.PHONY: check validate basic load ramp regression list clean

check:
	./scripts/check.sh

validate:
	./scripts/validate.sh

basic:
	./scripts/run.sh uac-basic

uas:
	./scripts/run.sh uas-answer

dtmf:
	./scripts/run.sh dtmf

rtp:
	./scripts/run.sh rtp-echo

load:
	./scripts/load.sh profiles/load-10cps.yaml

ramp:
	./scripts/load.sh profiles/ramp.yaml

regression:
	./scripts/regression.sh profiles/regression.yaml

list:
	./tools/scenario-list.sh

clean:
	rm -rf artifacts
