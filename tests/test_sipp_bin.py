from pathlib import Path
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sip_console.sipp_bin import SIPP_URL, ensure_sipp, find_sipp


class FakeResp:
    def __init__(self, data: bytes) -> None:
        self._data = data

    def read(self, *_args):
        return self._data

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False


class SippBinTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {}, clear=False)
        self.env.start()
        os.environ.pop("SIP_SIPP", None)
        self.which = patch("sip_console.sipp_bin.shutil.which", return_value=None)
        self.which.start()

    def tearDown(self):
        self.which.stop()
        self.env.stop()

    def test_finds_binary_in_repo_root(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            path = root / "sipp"
            path.write_bytes(b"x")
            path.chmod(0o755)
            self.assertEqual(find_sipp(root), path)

    def test_prefers_repo_binary_over_path(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            local = root / "sipp"
            path_bin = root / "path-sipp"
            local.write_bytes(b"local")
            path_bin.write_bytes(b"path")
            local.chmod(0o755)
            path_bin.chmod(0o755)
            with patch("sip_console.sipp_bin.shutil.which", return_value=str(path_bin)):
                self.assertEqual(find_sipp(root), local)

    def test_finds_binary_in_home(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "repo"
            home = Path(td) / "home"
            root.mkdir()
            home.mkdir()
            path = home / "sipp"
            path.write_bytes(b"x")
            path.chmod(0o755)
            with patch("sip_console.sipp_bin.Path.home", return_value=home):
                self.assertEqual(find_sipp(root), path)

    def test_download_to_repo_when_missing(self):
        payload = b"\x7fELF" + b"a" * 100_000
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with patch(
                "sip_console.sipp_bin.urllib.request.urlopen",
                return_value=FakeResp(payload),
            ) as opener:
                path = ensure_sipp(root)
            opener.assert_called()
            self.assertEqual(opener.call_args.args[0], SIPP_URL)
            self.assertEqual(path, root / "sipp")
            self.assertTrue(os.access(path, os.X_OK))
            self.assertEqual(path.read_bytes()[:4], b"\x7fELF")

    def test_download_falls_back_to_home(self):
        payload = b"\x7fELF" + b"a" * 100_000
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "repo"
            home = Path(td) / "home"
            root.mkdir()
            home.mkdir()
            with patch("sip_console.sipp_bin.Path.home", return_value=home), patch(
                "sip_console.sipp_bin._can_install",
                side_effect=lambda dest: dest == home / "sipp",
            ), patch(
                "sip_console.sipp_bin.urllib.request.urlopen",
                return_value=FakeResp(payload),
            ):
                path = ensure_sipp(root)
            self.assertEqual(path, home / "sipp")
            self.assertTrue(path.is_file())

    def test_rejects_tiny_or_non_elf_download(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "repo"
            home = Path(td) / "home"
            root.mkdir()
            home.mkdir()
            with patch("sip_console.sipp_bin.Path.home", return_value=home), patch(
                "sip_console.sipp_bin.urllib.request.urlopen",
                return_value=FakeResp(b"<html>not sipp</html>"),
            ):
                with self.assertRaises(RuntimeError):
                    ensure_sipp(root)
            self.assertFalse((root / "sipp").exists())
            self.assertFalse((home / "sipp").exists())
