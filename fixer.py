import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
tok = AutoTokenizer.from_pretrained("code-fixer-model")
model = AutoModelForCausalLM.from_pretrained(
    "code-fixer-model",
    torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32).to(DEVICE)


def extract_code(out):
    if "```" in out:
        body = out.split("```")[1]
        body = body.split("\n", 1)[1] if "\n" in body else body
        return body.rstrip("`").rstrip() + "\n"
    return out


def ask_llm(code, lang, err, sample=False):
    p = f"Fix this {lang} code.\n\nCode:\n```{lang}\n{code}\n```\n\nError:\n{err}"
    text = tok.apply_chat_template([{"role": "user", "content": p}],
                                   add_generation_prompt=True, tokenize=False)
    ids = tok(text, return_tensors="pt").to(DEVICE)
    kwargs = dict(max_new_tokens=1024, do_sample=sample)
    if sample:
        kwargs.update(temperature=0.7, top_p=0.9)
    with torch.no_grad():
        out = model.generate(**ids, **kwargs)
    return extract_code(tok.decode(out[0][ids["input_ids"].shape[1]:], skip_special_tokens=True))
