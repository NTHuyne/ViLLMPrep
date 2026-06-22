import asyncio
import logging
import traceback
from typing import Any, List
from tqdm import tqdm
from src.core.openai_calling.client_pool import OpenAIClientPool
from src.core.prompts.answer_generation import ANSWER_GENERATION
from src.core.utils.dump_utils import save_to_tmp
from src.configs.config import settings


logger = logging.getLogger("essay_answer_generation")


async def process_answer(
        chunk_id,
        question_id,
        content, 
        domain, 
        openai_client, 
        question,
        question_type,
        data_type
        ):
    """
    Process chunk of text to generate answers
    
    Args:
        chunk_id: Unique identifier for the chunk
        question_id: Unique identifier for the question
        content: Text content to generate answers from
        domain: Domain of the content
        openai_client: OpenAIGenerator instance
        question: Question to generate answer for
        question_type: Type of question
        data_type: Type of data (train or test)
    Returns:
        List of dictionaries containing chunk_id, question_id, domain, question, answer, question_type
    """
    try:
        messages = [
            {
                "role": "user",
                "content": ANSWER_GENERATION.format(
                    domain=domain,
                    content=content,
                    question=question
                )
            }
        ]
        save_to_tmp(messages, f"request_essay_answer_{question_id}")
        sample = await openai_client.call_openai(messages)

        if sample.strip():
            answer = sample.strip()

        return [
            {
                'chunk_id': chunk_id,
                'question_id': question_id,
                'domain': domain,
                'question': question,
                'answer': answer,
                'question_type': question_type,
                'data_type': data_type
            }
        ]

    except Exception as e:
        print(f"Error processing chunk {chunk_id}: {e}")
        traceback.print_exc()
        return None


async def synthesize_answer(
        questions: List[Any], 
        num_workers=settings.LLM_CONFIG_YML['batch_size'], 
        llm_model=settings.MODEL_CONF['model_name'], 
        base_url=settings.MODEL_CONF['base_url']
        ):
    """
    Synthesize answers for each question
    
    Args:
        questions: List of dictionaries containing chunk_id, question_id, content, domain, question, question_type
        num_workers: Total concurrent requests across all base URLs
    Returns:
        List of dictionaries containing chunk_id, question_id, domain, question, answer, question_type"""
    openai_client = OpenAIClientPool(
        llm_model=llm_model, base_urls=base_url, num_workers=num_workers
    )

    # Create tasks
    tasks = [
        process_answer(
            chunk_id=question['chunk_id'],
            question_id=question['question_id'],
            content=question['content'],
            openai_client=openai_client,
            domain=question['domain'],
            question=question['question'],
            question_type=question['question_type'],
            data_type=question['data_type']
        )
        for question in questions
    ]

    results = []
    for coro in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Generating answers"):
        res = await coro
        if res is None:
            continue
        results.extend(res)

    return results
