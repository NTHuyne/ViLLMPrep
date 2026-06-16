#!/usr/bin/env python3
"""
Script to generate SFT (Supervised Fine-Tuning) data with resume capability.

Pipeline:
  1. Keyword extraction  → save to keywords.json
  2. Essay question generation → save to essay_questions.json
  3. Essay answer generation  → save to essay_answers.json
  4. MCQA question generation → save to mcqa_questions.json
  5. MCQA answer generation   → save to mcqa_answers.json
  6. Compile final SFT data   → save to sft_data.json

If any step fails, re-run the script after fixing the issue; it will resume
from the last successfully completed step (unless it's the first step,
which always reloads from the input file).

Usage:
    python src/generate_sft_data.py --input chunks.json --output ./sft_output
    python src/generate_sft_data.py --input chunks.json --output ./sft_output \\
        --num-essay-train 20 --num-mcqa-train 5 \\
        --model gpt-4o-mini --base-url https://api.openai.com/v1
"""

import argparse
import asyncio
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.schemas.schemas import SFTGenerationRequest, ChunkItem
from src.functions.sft_generation_service import generate_sft_data
from src.configs.config import settings
from src.generate_utils import (
    load_chunks,
    save_intermediate,
    check_step,
    step_file_path,
)


async def run_pipeline(args: argparse.Namespace) -> None:
    """Run the SFT data generation pipeline step by step with resume support."""
    output_dir = args.output
    os.makedirs(output_dir, exist_ok=True)

    # --- Step 0: Load input (always required, never skipped) ---
    print(f"[INFO] Loading chunks from: {args.input}")
    chunk_data = load_chunks(args.input)
    print(f"[INFO] Loaded {len(chunk_data)} chunk(s)")
    if not chunk_data:
        print("[ERROR] No chunks found in input file.")
        sys.exit(1)

    # Determine model / base_url
    model = args.model or settings.MODEL_CONF.get("model_name")
    base_url = args.base_url or settings.MODEL_CONF.get("base_url")

    print(f"[INFO] Model: {model}")
    print(f"[INFO] Base URL: {base_url}")
    print(f"[INFO] Essay train: {args.num_essay_train}, Essay test: {args.num_essay_test}")
    print(f"[INFO] MCQA train: {args.num_mcqa_train}, MCQA test: {args.num_mcqa_test}")
    print(f"[INFO] Output directory: {output_dir}")

    # Build the request object (used for config, but we call steps manually)
    request = SFTGenerationRequest(
        generative_model=model,
        base_url=base_url,
        chunk_data=chunk_data,
        num_essay_train_samples=args.num_essay_train,
        num_mcqa_train_samples=args.num_mcqa_train,
        num_essay_test_samples=args.num_essay_test,
        num_mcqa_test_samples=args.num_mcqa_test,
    )

    # ---------------------------------------------------------------
    # Step 1: Keyword extraction
    # ---------------------------------------------------------------
    existing_keywords = check_step(output_dir, "keywords", "Keyword extraction")
    if existing_keywords is not None:
        chunks_with_keywords = existing_keywords
    else:
        from src.core.keyword_extractor.keyword_extraction import synthesize_keyword

        print("\n[STEP 1/6] Extracting keywords...")
        chunks_with_keywords = await synthesize_keyword(
            chunk_data,
            llm_model=model,
            base_url=base_url,
        )
        saved = save_intermediate(chunks_with_keywords, output_dir, "keywords")
        print(f"  -> Saved {len(chunks_with_keywords)} keyword results to {saved}")

    # Convert chunks_with_keywords back to the format expected by downstream
    # (list of dicts with id, content, keywords, domain)
    # Already in the correct format from synthesize_keyword.

    # ---------------------------------------------------------------
    # Step 2: Essay question generation
    # ---------------------------------------------------------------
    final_data = []
    need_essay = args.num_essay_train > 0 or args.num_essay_test > 0
    if need_essay:
        existing_eq = check_step(output_dir, "essay_questions", "Essay question generation")
        if existing_eq is not None:
            essay_questions = existing_eq
        else:
            from src.core.essay_QA_generator.essay_question_generation import synthesize_question

            total_essay = args.num_essay_train + args.num_essay_test
            if total_essay == 0:
                essay_questions = []
            else:
                train_ratio = args.num_essay_train / total_essay
                print(f"\n[STEP 2/6] Generating {total_essay} essay questions (train_ratio={train_ratio:.2f})...")
                essay_questions = await synthesize_question(
                    chunks_list=chunks_with_keywords,
                    total_num_questions=total_essay,
                    train_test_ratio=train_ratio,
                    llm_model=model,
                    base_url=base_url,
                )
                saved = save_intermediate(essay_questions, output_dir, "essay_questions")
                print(f"  -> Saved {len(essay_questions)} essay questions to {saved}")

        # ---------------------------------------------------------------
        # Step 3: Essay answer generation
        # ---------------------------------------------------------------
        if essay_questions:
            existing_ea = check_step(output_dir, "essay_answers", "Essay answer generation")
            if existing_ea is not None:
                essay_answers = existing_ea
            else:
                from src.core.essay_QA_generator.essay_answer_generation import synthesize_answer

                print(f"\n[STEP 3/6] Generating {len(essay_questions)} essay answers...")
                essay_answers = await synthesize_answer(
                    essay_questions,
                    llm_model=model,
                    base_url=base_url,
                )
                saved = save_intermediate(essay_answers, output_dir, "essay_answers")
                print(f"  -> Saved {len(essay_answers)} essay answers to {saved}")

            # Convert to ResponseSFTItem dict format
            for ans in essay_answers:
                final_data.append({
                    "question": ans["question"],
                    "answer": ans["answer"],
                    "id": ans["question_id"],
                    "question_type": ans["question_type"],
                    "domain": ans["domain"],
                    "original_document": ans["chunk_id"],
                    "data_type": ans["data_type"],
                })
    else:
        print("[SKIP] No essay samples requested.")

    # ---------------------------------------------------------------
    # Step 4: MCQA question generation
    # ---------------------------------------------------------------
    need_mcqa = args.num_mcqa_train > 0 or args.num_mcqa_test > 0
    if need_mcqa:
        existing_mq = check_step(output_dir, "mcqa_questions", "MCQA question generation")
        if existing_mq is not None:
            mcqa_questions = existing_mq
        else:
            from src.core.mcqa_QA_generator.mcqa_question_generation import synthesize_mcqa_question

            total_mcqa = args.num_mcqa_train + args.num_mcqa_test
            if total_mcqa == 0:
                mcqa_questions = []
            else:
                train_ratio = args.num_mcqa_train / total_mcqa
                print(f"\n[STEP 4/6] Generating {total_mcqa} MCQA questions (train_ratio={train_ratio:.2f})...")
                mcqa_questions = await synthesize_mcqa_question(
                    chunks_list=chunk_data,
                    total_num_mcqa_questions=total_mcqa,
                    train_test_ratio=train_ratio,
                    llm_model=model,
                    base_url=base_url,
                )
                saved = save_intermediate(mcqa_questions, output_dir, "mcqa_questions")
                print(f"  -> Saved {len(mcqa_questions)} MCQA questions to {saved}")

        # ---------------------------------------------------------------
        # Step 5: MCQA answer generation
        # ---------------------------------------------------------------
        if mcqa_questions:
            existing_ma = check_step(output_dir, "mcqa_answers", "MCQA answer generation")
            if existing_ma is not None:
                mcqa_answers = existing_ma
            else:
                from src.core.mcqa_QA_generator.mcqa_answer_generation import synthesize_mcqa_answers

                print(f"\n[STEP 5/6] Generating {len(mcqa_questions)} MCQA answers...")
                mcqa_answers = await synthesize_mcqa_answers(
                    mcqa_questions,
                    llm_model=model,
                )
                saved = save_intermediate(mcqa_answers, output_dir, "mcqa_answers")
                print(f"  -> Saved {len(mcqa_answers)} MCQA answers to {saved}")

            # Convert to ResponseSFTItem dict format
            for ans in mcqa_answers:
                final_data.append({
                    "question": ans["question"],
                    "answer": ans["answer"],
                    "id": ans["question_id"],
                    "question_type": ans["question_type"],
                    "domain": ans["domain"],
                    "original_document": ans["chunk_id"],
                    "data_type": ans["data_type"],
                })
    else:
        print("[SKIP] No MCQA samples requested.")

    # ---------------------------------------------------------------
    # Step 6: Write final SFT data
    # ---------------------------------------------------------------
    final_path = step_file_path(output_dir, "sft_data")
    with open(final_path, "w", encoding="utf-8") as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)

    print(f"\n[SUCCESS] Generated {len(final_data)} SFT samples total")
    for item in final_data:
        print(f"  - [{item['data_type']}] [{item['question_type']}] {item['id']}: {item['question'][:60]}...")
    print(f"[SUCCESS] Final output: {final_path}")
    print(f"[SUCCESS] Intermediate files in: {output_dir}/")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate SFT (Supervised Fine-Tuning) data from document chunks.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python src/generate_sft_data.py --input chunks.json --output ./sft_output

  # Customize sample counts
  python src/generate_sft_data.py --input chunks.json --output ./sft_output \\
      --num-essay-train 20 --num-essay-test 5 \\
      --num-mcqa-train 10 --num-mcqa-test 3

  # Specify model (overrides llm_config.yaml)
  python src/generate_sft_data.py --input chunks.json --output ./sft_output \\
      --model gpt-4o-mini --base-url https://api.openai.com/v1

  # Resume from interrupted run (just re-run the same command)
  python src/generate_sft_data.py --input chunks.json --output ./sft_output
        """,
    )

    parser.add_argument(
        "--input", "-i",
        type=str,
        required=True,
        help="Path to input JSON/JSONL file containing chunk data.",
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        required=True,
        help="Path to output DIRECTORY (not file). Intermediate results will be stored here.",
    )
    parser.add_argument(
        "--num-essay-train",
        type=int,
        default=20,
        help="Number of essay (tự luận) training samples to generate (default: 20).",
    )
    parser.add_argument(
        "--num-essay-test",
        type=int,
        default=0,
        help="Number of essay (tự luận) test samples to generate (default: 0).",
    )
    parser.add_argument(
        "--num-mcqa-train",
        type=int,
        default=5,
        help="Number of MCQA (trắc nghiệm) training samples to generate (default: 5).",
    )
    parser.add_argument(
        "--num-mcqa-test",
        type=int,
        default=0,
        help="Number of MCQA (trắc nghiệm) test samples to generate (default: 0).",
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
        default=None,
        help="LLM API base URL (overrides llm_config.yaml).",
    )
    return parser.parse_args()


def main() -> None:
    """Entry point."""
    args = parse_args()
    asyncio.run(run_pipeline(args))


if __name__ == "__main__":
    main()