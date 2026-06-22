"""
Unit tests for dump request mechanism and error handling (try/catch + traceback)
in question generation and answer generation modules.
"""
import asyncio
import json
import os
import tempfile
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

pytestmark = pytest.mark.asyncio

from src.core.essay_QA_generator.essay_question_generation import (
    process_question,
    synthesize_question,
)
from src.core.essay_QA_generator.essay_answer_generation import (
    process_answer,
    synthesize_answer,
)
from src.core.mcqa_QA_generator.mcqa_question_generation import (
    process_mcqa_question,
    synthesize_mcqa_question,
)
from src.core.mcqa_QA_generator.mcqa_answer_generation import (
    process_mcqa_answer,
    synthesize_mcqa_answers,
)
from src.core.keyword_extractor.keyword_extraction import (
    process_chunk,
    synthesize_keyword,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def openai_client():
    """Return a mocked OpenAIGenerator instance."""
    client = MagicMock()
    client.call_openai = AsyncMock()
    return client


@pytest.fixture
def dummy_chunks():
    """Return a list of chunk dicts as used by synthesize_question."""
    return [
        {
            "id": "chunk_0",
            "content": "Nội dung chunk 0.",
            "domain": "Khoa học",
            "keywords": ["keyword1", "keyword2"],
        },
        {
            "id": "chunk_1",
            "content": "Nội dung chunk 1.",
            "domain": "Khoa học",
            "keywords": ["keyword3"],
        },
        {
            "id": "chunk_2",
            "content": "Nội dung chunk 2.",
            "domain": "Khoa học",
            "keywords": ["keyword4"],
        },
    ]


@pytest.fixture
def dummy_questions():
    """Return a list of question dicts as used by synthesize_answer."""
    return [
        {
            "chunk_id": "chunk_0",
            "question_id": "chunk_0-q0",
            "content": "Nội dung chunk 0.",
            "domain": "Khoa học",
            "question": "Câu hỏi 1?",
            "question_type": "tuluan",
            "data_type": "train",
        },
        {
            "chunk_id": "chunk_1",
            "question_id": "chunk_1-q0",
            "content": "Nội dung chunk 1.",
            "domain": "Khoa học",
            "question": "Câu hỏi 2?",
            "question_type": "tuluan",
            "data_type": "train",
        },
    ]


@pytest.fixture
def dummy_mcqa_chunks():
    """Return a list of chunk objects (with .chunk_id etc.) for synthesize_mcqa_question."""
    class FakeChunk:
        def __init__(self, chunk_id, content, domain):
            self.chunk_id = chunk_id
            self.content = content
            self.domain = domain
    return [
        FakeChunk("mcq_chunk_0", "Nội dung MC chunk 0.", "Toán"),
        FakeChunk("mcq_chunk_1", "Nội dung MC chunk 1.", "Toán"),
    ]


@pytest.fixture
def dummy_mcqa_questions():
    """Return a list of MCQA question dicts for synthesize_mcqa_answers."""
    return [
        {
            "chunk_id": "mcq_chunk_0",
            "question_id": "mcq_chunk_0-mcq0",
            "content": "Nội dung MC chunk 0.",
            "domain": "Toán",
            "question": "MC câu hỏi 1?",
            "choice": "A. 1\nB. 2\nC. 3\nD. 4",
            "question_type": "tracnghiem",
            "data_type": "train",
        },
        {
            "chunk_id": "mcq_chunk_1",
            "question_id": "mcq_chunk_1-mcq0",
            "content": "Nội dung MC chunk 1.",
            "domain": "Toán",
            "question": "MC câu hỏi 2?",
            "choice": "A. 1\nB. 2\nC. 3\nD. 4",
            "question_type": "tracnghiem",
            "data_type": "train",
        },
    ]


# ---------------------------------------------------------------------------
# Test: dump request before calling LLM (Yêu cầu 1)
# ---------------------------------------------------------------------------

class TestDumpRequestBeforeCall:
    """Verify that save_to_tmp is called with the request payload before calling LLM."""

    @patch("src.core.essay_QA_generator.essay_question_generation.save_to_tmp")
    async def test_process_question_dumps_request(self, mock_save, openai_client):
        # get_items_from_output parses "1. text" format
        openai_client.call_openai.return_value = "1. Câu hỏi 1\n2. Câu hỏi 2"
        result = await process_question(
            chunk_id="chunk_test",
            content="Test content",
            domain="Test",
            openai_client=openai_client,
            keywords_list=["kw1"],
            num_questions=2,
        )
        # Verify save_to_tmp was called with the messages dict
        assert mock_save.called, "save_to_tmp should be called before calling LLM"
        call_args = mock_save.call_args[0]
        assert isinstance(call_args[0], list), "First arg should be the messages list"
        assert "request_essay_question_" in call_args[1], (
            f"Prefix should contain 'request_essay_question_', got {call_args[1]}"
        )
        # Verify result is not None
        assert result is not None
        assert len(result) == 2

    @patch("src.core.essay_QA_generator.essay_answer_generation.save_to_tmp")
    async def test_process_answer_dumps_request(self, mock_save, openai_client):
        openai_client.call_openai.return_value = "Đây là câu trả lời."
        result = await process_answer(
            chunk_id="chunk_test",
            question_id="chunk_test-q0",
            content="Test content",
            domain="Test",
            openai_client=openai_client,
            question="Câu hỏi?",
            question_type="tuluan",
            data_type="train",
        )
        assert mock_save.called, "save_to_tmp should be called before calling LLM"
        call_args = mock_save.call_args[0]
        assert isinstance(call_args[0], list), "First arg should be the messages list"
        assert "request_essay_answer_" in call_args[1], (
            f"Prefix should contain 'request_essay_answer_', got {call_args[1]}"
        )
        assert result is not None
        assert result[0]["answer"] == "Đây là câu trả lời."

    @patch("src.core.mcqa_QA_generator.mcqa_question_generation.save_to_tmp")
    async def test_process_mcqa_question_dumps_request(self, mock_save, openai_client):
        openai_client.call_openai.return_value = (
            "<question>MCQ 1?</question><choice>A. 1\nB. 2</choice>"
        )
        result = await process_mcqa_question(
            chunk_id="mcq_test",
            content="Test content",
            domain="Test",
            openai_client=openai_client,
            num_questions=1,
        )
        assert mock_save.called, "save_to_tmp should be called before calling LLM"
        call_args = mock_save.call_args[0]
        assert isinstance(call_args[0], list)
        assert "request_mcqa_question_" in call_args[1]
        assert result is not None
        assert len(result) == 1

    @patch("src.core.mcqa_QA_generator.mcqa_answer_generation.save_to_tmp")
    async def test_process_mcqa_answer_dumps_request(self, mock_save, openai_client):
        openai_client.call_openai.return_value = "A"
        result = await process_mcqa_answer(
            chunk_id="mcq_test",
            question_id="mcq_test-mcq0",
            content="Test content",
            question="MCQ 1?",
            choice="A. 1\nB. 2\nC. 3\nD. 4",
            domain="Test",
            question_type="tracnghiem",
            openai_client=openai_client,
            data_type="train",
        )
        assert mock_save.called, "save_to_tmp should be called before calling LLM"
        call_args = mock_save.call_args[0]
        assert isinstance(call_args[0], list)
        assert "request_mcqa_answer_" in call_args[1]
        assert result is not None
        assert result[0]["answer"] == "A"


# ---------------------------------------------------------------------------
# Test: error handling - when LLM raises exception (Yêu cầu 2)
# ---------------------------------------------------------------------------

class TestErrorHandling:
    """Verify that exceptions are caught, printed, and None is returned."""

    async def test_process_question_returns_none_on_error(self, openai_client):
        openai_client.call_openai.side_effect = Exception("LLM connection timeout")
        result = await process_question(
            chunk_id="chunk_err",
            content="Test",
            domain="Test",
            openai_client=openai_client,
            keywords_list=["kw"],
            num_questions=1,
        )
        assert result is None, "Should return None on exception"

    async def test_process_answer_returns_none_on_error(self, openai_client):
        openai_client.call_openai.side_effect = Exception("LLM API error")
        result = await process_answer(
            chunk_id="chunk_err",
            question_id="chunk_err-q0",
            content="Test",
            domain="Test",
            openai_client=openai_client,
            question="Câu hỏi?",
            question_type="tuluan",
            data_type="train",
        )
        assert result is None, "Should return None on exception"

    async def test_process_mcqa_question_returns_none_on_error(self, openai_client):
        openai_client.call_openai.side_effect = Exception("LLM timeout")
        result = await process_mcqa_question(
            chunk_id="mcq_err",
            content="Test",
            domain="Test",
            openai_client=openai_client,
            num_questions=1,
        )
        assert result is None, "Should return None on exception"

    async def test_process_mcqa_answer_returns_none_on_error(self, openai_client):
        openai_client.call_openai.side_effect = Exception("LLM API error")
        result = await process_mcqa_answer(
            chunk_id="mcq_err",
            question_id="mcq_err-mcq0",
            content="Test",
            question="MCQ 1?",
            choice="A. 1\nB. 2",
            domain="Test",
            question_type="tracnghiem",
            openai_client=openai_client,
            data_type="train",
        )
        assert result is None, "Should return None on exception"


# ---------------------------------------------------------------------------
# Test: synthesize functions handle None results from process_* (Yêu cầu 2)
# ---------------------------------------------------------------------------

class TestSynthesizeNoneHandling:
    """Verify that synthesize functions skip None results gracefully."""

    async def test_synthesize_answer_handles_none_result(self, dummy_questions):
        """process_answer returns None -> synthesize_answer should skip it."""
        openai_client = MagicMock()
        # Return a valid answer, then None (simulating a failed task that returned None)
        openai_client.call_openai = AsyncMock(return_value="Câu trả lời 1")

        async def mock_process_answer(**kwargs):
            if kwargs.get("question_id") == "chunk_1-q0":
                return None  # simulate process_answer returning None
            return [{
                "chunk_id": kwargs["chunk_id"],
                "question_id": kwargs["question_id"],
                "answer": "Câu trả lời 1",
                "domain": kwargs["domain"],
                "question": kwargs["question"],
                "question_type": kwargs["question_type"],
                "data_type": kwargs["data_type"],
            }]

        with patch(
            "src.core.essay_QA_generator.essay_answer_generation.process_answer",
            side_effect=mock_process_answer,
        ), patch(
            "src.core.essay_QA_generator.essay_answer_generation.OpenAIClientPool",
            return_value=openai_client,
        ):
            results = await synthesize_answer(
                questions=dummy_questions,
                num_workers=10,
                llm_model="test-model",
                base_url="http://test",
            )

        assert len(results) == 1, "Only 1 result should survive (second task returned None)"
        assert results[0]["answer"] == "Câu trả lời 1"

    async def test_synthesize_mcqa_answers_handles_none(self, dummy_mcqa_questions):
        """process_mcqa_answer returns None -> synthesize_mcqa_answers should skip it."""
        async def mock_process_answer(**kwargs):
            if kwargs.get("question_id") == "mcq_chunk_1-mcq0":
                return None
            return [{
                "chunk_id": kwargs["chunk_id"],
                "question_id": kwargs["question_id"],
                "answer": "A",
                "domain": kwargs["domain"],
                "question": kwargs["question"],
                "question_type": kwargs["question_type"],
                "data_type": kwargs["data_type"],
            }]

        openai_client = MagicMock()
        with patch(
            "src.core.mcqa_QA_generator.mcqa_answer_generation.process_mcqa_answer",
            side_effect=mock_process_answer,
        ), patch(
            "src.core.mcqa_QA_generator.mcqa_answer_generation.OpenAIClientPool",
            return_value=openai_client,
        ):
            results = await synthesize_mcqa_answers(
                questions=dummy_mcqa_questions,
                num_workers=10,
                llm_model="test-model",
                base_url="http://test",
            )

        assert len(results) == 1, "Only 1 result should survive (second task returned None)"
        assert results[0]["answer"] == "A"

    async def test_synthesize_question_handles_none_result(self, dummy_chunks):
        """process_question returns None -> synthesize_question should skip it."""
        async def mock_process_question(**kwargs):
            if kwargs.get("chunk_id") == "chunk_1":
                return None
            return [
                {"chunk_id": kwargs["chunk_id"], "question_id": f"{kwargs['chunk_id']}-q0",
                 "question": "Q?", "domain": kwargs["domain"], "question_type": "tuluan",
                 "content": kwargs["content"]}
            ]

        openai_client = MagicMock()
        with patch(
            "src.core.essay_QA_generator.essay_question_generation.process_question",
            side_effect=mock_process_question,
        ), patch(
            "src.core.essay_QA_generator.essay_question_generation.OpenAIClientPool",
            return_value=openai_client,
        ):
            results = await synthesize_question(
                chunks_list=dummy_chunks,
                total_num_questions=6,
                train_test_ratio=0.8,
                num_workers=10,
                llm_model="test-model",
                base_url="http://test",
            )

        assert len(results) == 2, "Only 2 results should survive (chunk_1 returned None)"
        chunk_ids = [r["chunk_id"] for r in results]
        assert "chunk_1" not in chunk_ids

    async def test_synthesize_keyword_handles_none(self):
        """process_chunk returns None -> synthesize_keyword should skip it."""
        async def mock_process_chunk(**kwargs):
            if kwargs.get("chunk_id") == "chunk_1":
                return None
            return {"id": kwargs["chunk_id"], "content": "Content", "keywords": ["kw1"], "domain": kwargs["domain"]}

        class FakeChunk:
            def __init__(self, chunk_id, content, domain):
                self.chunk_id = chunk_id
                self.content = content
                self.domain = domain

        chunks = [
            FakeChunk("chunk_0", "Content 0", "Domain"),
            FakeChunk("chunk_1", "Content 1", "Domain"),
        ]

        openai_client = MagicMock()
        with patch(
            "src.core.keyword_extractor.keyword_extraction.process_chunk",
            side_effect=mock_process_chunk,
        ), patch(
            "src.core.keyword_extractor.keyword_extraction.OpenAIClientPool",
            return_value=openai_client,
        ):
            results = await synthesize_keyword(
                chunk_data=chunks,
                num_workers=10,
                llm_model="test-model",
                base_url="http://test",
            )

        assert len(results) == 1, "Only 1 result should survive (chunk_1 returned None)"
        assert results[0]["id"] == "chunk_0"

    async def test_synthesize_all_tasks_fail_returns_empty(self, dummy_questions):
        """All process_* return None -> empty list."""
        async def mock_process_answer(**kwargs):
            return None

        openai_client = MagicMock()
        with patch(
            "src.core.essay_QA_generator.essay_answer_generation.process_answer",
            side_effect=mock_process_answer,
        ), patch(
            "src.core.essay_QA_generator.essay_answer_generation.OpenAIClientPool",
            return_value=openai_client,
        ):
            results = await synthesize_answer(
                questions=dummy_questions,
                num_workers=10,
                llm_model="test-model",
                base_url="http://test",
            )

        assert results == [], "Should return empty list when all tasks return None"


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])