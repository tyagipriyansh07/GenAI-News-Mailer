import os
from datetime import datetime
from dotenv import load_dotenv
from database_handler import DatabaseHandler
from news_fetcher import NewsFetcher
from content_writer import ContentWriter
from relevance_classifier import RelevanceClassifier

# ----------------------------
#  Configuration / Constants
# ----------------------------
load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")

def main():
    db_handler = DatabaseHandler()
    news_fetcher = NewsFetcher(api_key=NEWS_API_KEY, db_handler=db_handler)
    content_writer = ContentWriter(
        groq_api_key=GROQ_API_KEY,
        youtube_api_key=YOUTUBE_API_KEY,
        db_handler=db_handler
    )
    relevance_classifier = RelevanceClassifier(groq_api_key=GROQ_API_KEY)

    print(f"[{datetime.now()}] Starting the News Mailer process...")

    # ------------------------------------------------
    # 1) Fetch fresh articles from your sources
    # ------------------------------------------------
    queries = [
        "OpenAI developments", "Google DeepMind research",
        "Anthropic AI", "Generative AI applications", "AI tools",
        "Generative AI trends", "AI-powered assistants", "GenAI breakthroughs"
    ]
    news_fetcher.fetch_news(queries, per_query_limit=5)
    # You could also fetch YouTube or SERP if you like

    # ------------------------------------------------
    # 2) Classify new docs for relevance
    # ------------------------------------------------
    unclassified = db_handler.fetch_unclassified_docs("genai_news")
    for doc in unclassified:
        title_text = doc.get("title", "")
        is_relevant = relevance_classifier.is_genai_related(title_text)
        db_handler.set_relevance_in_collection("genai_news", doc["_id"], is_relevant)

    # ------------------------------------------------
    # 3) Summarize relevant docs
    # ------------------------------------------------
    content_writer.summarize_news()


    db_handler.close_connection()
    print(f"[{datetime.now()}] Completed mailing script.")

if __name__ == "__main__":
    main()
