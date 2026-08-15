from __future__ import annotations

from io import BytesIO
from typing import IO


class TermBuf:
    def __init__(self, rows: int = 24, cols: int = 80) -> None:
        self.rows0 = max(1, rows)
        self.cols = max(1, cols)
        self.grid: list[bytearray] = []
        self.r = 0
        self.c = 0
        self.state = "norm"
        self.csi = ""
        self._reset_grid()

    def _reset_grid(self) -> None:
        self.grid = [bytearray(b" " * self.cols) for _ in range(self.rows0)]
        self.r = 0
        self.c = 0

    def _ensure_row(self, row: int) -> None:
        while len(self.grid) <= row:
            self.grid.append(bytearray(b" " * self.cols))

    def _put(self, ch: str) -> None:
        self._ensure_row(self.r)
        if self.c >= self.cols:
            self.r += 1
            self.c = 0
            self._ensure_row(self.r)
        if self.c < self.cols:
            self.grid[self.r][self.c] = ord(ch) & 0xFF
            self.c += 1

    def _cup(self, row: int, col: int) -> None:
        self.r = max(0, row - 1)
        self.c = min(self.cols - 1, max(0, col - 1))
        self._ensure_row(self.r)

    def _csi(self, body: str, final: str) -> None:
        if body.startswith("?"):
            modes = body[1:].split(";")
            if final in "hl" and "1049" in modes:
                self._reset_grid()
            return
        parts = body.split(";") if body else []
        nums: list[int] = []
        for part in parts:
            if part == "":
                nums.append(0)
            else:
                try:
                    nums.append(int(part))
                except ValueError:
                    return
        n1 = nums[0] if nums else 0
        n2 = nums[1] if len(nums) > 1 else 0
        if final in "Hf":
            self._cup(n1 or 1, n2 or 1)
        elif final == "A":
            self.r = max(0, self.r - (n1 or 1))
        elif final == "B":
            self.r += n1 or 1
            self._ensure_row(self.r)
        elif final == "C":
            self.c = min(self.cols - 1, self.c + (n1 or 1))
        elif final == "D":
            self.c = max(0, self.c - (n1 or 1))
        elif final == "G":
            self.c = min(self.cols - 1, max(0, (n1 or 1) - 1))
        elif final == "d":
            self.r = max(0, (n1 or 1) - 1)
            self._ensure_row(self.r)
        elif final == "J":
            self._reset_grid()
        elif final == "K":
            self._ensure_row(self.r)
            start = self.c if n1 != 1 else 0
            end = self.cols if n1 != 1 else self.c
            if n1 == 2:
                start, end = 0, self.cols
            self.grid[self.r][start:end] = b" " * (end - start)
        elif final in "mnrhl":
            return

    def feed(self, data: bytes) -> None:
        text = data.decode("latin-1")
        i = 0
        while i < len(text):
            ch = text[i]
            if self.state == "norm":
                if ch == "\x1b":
                    self.state = "esc"
                elif ch == "\r":
                    self.c = 0
                elif ch == "\n":
                    self.r += 1
                    self.c = 0
                    self._ensure_row(self.r)
                elif ch == "\b":
                    self.c = max(0, self.c - 1)
                elif ch == "\t":
                    self.c = min(self.cols - 1, (self.c // 8 + 1) * 8)
                elif ord(ch) >= 32:
                    self._put(ch)
            elif self.state == "esc":
                if ch == "[":
                    self.state = "csi"
                    self.csi = ""
                elif ch == "]":
                    self.state = "osc"
                elif ch in "()":
                    self.state = "charset"
                else:
                    self.state = "norm"
            elif self.state == "csi":
                if 0x40 <= ord(ch) <= 0x7E:
                    self._csi(self.csi, ch)
                    self.state = "norm"
                else:
                    self.csi += ch
            elif self.state == "osc":
                if ch == "\x07":
                    self.state = "norm"
                elif ch == "\\":
                    self.state = "norm"
            elif self.state == "charset":
                self.state = "norm"
            i += 1

    def render(self) -> str:
        lines = [row.decode("latin-1").rstrip() for row in self.grid]
        while lines and lines[-1] == "":
            lines.pop()
        if not lines:
            return ""
        return "\n".join(lines) + "\n"


class TermLog:
    def __init__(self, fh: IO[bytes], rows: int = 24, cols: int = 80) -> None:
        self._fh = fh
        self._term = TermBuf(rows, cols)

    def write(self, data: bytes) -> None:
        self._term.feed(data)
        self.flush()

    def flush(self) -> None:
        encoded = self._term.render().encode("utf-8")
        self._fh.seek(0)
        self._fh.write(encoded)
        self._fh.truncate()
        self._fh.flush()

    def close(self) -> None:
        self.flush()
        self._fh.close()


def render_sipp_stdout(raw: bytes, rows: int = 24, cols: int = 80) -> str:
    buf = BytesIO()
    log = TermLog(buf, rows=rows, cols=cols)
    log.write(raw)
    return buf.getvalue().decode("utf-8")
