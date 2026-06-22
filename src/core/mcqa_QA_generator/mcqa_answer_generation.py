import asyncio
from tqdm import tqdm
from typing import List, Any
from src.core.openai_calling.client_pool import OpenAIClientPool
from src.core.prompts.mcqa_answer_generation import MCQA_ANSWER_PROMPT
from src.configs.config import settings


async def process_mcqa_answer(
        chunk_id,
        question_id, 
        content, 
        question,
        choice,
        domain,
        question_type,
        openai_client,
        data_type
        ):
    """
    Process chunk of text to generate multiple choice answers
    
    Args:
        chunk_id: Unique identifier for the chunk
        question_id: Unique identifier for the question
        content: Text content to generate answers from
        question: Question to generate answer for
        choice: Choices for the question
        domain: Domain of the content
        question_type: Type of question
        openai_client: OpenAIGenerator instance
    Returns:
        List of dictionaries containing chunk_id, question_id, domain, question, answer, question_type
    """
    try:
        if data_type == "train":
            sample = await openai_client.call_openai([
                        {
                            "role": "user",
                            "content": MCQA_ANSWER_PROMPT.format(
                                content = content,
                                question = question,
                                choice = choice
                            )
                        }
                    ])
            if sample.strip():
                sample = sample.strip()
        else:
            sample = choice
        
        return [{
            'chunk_id': chunk_id,
            'question_id': question_id,
            'question': question,
            'answer': sample,
            'domain': domain,
            'question_type': question_type,
            'data_type': data_type
        }]

    except Exception as e:
        print(f"Error processing chunk: {e}")
        raise


async def synthesize_mcqa_answers(
        questions: List[Any], 
        num_workers=settings.LLM_CONFIG_YML['batch_size'], 
        llm_model=settings.MODEL_CONF['model_name'], 
        base_url=settings.MODEL_CONF['base_url']
        ):
    """
    Synthesize multiple choice answers for each question
    
    Args:
        questions: List of dictionaries containing chunk_id, question_id, content, question, choice, domain, question_type
        num_workers: Total concurrent requests across all base URLs
    Returns:
        List of dictionaries containing chunk_id, question_id, domain, question, answer, question_type"""
    openai_client = OpenAIClientPool(
        llm_model=llm_model, base_urls=base_url, num_workers=num_workers
    )

    tasks = [
        process_mcqa_answer(
            chunk_id=question['chunk_id'],
            question_id=question['question_id'],
            content=question['content'],
            question=question['question'],
            choice=question['choice'],
            domain=question['domain'],
            openai_client=openai_client,
            question_type=question['question_type'],
            data_type=question['data_type']
        )
        for question in questions
    ]

    results = []
    for coro in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Generating mcqa answer"):
        result = await coro
        results.extend(result)

    return results
