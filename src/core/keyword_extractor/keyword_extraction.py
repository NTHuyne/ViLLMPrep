import asyncio
from typing import List, Any
from tqdm import tqdm
from src.core.openai_calling.call_openai import OpenAIGenerator
from src.core.utils.utils import get_items_from_output
from src.core.prompts.keyword_extraction import KEYWORD_GENERATION
from src.configs.config import settings

async def process_chunk(
        chunk_id, 
        content, 
        domain, 
        openai_client
        ):
    """
    Process chunk of text to extract keywords
    
    Args:
        chunk_id: Unique identifier for the chunk
        content: Text content to extract keywords from
        domain: Domain of the content
        openai_client: OpenAIGenerator instance
    Returns:
        Dictionary containing chunk_id, content, keywords"""
    try:
        messages = [
            {
                "role": "user",
                "content": KEYWORD_GENERATION.format(
                    domain=domain,
                    content=content,
                )
            }
        ]
        
        sample = await openai_client.call_openai(messages)            

        if sample.strip():
            key_words = get_items_from_output(sample)
        
        chunk_with_keywords = {
            'id': chunk_id,
            'content': content,
            'keywords': key_words,
            'domain': domain
        }

        return chunk_with_keywords

    except Exception as e:
        print(f"Error processing chunk: {e}")
        raise

async def synthesize_keyword(
        chunk_data: List[Any], 
        batch_size=settings.LLM_CONFIG_YML['batch_size'], 
        llm_model=settings.MODEL_CONF['model_name'], 
        base_url=settings.MODEL_CONF['base_url']
        ):
    """
    Synthesize keywords for each chunk of text

    Args:
        chunk_data: List of dictionaries containing chunk_id, content, domain
        batch_size: Number of chunks to process in concurrent batches
    Returns:
        List of dictionaries containing chunk_id, content, keywords
    """
    openai_client = OpenAIGenerator(llm_model=llm_model, base_url=base_url)

    tasks = [
        process_chunk(
            chunk_id=chunk.chunk_id, content=chunk.content, openai_client=openai_client,
            domain=chunk.domain
        )
        for chunk in chunk_data
    ]

    # Process in batches
    results = []
    for i in tqdm(range(0, len(tasks), batch_size), desc="Extracting keywords"):
        batch_tasks = tasks[i:i+batch_size]
        batch_results = await asyncio.gather(*batch_tasks)
        results.extend(batch_results)

    return results
