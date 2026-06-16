import asyncio
from typing import List
from src.core.keyword_extractor.keyword_extraction import synthesize_keyword
from src.core.essay_QA_generator.essay_question_generation import synthesize_question
from src.core.dpo_answer_generation.dpo_answer_generation import synthesize_dpo_answer
from src.schemas.schemas import DPOGenerationRequest, ResponseDPOItem

async def generate_dpo_data(request: DPOGenerationRequest) -> List[ResponseDPOItem]:
    """
    Generate DPO data based on the provided request."
    
    Args:
        request (DPOGenerationRequest): The request containing input data and parameters.
    Returns:
        List[ResponseDPOItem]: A list of generated DPO response items.
    """
    if request.num_samples > 0:

        # Extract keywords
        chunks_with_keywords = await synthesize_keyword(request.chunk_data, llm_model=request.generative_model, base_url=request.base_url)

        # Generate essay questions
        essay_questions = await synthesize_question(
            chunks_list=chunks_with_keywords,
            total_num_questions=request.num_samples,
            train_test_ratio=1,
            llm_model=request.generative_model,
            base_url=request.base_url
        )

        # Generate dpo answers
        dpo_answers = await synthesize_dpo_answer(essay_questions, llm_model=request.generative_model, base_url=request.base_url)


        # Compile dpo SFT data
        dpo_data = [
            ResponseDPOItem(
                question=answer['question'],
                accepted_answer=answer['accepted_answer'],
                rejected_answer=answer['rejected_answer'],
                id=answer['question_id'],
                domain=answer['domain'],
                original_document=answer['chunk_id'],
            )
            for answer in dpo_answers
        ]
        
    else:
        dpo_data = []

    return dpo_data
