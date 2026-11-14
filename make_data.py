import json, random, subprocess, tempfile, pathlib, re

LANGS = {"python": ".py", "java": ".java", "c": ".c", "cpp": ".cpp"}
PER_FILE = {"python": 3, "java": 12, "c": 8, "cpp": 8}
MAX_PER_LANG = 800


def check(code, lang):
    """Return (ok, error_message) using the real compiler."""
    if lang == "python":
        try:
            compile(code, "main.py", "exec")
            return True, ""
        except SyntaxError as e:
            return False, f"{type(e).__name__}: {e.msg} (line {e.lineno})"
        except Exception as e:
            return False, f"{type(e).__name__}: {e}"
    with tempfile.TemporaryDirectory() as d:
        d = pathlib.Path(d)
        name = {"java": "Main.java", "c": "main.c", "cpp": "main.cpp"}[lang]
        (d / name).write_text(code, encoding="utf-8")
        cmd = {
            "java": ["javac", "-encoding", "UTF-8", name],
            "c":    ["gcc", "-fsyntax-only", name],
            "cpp":  ["g++", "-fsyntax-only", name],
        }[lang]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=30,
                               cwd=d, encoding="utf-8", errors="ignore")
        except subprocess.TimeoutExpired:
            return True, ""
        return r.returncode == 0, (r.stderr or r.stdout).strip()[:800]


def mutate(code, lang):
    c_like = lang in ("c", "cpp", "java")
    ops = [
        lambda c: c.replace(")", "", 1),
        lambda c: c.replace("(", "", 1),
        lambda c: re.sub(r"\b(\w{4,})\b", lambda m: m.group(1)[:-1], c, count=1),
    ]
    if lang == "python":
        ops += [
            lambda c: c.replace(":", "", 1),
            lambda c: c.replace("    ", "  ", 1),
            lambda c: c.replace("[", "", 1),
            lambda c: c.replace('"', "", 1),
        ]
    if c_like:
        ops += [
            lambda c: c.replace(";", "", 1),
            lambda c: c.replace("}", "", 1),
            lambda c: c.replace("{", "", 1),
            lambda c: c.replace("int ", "", 1),
        ]
    if lang in ("c", "cpp"):
        ops.append(lambda c: re.sub(r"#include.*\n", "", c, count=1))
    if lang == "java":
        ops.append(lambda c: re.sub(r"import .*;\n", "", c, count=1))
    return random.choice(ops)(code)


def prompt(code, lang, err):
    return f"Fix this {lang} code.\n\nCode:\n```{lang}\n{code}\n```\n\nError:\n{err}"


def clean_java(good):
    good = re.sub(r"^package .*;\n", "", good, flags=re.M)
    good = re.sub(r"^import (static )?com\.thealgorithms.*;\n", "", good, flags=re.M)
    good = re.sub(r"^import (static )?org\.junit.*;\n", "", good, flags=re.M)
    m = re.search(r"(?:public\s+)?(?:final\s+|abstract\s+)*(?:class|enum|interface)\s+(\w+)", good)
    if not m:
        return None
    return re.sub(r"\b" + m.group(1) + r"\b", "Main", good)


def build(root="programs"):
    all_rows = []
    for lang, ext in LANGS.items():
        rows = []
        files = list(pathlib.Path(root, lang).rglob("*" + ext))
        random.shuffle(files)
        for path in files:
            good = path.read_text(encoding="utf-8", errors="ignore").replace("\r\n", "\n")
            if len(good) > (5000 if lang == "java" else 3000):
                continue
            if lang == "java":
                good = clean_java(good)
                if good is None:
                    continue
            ok, _ = check(good, lang)
            if not ok:
                continue
            seen = set()
            for _ in range(PER_FILE[lang] * 2):
                if len(seen) >= PER_FILE[lang]:
                    break
                bad = mutate(good, lang)
                if bad == good or bad in seen:
                    continue
                ok, err = check(bad, lang)
                if ok:
                    continue
                seen.add(bad)
                rows.append({"messages": [
                    {"role": "user", "content": prompt(bad, lang, err)},
                    {"role": "assistant", "content": f"```{lang}\n{good}\n```"},
                ]})
            if len(rows) >= MAX_PER_LANG * 1.2:
                break
        random.shuffle(rows)
        rows = rows[:MAX_PER_LANG]
        print(lang, len(rows), "examples", flush=True)
        all_rows += rows
    random.shuffle(all_rows)
    n = int(len(all_rows) * 0.9)
    pathlib.Path("data").mkdir(exist_ok=True)
    for name, part in (("train", all_rows[:n]), ("valid", all_rows[n:])):
        with open(f"data/{name}.jsonl", "w", encoding="utf-8") as f:
            for r in part:
                f.write(json.dumps(r) + "\n")
    print("TOTAL", len(all_rows), "examples")


if __name__ == "__main__":
    build()
