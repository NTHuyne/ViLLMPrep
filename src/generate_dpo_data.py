#!/usr/bin/env python3
"""
Script to generate DPO (Direct Preference Optimization) data with resume capability.

Pipeline:
  1. Keyword extraction  → save to keywords.json
  2. Essay question generation → save to essay_questions.json
  3. DPO answer generation (accepted + rejected) → save to dpo_answers.json
  4. Compile final DPO data   → save to dpo_data.json

If any step fails, re-run the script after fixing the issue; it will resume
from the last successfully completed step (unless it's the first step,
which always reloads from the input file).

Usage:
    python src/generate_dpo_data.py --input chunks.json --output ./dpo_output
    python src/generate_dpo_data.py --input chunks.json --output ./dpo_output \\
        --num-samples 3 --model gpt-4o-mini --base-url https://api.openai.com/v1
"""

import argparse
import asyncio
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.schemas.schemas import DPOGenerationRequest
from src.configs.config import settings
from src.generate_utils import (
    load_chunks,
    load_chunks_from_dir,
    save_intermediate,
    check_step,
    step_file_path,
)
from src.core.openai_calling.client_pool import normalize_base_urls


async def run_pipeline(args: argparse.Namespace) -> None:
    """Run the DPO data generation pipeline step by step with resume support."""
    output_dir = args.output
    os.makedirs(output_dir, exist_ok=True)

    # --- Step 0: Load input (always required, never skipped) ---
    if args.input:
        print(f"[INFO] Loading chunks from: {args.input}")
        chunk_data = load_chunks(args.input)
    else:
        print(f"[INFO] Loading chunks from directory: {args.input_dir}")
        chunk_data = load_chunks_from_dir(args.input_dir)
    print(f"[INFO] Loaded {len(chunk_data)} chunk(s)")
    if not chunk_data:
        print("[ERROR] No chunks found in input.")
        sys.exit(1)

    # Determine model / base_url
    model = args.model or settings.MODEL_CONF.get("model_name")
    if args.base_url:
        base_urls = normalize_base_urls(args.base_url)
    else:
        base_urls = normalize_base_urls(settings.MODEL_CONF.get("base_url"))
    num_workers = args.num_workers
    per_url_workers = max(1, num_workers // len(base_urls))

    print(f"[INFO] Model: {model}")
    print(f"[INFO] Base URLs ({len(base_urls)}): {base_urls}")
    print(f"[INFO] Workers: {num_workers} total ({per_url_workers} per URL)")
    print(f"[INFO] Number of DPO samples: {args.num_samples}")
    print(f"[INFO] Output directory: {output_dir}")

    # ---------------------------------------------------------------
    # Step 1: Keyword extraction
    # ---------------------------------------------------------------
    existing_keywords = check_step(output_dir, "keywords", "Keyword extraction")
    if existing_keywords is not None:
        chunks_with_keywords = existing_keywords
    else:
        from src.core.keyword_extractor.keyword_extraction import synthesize_keyword

        print("\n[STEP 1/4] Extracting keywords...")
        chunks_with_keywords = await synthesize_keyword(
            chunk_data,
            llm_model=model,
            base_url=base_urls,
            num_workers=num_workers,
        )
        saved = save_intermediate(chunks_with_keywords, output_dir, "keywords")
        print(f"  -> Saved {len(chunks_with_keywords)} keyword results to {saved}")

    # ---------------------------------------------------------------
    # Step 2: Essay question generation
    # ---------------------------------------------------------------
    if args.num_samples == 0:
        essay_questions = []
        print("[SKIP] No DPO samples requested (num_samples=0).")
    else:
        existing_eq = check_step(output_dir, "essay_questions", "Essay question generation")
        if existing_eq is not None:
            essay_questions = existing_eq
        else:
            from src.core.essay_QA_generator.essay_question_generation import synthesize_question

            print(f"\n[STEP 2/4] Generating {args.num_samples} questions (train_test_ratio=1)...")
            essay_questions = await synthesize_question(
                chunks_list=chunks_with_keywords,
                total_num_questions=args.num_samples,
                train_test_ratio=1,
                llm_model=model,
                base_url=base_urls,
                num_workers=num_workers,
            )
            saved = save_intermediate(essay_questions, output_dir, "essay_questions")
            print(f"  -> Saved {len(essay_questions)} questions to {saved}")

    # ---------------------------------------------------------------
    # Step 3: DPO answer generation
    # ---------------------------------------------------------------
    final_data = []
    if essay_questions:
        existing_da = check_step(output_dir, "dpo_answers", "DPO answer generation")
        if existing_da is not None:
            dpo_answers = existing_da
        else:
            from src.core.dpo_answer_generation.dpo_answer_generation import synthesize_dpo_answer

            print(f"\n[STEP 3/4] Generating {len(essay_questions)} DPO answer pairs (accepted + rejected)...")
            dpo_answers = await synthesize_dpo_answer(
                essay_questions,
                llm_model=model,
                base_url=base_urls,
                num_workers=num_workers,
            )
            saved = save_intermediate(dpo_answers, output_dir, "dpo_answers")
            print(f"  -> Saved {len(dpo_answers)} DPO answer pairs to {saved}")

        # Convert to final dict format (ResponseDPOItem)
        for ans in dpo_answers:
            final_data.append({
                "question": ans["question"],
                "accepted_answer": ans["accepted_answer"],
                "rejected_answer": ans["rejected_answer"],
                "id": ans["question_id"],
                "domain": ans["domain"],
                "original_document": ans["chunk_id"],
            })
    else:
        print("[SKIP] No DPO answer pairs to generate.")

    # ---------------------------------------------------------------
    # Step 4: Write final DPO data
    # ---------------------------------------------------------------
    final_path = step_file_path(output_dir, "dpo_data")
    with open(final_path, "w", encoding="utf-8") as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)

    print(f"\n[SUCCESS] Generated {len(final_data)} DPO samples total")
    for item in final_data:
        print(f"  - {item['id']}: {item['question'][:60]}...")
    print(f"[SUCCESS] Final output: {final_path}")
    print(f"[SUCCESS] Intermediate files in: {output_dir}/")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate DPO (Direct Preference Optimization) data from document chunks.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python src/generate_dpo_data.py --input chunks.json --output ./dpo_output

  # Customize number of samples and model
  python src/generate_dpo_data.py --input chunks.json --output ./dpo_output \\
      --num-samples 5 --model gpt-4o-mini --base-url https://api.openai.com/v1

  # Load from a directory of JSON/JSONL files
  python src/generate_dpo_data.py --input-dir ./chunks_dir --output ./dpo_output

  # Multiple base URLs with parallel workers
  python src/generate_dpo_data.py --input chunks.json --output ./dpo_output \\
      --base-url http://host1:8000/v1,http://host2:8000/v1 --num-workers 32

  # Resume from interrupted run (just re-run the same command)
  python src/generate_dpo_data.py --input chunks.json --output ./dpo_output
        """,
    )

    parser.add_argument(
        "--input", "-i",
        type=str,
        default=None,
        help="Path to input JSON/JSONL file containing chunk data.",
    )
    parser.add_argument(
        "--input-dir",
        type=str,
        default=None,
        help="Directory containing JSON/JSONL chunk files (same format as --input).",
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        required=True,
        help="Path to output DIRECTORY (not file). Intermediate results will be stored here.",
    )
    parser.add_argument(
        "--num-samples",
        type=int,
        default=2,
        help="Number of DPO samples to generate (default: 2).",
    )
    parser.add_argument(
        "--model", "-m",
        type=str,
        default=None,
        help="LLM model name (overrides llm_config.yaml).",
    )
    parser.add_argument(
        "--base-url",
        type=str,
        nargs="+",
        default=None,
        help="LLM API base URL(s). Space- or comma-separated (overrides llm_config.yaml).",
    )
    parser.add_argument(
        "--num-workers",
        type=int,
        default=settings.LLM_CONFIG_YML["batch_size"],
        help=f"Total concurrent LLM requests, split evenly across base URLs (default: {settings.LLM_CONFIG_YML['batch_size']}).",
    )
    args = parser.parse_args()

    if bool(args.input) == bool(args.input_dir):
        parser.error("Exactly one of --input or --input-dir must be provided.")

    return args


def main() -> None:
    """Entry point."""
    args = parse_args()
    asyncio.run(run_pipeline(args))


if __name__ == "__main__":
    main()