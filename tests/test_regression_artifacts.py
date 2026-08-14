import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sip_console.regression import run_regression


PROFILE = """
tests:
  - name: case-one
    scenario: uac-basic
    enabled: true
  - name: skipped
    scenario: uac-basic
    enabled: false
"""


def _fake_run_sipp(root, scenario, extra=None, *, artifact_dir=None, phase=None, **kwargs):
    if artifact_dir is None:
        raise AssertionError("regression must pass artifact_dir so logs live under summary")
    artifact_dir.mkdir(parents=True, exist_ok=True)
    (artifact_dir / "stdout.log").write_text("sipp-ok\n", encoding="utf-8")
    (artifact_dir / "stderr.log").write_text("", encoding="utf-8")
    (artifact_dir / "result.json").write_text("{}", encoding="utf-8")
    return 0


class RegressionArtifactLayoutTests(unittest.TestCase):
    def test_summary_artifacts_dir_contains_per_test_logs(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            profile = root / "regression.yaml"
            profile.write_text(PROFILE, encoding="utf-8")
            with patch("sip_console.regression.run_sipp", side_effect=_fake_run_sipp):
                rc = run_regression(root, profile)
            self.assertEqual(rc, 0)
            arts = list((root / "artifacts").glob("*-regression"))
            self.assertEqual(len(arts), 1)
            outroot = arts[0]
            summary = json.loads((outroot / "summary.json").read_text(encoding="utf-8"))
            self.assertEqual(Path(summary["artifacts"]), outroot)
            run_dir = outroot / "case-one"
            self.assertTrue((run_dir / "stdout.log").is_file())
            self.assertTrue((run_dir / "result.json").is_file())
            self.assertFalse((outroot / "skipped").exists())


if __name__ == "__main__":
    unittest.main()
