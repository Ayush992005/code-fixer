"""Runs a program and returns what it printed (used by the /run API endpoint).

Each run happens in a fresh temporary folder, with a time limit and an output limit.
WARNING: this executes whatever code it is given on THIS computer. Use it for local
development and demos only. For a public website, run it inside a sandbox (Docker).
"""
import os
import re
import subprocess
import sys
import tempfile
import time

COMPILE_TIMEOUT = 30     # seconds
RUN_TIMEOUT = 10         # seconds
MAX_CHARS = 20000        # longest output returned
EXE = ".exe" if os.name == "nt" else ""


def _clip(data):
    text = (data or b"").decode("utf-8", errors="replace")
    return text if len(text) <= MAX_CHARS else text[:MAX_CHARS] + "\n... output cut ..."


def _exec(cmd, cwd, stdin_text, timeout):
    """Returns (exit_code, stdout, stderr, timed_out)."""
    try:
        r = subprocess.run(cmd, cwd=cwd, input=(stdin_text or "").encode("utf-8"),
                           capture_output=True, timeout=timeout)
        return r.returncode, _clip(r.stdout), _clip(r.stderr), False
    except subprocess.TimeoutExpired as e:
        return -1, _clip(e.stdout), _clip(e.stderr), True
    except FileNotFoundError as e:
        return -1, "", f"Tool not found: {e.filename}. Is it installed and on PATH?", False


def run_code(code, lang, stdin_text=""):
    start = time.time()
    with tempfile.TemporaryDirectory() as d:
        if lang == "python":
            open(os.path.join(d, "main.py"), "w", encoding="utf-8").write(code)
            compile_cmd = None
            run_cmd = [sys.executable, "-u", "main.py"]
        elif lang == "java":
            m = re.search(r"public\s+(?:final\s+|abstract\s+)*class\s+(\w+)", code)
            name = m.group(1) if m else "Main"
            open(os.path.join(d, name + ".java"), "w", encoding="utf-8").write(code)
            compile_cmd = ["javac", "-encoding", "UTF-8", name + ".java"]
            run_cmd = ["java", name]
        elif lang in ("c", "cpp"):
            src = "main.c" if lang == "c" else "main.cpp"
            open(os.path.join(d, src), "w", encoding="utf-8").write(code)
            compile_cmd = ["gcc" if lang == "c" else "g++", src, "-o", "prog" + EXE]
            run_cmd = [os.path.join(d, "prog" + EXE)]
        else:
            return {"ok": False, "phase": "compile", "stdout": "",
                    "stderr": f"Unsupported language: {lang}", "exit_code": -1,
                    "timed_out": False, "time_ms": 0}

        if compile_cmd:
            code_rc, out, err, timed_out = _exec(compile_cmd, d, "", COMPILE_TIMEOUT)
            if timed_out or code_rc != 0:
                return {"ok": False, "phase": "compile", "stdout": out,
                        "stderr": err or "Compilation timed out.", "exit_code": code_rc,
                        "timed_out": timed_out, "time_ms": int((time.time() - start) * 1000)}

        t0 = time.time()
        rc, out, err, timed_out = _exec(run_cmd, d, stdin_text, RUN_TIMEOUT)
        return {"ok": rc == 0 and not timed_out, "phase": "run", "stdout": out,
                "stderr": err, "exit_code": rc, "timed_out": timed_out,
                "time_ms": int((time.time() - t0) * 1000)}
