import asyncio
import random
from typing import List, Any
from tqdm import tqdm
from src.core.openai_calling.call_openai import OpenAIGenerator
from src.core.utils.utils import get_items_from_output
from src.core.prompts.question_generation import QUESTION_GENERATION
from src.configs.config import settings


async def process_question(
        chunk_id,
        content,
        domain,
        openai_client,
        keywords_list,
        num_questions
        ):
    """
    Process chunk of text to generate questions
    
    Args:
        chunk_id: Unique identifier for the chunk
        content: Text content to generate questions from
        domain: Domain of the content
        openai_client: OpenAIGenerator instance
        keywords_list: List of keywords to generate questions from
        num_questions: Number of questions to generate for each keyword
    Returns:
        List of dictionaries containing chunk_id, question_id, domain, question, question_type
    """
    try:
        results = []
        sample = await openai_client.call_openai([
            {
                "role": "user",
                "content": QUESTION_GENERATION.format(
                    domain=domain,
                    content=content,
                    keyword=keywords_list,
                    num_questions=num_questions
                )
            }
        ])

        if sample.strip():
            questions = get_items_from_output(sample)

        for qid, question in enumerate(questions):
            results.append({
                'chunk_id': chunk_id,
                'question_id': f"{chunk_id}-q{qid}",
                'content': content,
                'domain': domain,
                'question': question,
                'question_type': 'tuluan',
            })

        return results

    except Exception as e:
        print(f"Error processing chunk: {e}")
        raise


async def synthesize_question(
        chunks_list: List[Any], 
        total_num_questions: int, 
        train_test_ratio: float, 
        batch_size=settings.LLM_CONFIG_YML['batch_size'], 
        llm_model=settings.MODEL_CONF['model_name'], 
        base_url=settings.MODEL_CONF['base_url']
        ):
    """
    Synthesize questions for each chunk of text
    
    Args:
        chunks_list: List of dictionaries containing chunk_id, content, domain, keywords
        total_num_questions: Total number of questions to generate
        batch_size: Number of chunks to process in concurrent batches
        train_test_ratio: Ratio of train to test data
    Returns:
        List of dictionaries containing chunk_id, question_id, domain, question, question_type, data_type
    """
    openai_client = OpenAIGenerator(llm_model, base_url=base_url)

    num_questions_per_chunk = max(1, round(total_num_questions / len(chunks_list)))


    tasks = [
        process_question(
            chunk_id=chunk['id'], content=chunk['content'], openai_client=openai_client,
            domain=chunk['domain'], keywords_list=chunk['keywords'], num_questions=num_questions_per_chunk
        )
        for chunk in chunks_list
    ]

    # Process in batches
    results = []
    for i in tqdm(range(0, len(tasks), batch_size), desc="Generating seed questions"):
        batch_tasks = tasks[i:i + batch_size]
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
