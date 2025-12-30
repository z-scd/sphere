"""
LLM service using OpenRouter API
File: services/llm_service.py
"""

import os
import requests
from dotenv import load_dotenv
from typing import List, Dict, Optional

load_dotenv()

class LLMService:
    """Handles LLM interactions via OpenRouter"""

    def __init__(self):
        """Initialize LLM service with API credentials"""
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not set")

        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-120b:free")

        self.default_system_prompt = """You are a knowledgeable medical assistant helping medical students. 
Your role is to provide accurate, evidence-based information based on the provided context.

Guidelines:
- Answer based primarily on the provided context
- If the context doesn't contain enough information, acknowledge this
- Use clear, educational language appropriate for medical students
- Cite relevant information from the sources when appropriate
- If you're uncertain, express that uncertainty
- Never provide medical advice for specific patients
- Focus on educational explanations and concepts

Always prioritize accuracy and safety in your responses."""

    def generate_answer(
        self, query: str, context_docs: List[Dict], system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate an answer using the LLM

        Args:
            query: User's question
            context_docs: Retrieved documents for context
            system_prompt: Optional custom system prompt

        Returns:
            Generated answer as string
        """
        # Prepare context from retrieved documents
        context = self._format_context(context_docs)

        # Build messages
        messages = [
            {"role": "system", "content": system_prompt or self.default_system_prompt},
            {
                "role": "user",
                "content": f"""Context from medical documents:

{context}

Question: {query}

Please provide a comprehensive answer based on the context above.""",
            },
        ]

        # Make API request
        try:
            response = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://medical-rag-app.com",  # Optional: your app URL
                    "X-Title": "Medical RAG Application",  # Optional: your app name
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 2000,
                },
                timeout=60,
            )

            response.raise_for_status()
            result = response.json()

            # Extract answer
            answer = result["choices"][0]["message"]["content"]
            return answer

        except requests.exceptions.RequestException as e:
            error_msg = f"Error calling OpenRouter API: {str(e)}"
            if hasattr(e.response, "text"):
                error_msg += f"\nResponse: {e.response.text}"
            raise Exception(error_msg)

    def _format_context(self, context_docs: List[Dict]) -> str:
        """
        Format retrieved documents into context string

        Args:
            context_docs: List of document dictionaries

        Returns:
            Formatted context string
        """
        if not context_docs:
            return "No relevant context found."

        formatted_parts = []
        for i, doc in enumerate(context_docs, 1):
            source = doc["metadata"]["source"]
            content = doc["content"]
            formatted_parts.append(f"[Source {i}: {source}]\n{content}\n")

        return "\n---\n".join(formatted_parts)

    async def generate_answer_streaming(
        self, query: str, context_docs: List[Dict], system_prompt: Optional[str] = None
    ):
        """
        Generate answer with streaming (for future use)

        Args:
            query: User's question
            context_docs: Retrieved documents
            system_prompt: Optional custom system prompt

        Yields:
            Chunks of the generated answer
        """
        # This can be implemented later for streaming responses
        # OpenRouter supports streaming with stream=True parameter
        pass
