import os
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
import time
import requests

class RelevanceClassifier:
    """
    Uses an LLM (Groq or other) to determine if a given piece of text
    is related to the GenAI persona (Generative AI, ChatGPT, OpenAI, LLMs, etc.).
    """
    def __init__(self, groq_api_key):
        self.groq_api_key = groq_api_key
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.retry_attempts = 5

    def is_genai_related(self, text):
        """
        Returns True if the text is relevant to Generative AI or modern AI 
        technologies (e.g., AI, ChatGPT, OpenAI, LLMs), False otherwise.
        """

        # Refined prompt
        prompt = (
            "You are a classifier checking if a piece of text is relevant to a 'GenAI persona'.\n"
            "The 'GenAI persona' covers topics like Generative AI, ChatGPT, OpenAI, large language models, "
            "and similarly modern AI advances or breakthroughs.\n\n"
            "If the text explicitly or implicitly references advanced AI, chatGPT, openAI, LLMs, or modern AI tech, "
            "respond with 'true'. Otherwise, respond with 'false'.\n\n"
            "Provide ONLY the word 'true' or 'false'.\n\n"
            f"Text: {text}"
        )

        payload = {
            "model": GROQ_MODEL,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }

        for attempt in range(self.retry_attempts):
            try:
                response = requests.post(self.base_url, json=payload, headers=headers)
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 5))
                    print(f"[RelevanceClassifier] Rate limit hit. Retrying after {retry_after} seconds...")
                    time.sleep(retry_after)
                    continue

                response.raise_for_status()
                data = response.json()
                classification = data.get("choices", [{}])[0] \
                                    .get("message", {}) \
                                    .get("content", "") \
                                    .strip() \
                                    .lower()
                return "true" in classification
            except requests.exceptions.RequestException as e:
                print(f"[RelevanceClassifier] Error calling Groq API: {e}")
                if attempt == self.retry_attempts - 1:
                    return False
                time.sleep(2 ** attempt)
        
        return False

    def is_valid_summary(summary: str) -> bool:
    # Return true only if it’s not empty and not our fallback
        if not summary:
            return False
        return summary.lower() != "no summary available"

