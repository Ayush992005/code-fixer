import json
from repair import repair

stats = {}
for line in open("data/valid.jsonl", encoding="utf-8"):
    user = json.loads(line)["messages"][0]["content"]
    lang = user.split()[2]
    code = user.split("```" + lang + "\n", 1)[1].split("\n```\n\nError:", 1)[0]
    r = repair(code, lang)
    s = stats.setdefault(lang, [0, 0])
    s[0] += r["success"]
    s[1] += 1

for lang, (g, t) in stats.items():
    print(f"{lang}: {g}/{t} fixed = {100*g/t:.1f}%")
