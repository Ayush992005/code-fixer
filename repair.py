from fixer import ask_llm
from make_data import check


def repair(code, lang, max_attempts=6):
    """Compile -> LLM fix -> compile again, repeating with the NEW error
    until the code compiles or max_attempts is reached."""
    ok, err = check(code, lang)
    if ok:
        return {"success": True, "fixed_code": code, "attempts": 0, "history": []}

    history = []
    seen = {code.strip()}

    for attempt in range(1, max_attempts + 1):
        history.append({"attempt": attempt, "error": err})

        new = ask_llm(code, lang, err, sample=False)
        if new.strip() in seen:                      # model repeated itself -> try sampling
            new = ask_llm(code, lang, err, sample=True)
        seen.add(new.strip())

        ok, new_err = check(new, lang)
        if ok:
            return {"success": True, "fixed_code": new,
                    "attempts": attempt, "history": history}

        code, err = new, new_err

    return {"success": False, "fixed_code": code, "error": err,
            "attempts": max_attempts, "history": history}
