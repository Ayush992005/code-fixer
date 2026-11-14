import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

BASE = "Qwen/Qwen2.5-Coder-1.5B-Instruct"   # must match MODEL in train.py
model = AutoModelForCausalLM.from_pretrained(BASE, torch_dtype=torch.float32)
model = PeftModel.from_pretrained(model, "adapters").merge_and_unload()
model.save_pretrained("code-fixer-model")
AutoTokenizer.from_pretrained(BASE).save_pretrained("code-fixer-model")
print("saved")
