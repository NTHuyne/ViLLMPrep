import asyncio
import itertools
from typing import List, Union

from src.core.openai_calling.call_openai import OpenAIGenerator


def normalize_base_urls(base_url: Union[str, List[str]]) -> List[str]:
    """Accept str | list, support comma-separated; return non-empty list[str]."""
    if isinstance(base_url, str):
        parts = [u.strip() for u in base_url.split(",")]
    else:
        parts = [p.strip() for u in base_url for p in str(u).split(",")]
    return [p for p in parts if p]


class OpenAIClientPool:
    """Round-robin OpenAI client pool with per-URL concurrency limits."""

    def __init__(
        self,
        llm_model: str,
        base_urls: Union[str, List[str]],
        num_workers: int,
    ) -> None:
        urls = normalize_base_urls(base_urls)
        if not urls:
            raise ValueError("At least one base URL is required.")

        self.clients = [
            OpenAIGenerator(llm_model=llm_model, base_url=url) for url in urls
        ]
        per_url = max(1, num_workers // len(self.clients))
        self.semaphores = [asyncio.Semaphore(per_url) for _ in self.clients]
        self._counter = itertools.count()
        self.per_url = per_url
        self.num_workers = num_workers
        self.base_urls = urls

    async def call_openai(self, messages, **kwargs):
        i = next(self._counter) % len(self.clients)
        async with self.semaphores[i]:
            return await self.clients[i].call_openai(messages, **kwargs)
