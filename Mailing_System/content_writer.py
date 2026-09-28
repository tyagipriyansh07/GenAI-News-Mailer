import os
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
import time
import requests
import re
class ContentWriter:
    def __init__(self, groq_api_key, youtube_api_key, db_handler):
        self.groq_api_key = groq_api_key
        self.youtube_api_key = youtube_api_key
        self.db_handler = db_handler
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.retry_attempts = 5


    def generate_summary(self, text, summary_type):
        prompt = ""
        if summary_type == 'concise':
            prompt = f"Summarize this content in under 50 words:\n{text}"
        elif summary_type == 'detailed':
            prompt = (
                "Summarize the content in a detailed format:\n"
                "1. A short paragraph summarizing the content.\n"
                "2. 3-4 Key insights in bullet points.\n\n"
                f"Content:\n{text}"
            )

        payload = {
            "model": GROQ_MODEL,
            "messages": [{"role": "user", "content": prompt}]
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
                    print(f"[ContentWriter] Rate limit hit. Retrying after {retry_after} seconds...")
                    time.sleep(retry_after)
                    continue
                response.raise_for_status()
                data = response.json()
                summary = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                if "sorry" in summary.lower() or "i apologize" in summary.lower() or "no content" in summary.lower():
                    summary = "No summary available"
                return summary
            
            
            except requests.exceptions.RequestException as e:
                print(f"[ContentWriter] Error during Groq API call: {e}")
                if attempt == self.retry_attempts - 1:
                    return "No summary available."
                time.sleep(2 ** attempt)
        return "No summary available."

    def summarize_news(self, limit=None):
        unsummarized_news = self.db_handler.fetch_unsummarized_news()
        if limit:
            unsummarized_news = unsummarized_news[:limit]
            print(f"[ContentWriter] Summarizing {len(unsummarized_news)} news articles.")

        for genai_news in unsummarized_news:
            concise_summary = self.generate_summary(genai_news['title'], 'concise')
            detailed_summary = self.generate_summary(genai_news['title'], 'detailed')
            self.db_handler.update_news(genai_news['_id'], concise_summary, detailed_summary)
 
    
    def generate_tutorial(self, topic="multi-agent systems in AI"):
        """
        Generates a short tutorial for the given topic using an LLM (Groq).
        """
        prompt = f"""
    You are an AI that writes concise educational tutorials in HTML.
    Please create a short, step-by-step tutorial on the following topic:
    '{topic}'

    Requirements:
    1. Use a friendly, instructive tone suitable for newsletter readers.
    2. Structure your tutorial with simple HTML tags, such as <h3> or <h4> for each step, 
       and <ul><li> for bullet points if needed.
    3. Provide a brief "learning roadmap" or "step by step" guide.
    4. Include 2-3 relevant links or resources at the end.
    5. Limit the tutorial to a few paragraphs total, avoiding excessive length.

    Return ONLY valid HTML (no Markdown or LaTeX). 
    """

        payload = {
            "model": GROQ_MODEL,
            "messages": [{"role": "user", "content": prompt}]
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
                    print(f"[TutorialGenerator] Rate limit hit. Retrying after {retry_after} seconds...")
                    time.sleep(retry_after)
                    continue
                
                response.raise_for_status()
                data = response.json()
                tutorial_text = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                return tutorial_text
            except requests.exceptions.RequestException as e:
                print(f"[TutorialGenerator] Error during tutorial generation call: {e}")
                if attempt == self.retry_attempts - 1:
                    return "Failed to generate tutorial after multiple retries."
                time.sleep(2 ** attempt)

        return "No tutorial available."

        
    def generate_editorial_pov(self, articles):
        """
        Generates a cohesive editorial POV using insights from five articles in the email.
    
        :param articles: List of article objects (hero, top stories, insights)
        :return: Generated editorial POV as a string
        """

        if not articles or len(articles) < 3:
            return "Our perspective on this week’s AI advancements is currently unavailable."

    # Extract the summaries from articles
        summaries = "\n\n".join(
            [f"Title: {article['title']}\nSummary: {article.get('detailed_summary', 'No summary available')}" for article in articles]
        )

    # Define the prompt for the LLM
        prompt = f"""
        You are a senior AI analyst writing for a Generative AI newsletter.
        Your task is to generate a concise **"Editor's POV"** opinion piece, connecting themes from the following five articles.

        ### Articles:
        {summaries}

    ### Requirements:
        1. Identify **common themes** or **emerging trends** across these five articles.
        2. Provide **insightful analysis** about the implications of these trends in AI, business, or society.
        3. Offer a **thought-provoking conclusion**, possibly predicting future developments.
        4. Keep it **short and engaging (about 100-150 words).**
        5. Write in a **professional yet conversational tone**.

        **Output only the final generated text** without any formatting instructions.
        """

        payload = {
            "model": GROQ_MODEL,
            "messages": [{"role": "user", "content": prompt}]
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
                    print(f"[POV Generator] Rate limit hit. Retrying after {retry_after} seconds...")
                    time.sleep(retry_after)
                    continue
            
                response.raise_for_status()
                data = response.json()
                pov_text = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                return pov_text
            except requests.exceptions.RequestException as e:
                print(f"[POV Generator] Error: {e}")
                if attempt == self.retry_attempts - 1:
                    return "Failed to generate editorial POV after multiple retries."
                time.sleep(2 ** attempt)

        return "No editorial POV available at this time."
    


def convert_markdown_to_html(md_text: str) -> str:
        """
        Converts minimal markdown markers (like **bold**, and lines starting with '* ')
        into HTML tags.
        """
        if not md_text:
            return ""

        # 1. Convert '**text**' to '<strong>text</strong>'
        md_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', md_text)

        # 2. Convert lines that start with '* ' into <ul><li>...</li></ul> structure
        lines = md_text.split('\n')
        new_lines = []
        in_list = False

        for line in lines:
            stripped = line.strip()
            if stripped.startswith('* '):
                # If we're not already in a list, start one
                if not in_list:
                    new_lines.append('<ul>')
                    in_list = True
                # Remove '* ' from the start
                content = stripped[2:].strip()
                new_lines.append(f'<li>{content}</li>')
            else:
                # If we were in a list, close it
                if in_list:
                    new_lines.append('</ul>')
                    in_list = False
                # Put normal lines in <p> tags
                new_lines.append(f'<p>{line}</p>')

        # If ended while still in a list, close it
        if in_list:
            new_lines.append('</ul>')

        return '\n'.join(new_lines)

   