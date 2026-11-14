import pathlib
from make_data import check

files = list(pathlib.Path("programs/c").rglob("*.c"))
print(len(files), "C files")
too_long = ok = 0
first_err = None
for p in files[:200]:
    t = p.read_text(encoding="utf-8", errors="ignore").replace("\r\n", "\n")
    if len(t) > 3000:
        too_long += 1
        continue
    good, err = check(t, "c")
    if good:
        ok += 1
    elif first_err is None:
        first_err = err
print("too long:", too_long, "| compile ok:", ok)
print("first error:", first_err)