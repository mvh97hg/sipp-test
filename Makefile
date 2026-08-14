.PHONY: check validate basic load ramp regression list clean

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

rtp:
	python3 -m sip_console run rtp-echo

load:
	python3 -m sip_console load profiles/load-10cps.yaml

ramp:
	python3 -m sip_console load profiles/ramp.yaml

regression:
	python3 -m sip_console regression profiles/regression.yaml

list:
	python3 -m sip_console list

clean:
	rm -rf logs artifacts
	rm -f -- *.csv *.log uac-*_*.csv uac-*_*.log 2>/dev/null || true
