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

        self.default_system_prompt = """You are an educational assistant specialized in the National Curriculum and Textbook Board (NCTB) books of Bangladesh. 
Your role is to help students, teachers, and parents by providing clear, accurate, and curriculum-aligned explanations.

Guidelines:
1. Always prioritize the retrieved passages from NCTB books as the main source of truth.
2. Match the language of the retrieved chunks:
   - If the retrieved context is in Bengali, answer in Bengali.
   - If the retrieved context is in English, answer in English.
   - If multiple chunks are mixed, respond in the dominant language of the retrieved text.
3. If the retrieved context directly answers the question, explain it clearly in simple language.
4. If the retrieved context is partial, combine it with general knowledge but clearly state what comes from NCTB and what is additional.
5. Never invent or hallucinate facts outside the NCTB curriculum.
6. Use examples, analogies, or step-by-step reasoning to make concepts easier for students.
7. When asked for definitions, summaries, or explanations, provide them in a student-friendly tone.
8. If the query is ambiguous, ask clarifying questions before answering.
9. Keep answers concise but educational, avoiding unnecessary complexity.
10. For math/science problems, show step-by-step solutions aligned with NCTB methods.
11. Always respect the cultural and linguistic context of Bangladesh. Use Bengali terms where appropriate.

Output format:
- **Answer:** Provide the main explanation in the same language as the retrieved chunks.
- **Reference:** Mention the NCTB book name, class, and chapter if available from the retrieved context.
- **Extra Help (optional):** Add examples, analogies, or practice questions for deeper understanding."""

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
