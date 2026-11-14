import pathlib, shutil

# Copies correct programs from the cloned repos into programs/<language>/
for lang, ext, repo in [("python", ".py", "Python"), ("java", ".java", "Java"),
                        ("c", ".c", "C"), ("cpp", ".cpp", "C-Plus-Plus")]:
    out = pathlib.Path("programs") / lang
    out.mkdir(parents=True, exist_ok=True)
    n = 0
    for i, p in enumerate(pathlib.Path(repo).rglob("*" + ext)):
        shutil.copy(p, out / f"{i}_{p.name}")
        n += 1
    print(lang, n, "files")
