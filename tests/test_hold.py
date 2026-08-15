from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sip_console.config import hold_ms
from sip_console.load import run_load
from sip_console.sipp_cmd import build_sipp_cmd

ROOT = Path(__file__).resolve().parents[1]


class HoldMsTests(unittest.TestCase):
    def test_scenario_defaults(self):
        self.assertEqual(hold_ms({}, "uac-basic"), 5000)
        self.assertEqual(hold_ms({}, "rtp-echo"), 10000)
        self.assertEqual(hold_ms({}, "dtmf"), 5000)

    def test_env_seconds_and_ms(self):
        self.assertEqual(hold_ms({"SIP_CALL_DURATION": "30"}, "uac-basic"), 30000)
        self.assertEqual(hold_ms({"SIP_HOLD_MS": "12000"}, "uac-basic"), 12000)

    def test_cli_overrides_env(self):
        self.assertEqual(
            hold_ms({"SIP_CALL_DURATION": "30"}, "uac-basic", duration_s=15),
            15000,
        )

    def test_sipp_dash_d_sets_pause_duration(self):
        with tempfile.TemporaryDirectory() as td:
            cmd = build_sipp_cmd(
                root=ROOT,
                scenario="uac-basic",
                target="10.0.0.5:5060",
                service="1000",
                transport="udp",
                local_ip="1.2.3.4",
                local_port="",
                media_ip="1.2.3.4",
                media_port="6000",
                csv_path=Path("/tmp/u.csv"),
                artifact_dir=Path(td),
                call_limit=1,
                hold_ms=25000,
            )
            self.assertEqual(cmd[cmd.index("-d") + 1], "25000")
            self.assertEqual(cmd[cmd.index("-recv_timeout") + 1], "25000")
            self.assertEqual(
                cmd[cmd.index("-sf") + 1],
                str(ROOT / "scenarios/uac/uac-basic.xml"),
            )
            self.assertNotIn("-set", cmd)

    def test_load_profile_duration_seconds(self):
        with tempfile.TemporaryDirectory() as td:
            profile = Path(td) / "p.yaml"
            profile.write_text(
                "scenario: uac-basic\ncps: 1\nmax_concurrent: 1\ncalls: 1\nduration: 20\n",
                encoding="utf-8",
            )
            with patch("sip_console.load.run_sipp", return_value=0) as m:
                run_load(Path(td), profile)
            self.assertEqual(m.call_args.kwargs["duration_s"], 20.0)
