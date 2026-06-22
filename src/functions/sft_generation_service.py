import asyncio
import logging
import traceback
from typing import List
from src.core.keyword_extractor.keyword_extraction import synthesize_keyword
from src.core.essay_QA_generator.essay_question_generation import synthesize_question
from src.core.essay_QA_generator.essay_answer_generation import synthesize_answer
from src.core.mcqa_QA_generator.mcqa_question_generation import synthesize_mcqa_question
from src.core.mcqa_QA_generator.mcqa_answer_generation import synthesize_mcqa_answers
from src.core.utils.dump_utils import save_to_tmp
from src.schemas.schemas import SFTGenerationRequest, ResponseSFTItem


logger = logging.getLogger("sft_generation_service")

async def generate_sft_data(request: SFTGenerationRequest) -> List[ResponseSFTItem]:
    """
    Generate SFT data based on the provided request.

    Args:
        request (SFTGenerationRequest): The request containing input data and parameters.

    Returns:
        List[ResponseSFTItem]: A list of generated SFT response items.
    """

    if not request.chunk_data:
        raise ValueError("Input chunk data is required.")
    
    if request.num_essay_train_samples > 0 or request.num_essay_test_samples > 0:
        # Extract keywords
        try:
            chunks_with_keywords = await synthesize_keyword(request.chunk_data, llm_model=request.generative_model, base_url=request.base_url)
            save_to_tmp(chunks_with_keywords, "sft_keywords")
        except Exception as e:
            logger.exception("Error extracting keywords")
            chunks_with_keywords = []

        # Generate essay questions
        try:
            essay_questions = await synthesize_question(
                chunks_list=chunks_with_keywords,
                total_num_questions=request.num_essay_train_samples + request.num_essay_test_samples,
                train_test_ratio=request.num_essay_train_samples / (request.num_essay_train_samples + request.num_essay_test_samples),
                llm_model=request.generative_model,
                base_url=request.base_url
            )
            save_to_tmp(essay_questions, "sft_essay_questions")
        except Exception as e:
            logger.exception("Error generating essay questions")
            essay_questions = []

        # Generate essay answers with retry protection
        try:
            essay_answers = await synthesize_answer(essay_questions, llm_model=request.generative_model, base_url=request.base_url)
            save_to_tmp(essay_answers, "sft_essay_answers")
        except Exception as e:
            logger.exception("Error generating essay answers, questions have been dumped for recovery")
            essay_answers = []

        # Compile essay SFT data
        essay_sft_data = [
            ResponseSFTItem(
                question=answer['question'],
                answer=answer['answer'],
                id=answer['question_id'],
                question_type=answer['question_type'],
                domain=answer['domain'],
                original_document=answer['chunk_id'],
                data_type=answer['data_type']
            )
            for answer in essay_answers
        ]
    else:
        essay_sft_data = []


    if request.num_mcqa_train_samples > 0 or request.num_mcqa_test_samples > 0:
        # Generate MCQA questions
        try:
            mcqa_questions = await synthesize_mcqa_question(
                chunks_list=request.chunk_data,
                total_num_mcqa_questions=request.num_mcqa_train_samples + request.num_mcqa_test_samples,
                train_test_ratio=request.num_mcqa_train_samples / (request.num_mcqa_train_samples + request.num_mcqa_test_samples),
                llm_model=request.generative_model,
                base_url=request.base_url
            )
            save_to_tmp(mcqa_questions, "sft_mcqa_questions")
        except Exception as e:
            logger.exception("Error generating MCQA questions")
            mcqa_questions = []

        # Generate MCQA answers with retry protection
        try:
            mcqa_answers = await synthesize_mcqa_answers(mcqa_questions, llm_model=request.generative_model)
            save_to_tmp(mcqa_answers, "sft_mcqa_answers")
        except Exception as e:
            logger.exception("Error generating MCQA answers, questions have been dumped for recovery")
            mcqa_answers = []

        # Compile MCQA SFT data
        mcqa_sft_data = [
            ResponseSFTItem(
                question=answer['question'],
                answer=answer['answer'],
                id=answer['question_id'],
                question_type=answer['question_type'],
                domain=answer['domain'],
                original_document=answer['chunk_id'],
                data_type=answer['data_type'],
                base_url=request.base_url
            )
            for answer in mcqa_answers
        ]
    else:
        mcqa_sft_data = []
        

    # Combine essay and MCQA data
    return essay_sft_data + mcqa_sft_data
