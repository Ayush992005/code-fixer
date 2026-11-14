import torch
from datasets import load_dataset
from peft import LoraConfig
from transformers import AutoModelForCausalLM
from trl import SFTTrainer, SFTConfig

# 12 GB VRAM: 1.5B model.  6 GB VRAM: change to Qwen/Qwen2.5-Coder-0.5B-Instruct
MODEL = "Qwen/Qwen2.5-Coder-1.5B-Instruct"

bf16 = torch.cuda.is_available() and torch.cuda.is_bf16_supported()
model = AutoModelForCausalLM.from_pretrained(
    MODEL, torch_dtype=torch.bfloat16 if bf16 else torch.float32)

ds = load_dataset("json", data_files={"train": "data/train.jsonl",
                                      "validation": "data/valid.jsonl"})

cfg = SFTConfig(
    output_dir="adapters",
    num_train_epochs=2,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=16,
    learning_rate=2e-4,
    logging_steps=10,
    eval_strategy="steps", eval_steps=100,
    save_strategy="steps", save_steps=200, save_total_limit=2,
    bf16=bf16, fp16=not bf16,
    gradient_checkpointing=True,
    max_length=2048,          # if TRL complains, rename to max_seq_length; if out of memory use 1024
    report_to="none",
)

trainer = SFTTrainer(
    model=model, args=cfg,
    train_dataset=ds["train"], eval_dataset=ds["validation"],
    peft_config=LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05,
                           target_modules="all-linear", task_type="CAUSAL_LM"),
)
trainer.train()
trainer.save_model("adapters")
print("DONE")
