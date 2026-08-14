from pathlib import Path
import subprocess, sys, tempfile

root=Path(__file__).resolve().parent.parent
with tempfile.TemporaryDirectory() as td:
    td=Path(td)
    inp=td/"users.csv"
    out=td/"out.csv"
    inp.write_text("SEQUENTIAL\n1000;2000;pbx.example.com\n1001;2001;tenant.example.com\n", encoding="utf-8")
    subprocess.run([
        sys.executable, str(root/"tools/prepare_csv.py"),
        "--input", str(inp), "--output", str(out),
        "--target", "210.211.122.104:5090",
    ], check=True)
    text=out.read_text()
    assert "1000;2000;pbx.example.com;" in text
    assert "1001;2001;tenant.example.com;" in text
print("prepare_csv: OK")
