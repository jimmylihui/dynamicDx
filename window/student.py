"""Qwen3.5-4B student with one LoRA adapter for both tasks (Appendix I, "Student").

Pass 1 predicts at most one window from the timestamped 32-frame survey; pass 2 continues the same
conversation and generates one phenomenology sentence. A valid window adds an image-instruction turn
with K frames from the window; otherwise pass 2 is a text-only turn over the survey already shown.
Both are plain text generation; only target-text tokens carry loss.
"""
import json
import os
import sys

import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as W                                                    # noqa: E402

BASE = os.environ.get("BASE_MODEL", "Qwen/Qwen3.5-4B")
END = "<|im_end|>\n"
# LoRA on the language side only; the vision tower is frozen and excluded
LORA_TARGETS = r"^(?!.*visual).*\.(q_proj|k_proj|v_proj|o_proj|gate_proj|up_proj|down_proj|in_proj_qkv|out_proj)$"


def load(adapter=None, train=False):
    from transformers import AutoModelForImageTextToText, AutoProcessor
    proc = AutoProcessor.from_pretrained(BASE)
    model = AutoModelForImageTextToText.from_pretrained(BASE, torch_dtype=torch.bfloat16,
                                                        device_map="cuda")
    if train:
        from peft import LoraConfig, get_peft_model
        for p in model.parameters():
            p.requires_grad_(False)
        model.gradient_checkpointing_enable()
        model.enable_input_require_grads()
        model = get_peft_model(model, LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05, bias="none",
                                                 target_modules=LORA_TARGETS))
        n_tr = sum(p.numel() for p in model.parameters() if p.requires_grad)
        n_all = sum(p.numel() for p in model.parameters())
        print("trainable %.1fM of %.2fB (%.2f%%)" % (n_tr / 1e6, n_all / 1e9, 100.0 * n_tr / n_all))
    elif adapter:
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, adapter)
    model.eval()
    return proc, model


def user(images, text):
    return {"role": "user", "content": [{"type": "image"} for _ in images] + [{"type": "text", "text": text}]}


def assistant(text):
    return {"role": "assistant", "content": [{"type": "text", "text": text}]}


def render(proc, messages):
    # the chat template is rendered with the reasoning block closed
    return proc.apply_chat_template(messages, tokenize=False, add_generation_prompt=True,
                                    enable_thinking=False)


def encode(proc, messages, images, target, device="cuda"):
    """inputs with labels on the target tokens only (prompt, image and template positions masked)"""
    prompt = render(proc, messages)
    kw = dict(images=images) if images else {}
    enc = proc(text=[prompt + target + END], return_tensors="pt", **kw)
    n_prompt = proc(text=[prompt], return_tensors="pt", **kw)["input_ids"].shape[1]
    labels = enc["input_ids"].clone()
    labels[:, :n_prompt] = -100
    enc["labels"] = labels
    return {k: v.to(device) for k, v in enc.items()}


@torch.no_grad()
def generate(proc, model, messages, images, max_new_tokens, device="cuda"):
    kw = dict(images=images) if images else {}
    enc = proc(text=[render(proc, messages)], return_tensors="pt", **kw).to(device)
    out = model.generate(**enc, do_sample=False, max_new_tokens=max_new_tokens)
    return proc.batch_decode(out[:, enc["input_ids"].shape[1]:], skip_special_tokens=True)[0].strip()


def pass2_turn(video, w, k, survey_imgs):
    """(messages to append, images to append) for the recognition turn"""
    if w and w[0] == "request":
        fr = W.window_frames(video, w[1], w[2], k)
        return user(fr, W.RECOGNITION_INSTRUCTION.format(N=len(fr))), fr
    return user([], W.RECOGNITION_INSTRUCTION.format(N=len(survey_imgs))), []


def window_text(w):
    return W.target_text(w) if w else json.dumps({"mode": "invalid"})
