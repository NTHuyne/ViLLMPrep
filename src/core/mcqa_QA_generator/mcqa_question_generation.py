import asyncio
import re
import random
from typing import List
from tqdm import tqdm
from src.core.openai_calling.call_openai import OpenAIGenerator
from src.core.prompts.mcqa_question_generation import MCQA_QUESTION_GENERATION_PROMPT
from src.configs.config import settings

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
        sample = await openai_client.call_openai([
            {
                "role": "user",
                "content": MCQA_QUESTION_GENERATION_PROMPT.format(
                    domain=domain,
                    content=content,
                    num_questions=num_questions
                )
            }
        ])
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
        print(f"Error processing chunk: {e}")
        raise

async def synthesize_mcqa_question(
        chunks_list: List[str], 
        total_num_mcqa_questions: int, 
        train_test_ratio: float, 
        batch_size=settings.LLM_CONFIG_YML['batch_size'], 
        llm_model=settings.MODEL_CONF['model_name'], 
        base_url=settings.MODEL_CONF['base_url']
        ):
    """
    Synthesize multiple choice questions for each chunk of text
    
    Args:
        chunks_list: List of dictionaries containing chunk_id, content, domain
        total_num_mcqa_questions: Total number of multiple choice questions to generate
        train_test_ratio: Ratio of train to test data
        batch_size: Number of chunks to process in concurrent batches
    Returns:
        List of dictionaries containing chunk_id, content, domain, question_id, question, choice, data_type
    """

    openai_client = OpenAIGenerator(llm_model, base_url=base_url)

    num_questions_per_chunk = max(1, round(total_num_mcqa_questions / len(chunks_list)))

    tasks = [
        process_mcqa_question(
            chunk_id=chunk.chunk_id, content=chunk.content, domain=chunk.domain,
            openai_client=openai_client, num_questions=num_questions_per_chunk
        )
        for chunk in chunks_list
    ]

    # Process in batches
    results = []
    for i in tqdm(range(0, len(tasks), batch_size), desc="Generating mcqa questions"):
        batch_tasks = tasks[i:i+batch_size]
        batch_results = await asyncio.gather(*batch_tasks)
        for res in batch_results:
            results.extend(res)
            
    # Shuffle results before splitting
    random.shuffle(results)

    # Split results into train and test based on the train_test_ratio
    train_size = int(len(results) * train_test_ratio)
    for i, result in enumerate(results):
        result['data_type'] = 'train' if i < train_size else 'test'

    return results
