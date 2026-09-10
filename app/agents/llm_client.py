import json
import os
from typing import Dict, Any, Optional
from app.config import settings

# Ordered priority list of models to try
GEMINI_MODELS = [
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash-lite",
    "gemini-2.5-flash-lite"
]

class LLMClient:
    @property
    def provider(self) -> str:
        return settings.llm_provider.lower()

    @property
    def gemini_key(self) -> str:
        return settings.gemini_api_key

    @property
    def openai_key(self) -> str:
        return settings.openai_api_key

    def _get_gemini_client(self):
        if hasattr(self, '_cached_client') and self._cached_client:
            return self._cached_client
        from google import genai
        import tenacity
        client = genai.Client(api_key=self.gemini_key)
        try:
            if hasattr(client._api_client, '_retry'):
                client._api_client._retry.stop = tenacity.stop_after_attempt(1)
        except Exception:
            pass
        self._cached_client = client
        return client

    def generate_json(self, system_prompt: str, user_prompt: str) -> Optional[Dict[str, Any]]:
        """
        Attempts to query the configured LLM API (Gemini or OpenAI).
        If provider is 'mock' or API call fails, returns None so caller can fallback to rule-based response.
        """
        if self.provider == "gemini" and self.gemini_key:
            client = self._get_gemini_client()
            prompt = f"{system_prompt}\n\nUser Message:\n{user_prompt}\n\nReturn JSON ONLY. Do not wrap in markdown code blocks."

            for model_name in GEMINI_MODELS:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt
                    )
                    text = response.text
                    clean_text = self._extract_json_text(text)
                    return json.loads(clean_text)
                except Exception as e:
                    print(f"[LLMClient] Gemini JSON call error on {model_name}: {e}")
                    continue

        elif self.provider == "openai" and self.openai_key:
            try:
                import openai
                client = openai.OpenAI(api_key=self.openai_key)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                text = response.choices[0].message.content
                return json.loads(text)
            except Exception as e:
                print(f"[LLMClient] OpenAI API call error: {e}")

        return None

    def generate_text(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        if self.provider == "gemini" and self.gemini_key:
            client = self._get_gemini_client()
            prompt = f"{system_prompt}\n\n{user_prompt}"

            for model_name in GEMINI_MODELS:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt
                    )
                    if response.text and response.text.strip():
                        return response.text.strip()
                except Exception as e:
                    print(f"[LLMClient] Gemini text call error on {model_name}: {e}")
                    continue

        elif self.provider == "openai" and self.openai_key:
            try:
                import openai
                client = openai.OpenAI(api_key=self.openai_key)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"[LLMClient] OpenAI text call error: {e}")
        return None

    def _extract_json_text(self, text: str) -> str:
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()

llm_client = LLMClient()
