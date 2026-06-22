import asyncio
import re
import random
import traceback
from typing import List
from tqdm import tqdm
from src.core.openai_calling.client_pool import OpenAIClientPool
from src.core.prompts.mcqa_question_generation import MCQA_QUESTION_GENERATION_PROMPT
from src.configs.config import settings
from src.core.utils.dump_utils import save_to_tmp

async def process_mcqa_question(
        chunk_id,
        content,
        domain,
        openai_client,
        num_questions
        ):
    """
    Process chunk of text to generate multiple choice questions
    
    Args:
        chunk_id: Unique identifier for the chunk
        content: Text content to generate questions from
        domain: Domain of the content
        openai_client: OpenAIGenerator instance
        num_questions: Number of questions to generate
    Returns:
        List of dictionaries containing chunk_id, question_id, domain, question, choice
    """
    try:
        results = []
        messages = [
            {
                "role": "user",
                "content": MCQA_QUESTION_GENERATION_PROMPT.format(
                    domain=domain,
                    content=content,
                    num_questions=num_questions
                )
            }
        ]
        save_to_tmp(messages, f"request_mcqa_question_{chunk_id}")
        sample = await openai_client.call_openai(messages)
        if sample.strip():
            question_matches = re.findall(r'<question>(.*?)</question>', sample, re.DOTALL)
            choice_matches = re.findall(r'<choice>(.*?)</choice>', sample, re.DOTALL)

            for i in range(len(question_matches)):
                question = question_matches[i].strip()
                choice = choice_matches[i].strip()

                results.append({
                    'chunk_id': chunk_id,
                    'content': content,
                    'domain': domain,
                    'question_id': f"{chunk_id}-mcq{i}",
                    'question': question,
                    'choice': choice,
                    'question_type': 'tracnghiem'
                })

        return results

    except Exception as e:
        print(f"Error processing chunk {chunk_id}: {e}")
        traceback.print_exc()
        return None

async def synthesize_mcqa_question(
        chunks_list: List[str], 
        total_num_mcqa_questions: int, 
        train_test_ratio: float, 
        num_workers=settings.LLM_CONFIG_YML['batch_size'], 
        llm_model=settings.MODEL_CONF['model_name'], 
        base_url=settings.MODEL_CONF['base_url']
        ):
    """
    Synthesize multiple choice questions for each chunk of text
    
    Args:
        chunks_list: List of dictionaries containing chunk_id, content, domain
        total_num_mcqa_questions: Total number of multiple choice questions to generate
        train_test_ratio: Ratio of train to test data
        num_workers: Total concurrent requests across all base URLs
    Returns:
        List of dictionaries containing chunk_id, content, domain, question_id, question, choice, data_type
    """

    openai_client = OpenAIClientPool(
        llm_model=llm_model, base_urls=base_url, num_workers=num_workers
    )

    num_questions_per_chunk = max(1, round(total_num_mcqa_questions / len(chunks_list)))

    tasks = [
        process_mcqa_question(
            chunk_id=chunk.chunk_id, content=chunk.content, domain=chunk.domain,
            openai_client=openai_client, num_questions=num_questions_per_chunk
        )
        for chunk in chunks_list
    ]

    results = []
    for coro in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Generating mcqa questions"):
        res = await coro
        if res is None:
            continue
        results.extend(res)
            
    # Shuffle results before splitting
    random.shuffle(results)

    # Split results into train and test based on the train_test_ratio
    train_size = int(len(results) * train_test_ratio)
    for i, result in enumerate(results):
        result['data_type'] = 'train' if i < train_size else 'test'

    return results
