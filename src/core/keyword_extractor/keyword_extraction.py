import asyncio
import traceback
from typing import List, Any
from tqdm import tqdm
from src.core.openai_calling.client_pool import OpenAIClientPool
from src.core.utils.utils import get_items_from_output
from src.core.utils.dump_utils import save_to_tmp
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
        save_to_tmp(messages, f"request_keyword_{chunk_id}")
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
        print(f"Error processing chunk {chunk_id}: {e}")
        traceback.print_exc()
        return None

async def synthesize_keyword(
        chunk_data: List[Any], 
        num_workers=settings.LLM_CONFIG_YML['batch_size'], 
        llm_model=settings.MODEL_CONF['model_name'], 
        base_url=settings.MODEL_CONF['base_url']
        ):
    """
    Synthesize keywords for each chunk of text

    Args:
        chunk_data: List of dictionaries containing chunk_id, content, domain
        num_workers: Total concurrent requests across all base URLs
    Returns:
        List of dictionaries containing chunk_id, content, keywords
    """
    openai_client = OpenAIClientPool(
        llm_model=llm_model, base_urls=base_url, num_workers=num_workers
    )

    tasks = [
        process_chunk(
            chunk_id=chunk.chunk_id, content=chunk.content, openai_client=openai_client,
            domain=chunk.domain
        )
        for chunk in chunk_data
    ]

    results = []
    for coro in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Extracting keywords"):
        result = await coro
        if result is None:
            continue
        results.append(result)

    return results
