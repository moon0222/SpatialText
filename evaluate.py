# coding=utf-8
import os
import argparse
import json
import logging
import re
from tqdm import tqdm

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


# ==========================================================
# Basic Configuration
# ==========================================================

DEFAULT_MODEL_PATH = "deepseek-ai/DeepSeek-R1-Distill-Llama-8B"


def setup_logging():
    fmt = '%(asctime)s,%(msecs)03d - %(name)s - %(levelname)s - %(message)s'
    datefmt = '%Y-%m-%d %H:%M:%S'
    logging.basicConfig(level=logging.INFO, format=fmt, datefmt=datefmt)


setup_logging()
logger = logging.getLogger("DeepSeek-Benchmark")


# ==========================================================
# Utility Functions
# ==========================================================

def _normalize_token(s: str) -> str:
    """Normalize token by stripping whitespace and quotes."""
    return s.strip().strip('"\'')


def _strip_nonword_upper(s: str) -> str:
    """Remove non-alphanumeric characters and convert to uppercase."""
    return re.sub(r'[\W_]+', '', s).upper()


def _parse_candidates(opts):
    """
    Parse candidate options into structured format.
    Extract option label (A/B/C) and text.
    """
    parsed = []
    for cand in opts or []:
        cand_str = str(cand)
        m = re.match(r'\s*([A-Za-z])\s*[\.．、:：]?\s*(.*)', cand_str)
        label = m.group(1).upper() if m else None
        text_part = m.group(2).strip() if m else cand_str.strip()
        parsed.append({
            "label": label,
            "text": text_part,
            "raw": cand_str
        })
    return parsed


def _match_token_to_candidate(token: str, parsed):
    """
    Match a predicted token to candidate options.
    """
    tok_norm = _normalize_token(token)
    tok_flat = _strip_nonword_upper(tok_norm)

    for p in parsed:
        for key in (p["label"], p["text"], p["raw"]):
            if not key:
                continue

            key_norm = _normalize_token(key)
            key_flat = _strip_nonword_upper(key_norm)

            if (
                tok_flat == key_flat or
                tok_flat.startswith(key_flat) or
                key_flat.startswith(tok_flat)
            ):
                return p["label"] or p["text"] or p["raw"]

    return None


# ==========================================================
# Model Loading
# ==========================================================

def load_model_and_tokenizer(model_path: str, device: str = "auto"):
    """
    Load model and tokenizer.
    """
    logger.info(f"Loading model: {model_path}")

    tokenizer = AutoTokenizer.from_pretrained(
        model_path,
        trust_remote_code=True
    )

    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        trust_remote_code=True,
        torch_dtype=torch.bfloat16 if torch.cuda.is_available() else "auto",
        device_map=device
    )

    model.eval()

    logger.info(f"Model loaded successfully. Current device: {model.device}")

    return tokenizer, model


# ==========================================================
# Prompt Templates
# ==========================================================

SYSTEM_PROMPT = (
    "You are an intelligent assistant specialized in spatial reasoning."
)

ROOM_PROMPT_TEMPLATE = """
Please carefully read the following spatial scene description.

Select exactly one correct answer from the candidate options.
Only output the option letter (e.g., A, B, or C).

Scene Description:
{scene}

Question:
{question}

Candidate Answers:
{candidates}

Strict Format Requirement:
Output exactly one line in the format:
Answer: <OptionLetter>
"""

BLOCK_PROMPT_TEMPLATE = """
Please carefully read the following spatial scene description.

The scene consists of independent rectangular or cuboid regions.
All regions are axis-aligned and non-overlapping.
Ignore object size and treat objects as points.

Scene Description:
{scene}

Question:
{question}

Candidate Answers:
{candidates}

Strict Format Requirement:
Output the final answer on the last line in the format:
Answer: <OptionLetter>
or
Answer: A,B
"""


# ==========================================================
# Benchmark Execution
# ==========================================================

def run_benchmark(model_path,
                  dataset_path,
                  output_path,
                  dataset_type="room",
                  device="auto",
                  max_new_tokens=8192):

    tokenizer, model = load_model_and_tokenizer(model_path, device)

    with open(dataset_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    results = []
    total = 0
    correct = 0

    for item in tqdm(data, desc="Processing scenes"):

        # Dataset field mapping
        if dataset_type == "room":
            scene_desc = item.get("scene_description", "")
            questions = item.get("questions", [])
        else:
            scene_desc = item.get("description", "")
            questions = item.get("questions", [])

        for q in questions:

            if dataset_type == "room":
                question = q.get("question", "")
                candidates = q.get("options", [])
                gold = q.get("answer", None)
            else:
                question = q.get("question", "")
                candidates = q.get("candidate_answers", [])
                gold = q.get("answer", None)

            candidates_str = "; ".join(candidates)

            template = (
                ROOM_PROMPT_TEMPLATE
                if dataset_type == "room"
                else BLOCK_PROMPT_TEMPLATE
            )

            prompt = template.format(
                scene=scene_desc,
                question=question,
                candidates=candidates_str
            )

            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ]

            input_ids = tokenizer.apply_chat_template(
                messages,
                add_generation_prompt=True,
                return_tensors="pt"
            ).to(model.device)

            with torch.no_grad():
                output_ids = model.generate(
                    input_ids,
                    max_new_tokens=max_new_tokens,
                    do_sample=False
                )

            output_text = tokenizer.decode(
                output_ids[0][input_ids.shape[-1]:],
                skip_special_tokens=True
            )

            # Extract predicted answer
            predicted = output_text.strip().split("Answer:")[-1].strip()
            predicted = predicted.replace(" ", "")

            total += 1
            is_correct = str(gold).replace(" ", "") == predicted

            if is_correct:
                correct += 1

            results.append({
                "question": question,
                "gold_answer": gold,
                "predicted_answer": predicted,
                "correct": is_correct
            })

    accuracy = correct / total if total > 0 else 0

    with open(output_path, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"Total questions: {total}")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Results saved to: {output_path}")


# ==========================================================
# CLI
# ==========================================================

def main():
    parser = argparse.ArgumentParser(
        description="DeepSeek Spatial Reasoning Benchmark"
    )

    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL_PATH,
        help="Model path or HuggingFace model name"
    )

    parser.add_argument(
        "--dataset",
        required=True,
        help="Path to JSON dataset file"
    )

    parser.add_argument(
        "--dataset-type",
        choices=["room", "block"],
        required=True,
        help="Dataset format type"
    )

    parser.add_argument(
        "--output",
        default="results.jsonl",
        help="Output file path"
    )

    parser.add_argument(
        "--device",
        default="auto",
        help="Device mapping (e.g., auto, cuda, npu)"
    )

    parser.add_argument(
        "--max-new-tokens",
        type=int,
        default=8192,
        help="Maximum generation length"
    )

    args = parser.parse_args()

    run_benchmark(
        args.model,
        args.dataset,
        args.output,
        args.dataset_type,
        args.device,
        args.max_new_tokens
    )


if __name__ == "__main__":
    main()