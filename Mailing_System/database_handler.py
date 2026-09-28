from pymongo import MongoClient, DESCENDING  # type: ignore
from datetime import datetime
from bson import ObjectId  # type: ignore
import requests
from bs4 import BeautifulSoup  # type: ignore

class DatabaseHandler:
    def __init__(self, uri="mongodb://localhost:27017/", db_name="genai_news_mailer"):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]

        self.youtube = self.db['youtube']
        self.serp = self.db['serp']
        self.genai_news = self.db['genai_news']
        
        self.sent_articles = self.db["sent_articles"]

        # Indexes
        self.youtube.create_index([("date", DESCENDING), ("title", DESCENDING)])
        self.serp.create_index([("date", DESCENDING), ("title", DESCENDING)])
        self.genai_news.create_index([("date", DESCENDING), ("title", DESCENDING)])

    def format_date(self, date):
        try:
            if '.' in date:
                return datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f").strftime("%Y-%m-%d")
            elif date.endswith('Z'):
                return datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d")
            else:
                return datetime.strptime(date, "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d")
        except ValueError as e:
            print(f"[DatabaseHandler] Error parsing date: {date} - {e}")
            return None

    # ----------------------------------------
    # Insert methods
    # ----------------------------------------
    def insert_youtube(self, title, url, date, transcript, concise_summary, detailed_summary):
        formatted_date = self.format_date(date)
        if not formatted_date:
            return
        self.youtube.insert_one({
            "title": title,
            "url": url,
            "date": formatted_date,
            "transcript": transcript,
            "concise_summary": concise_summary,
            "detailed_summary": detailed_summary,
            "is_genai_related": None,  # will be updated later
            "image": ""
        })

    def insert_serp(self, title, url, date, snippet, concise_summary, detailed_summary, image=""):
        formatted_date = self.format_date(date)
        if not formatted_date:
            return
        self.serp.insert_one({
            "title": title,
            "url": url,
            "date": formatted_date,
            "snippet": snippet,
            "concise_summary": concise_summary,
            "detailed_summary": detailed_summary,
            "is_genai_related": None,
            "image": image
        })
        
    def insert_genai_news(self, title, url, date, category, concise_summary, detailed_summary, image=""):
        formatted_date = self.format_date(date)
        if not formatted_date:
            return
        self.genai_news.insert_one({
            "title": title,
            "url": url,
            "date": formatted_date,
            "category": category,
            "concise_summary": concise_summary,
            "detailed_summary": detailed_summary,
            "is_genai_related": None,
            "image": image
        })

    # ----------------------------------------
    # Fetch methods for summarization
    # ----------------------------------------
    def fetch_unsummarized_news(self):
        return list(self.genai_news.find({
            "$or": [
                {"concise_summary": {"$exists": False}},
                {"concise_summary": "Concise summary placeholder"},
                {"detailed_summary": {"$exists": False}},
                {"detailed_summary": "Detailed summary placeholder"}
            ],
            "is_genai_related": True  # Only get relevant items
        }))

    def fetch_unsummarized_youtube(self):
        return list(self.youtube.find({
            "$or": [
                {"concise_summary": {"$exists": False}},
                {"concise_summary": "Concise transcript summary placeholder"},
                {"detailed_summary": {"$exists": False}},
                {"detailed_summary": "detailed transcript summary placeholder"}
            ],
            "is_genai_related": True
        }))

    def fetch_unsummarized_serp(self):
        return list(self.serp.find({
            "$or": [
                {"concise_summary": {"$exists": False}},
                {"concise_summary": "Concise SERP summary placeholder"},
                {"detailed_summary": {"$exists": False}},
                {"detailed_summary": "Detailed SERP summary placeholder"}
            ],
            "is_genai_related": True
        }))

    # ----------------------------------------
    # Update methods
    # ----------------------------------------
    def update_news(self, news_id, concise_summary, detailed_summary):
        self.genai_news.update_one(
            {"_id": ObjectId(news_id)},
            {"$set": {
                "concise_summary": concise_summary,
                "detailed_summary": detailed_summary
            }}
        )
        
    def update_youtube(self, video_id, transcript, concise_summary, detailed_summary):
        self.youtube.update_one(
            {"_id": ObjectId(video_id)},
            {"$set": {
                "transcript": transcript,
                "concise_summary": concise_summary,
                "detailed_summary": detailed_summary
            }}
        )

    def update_serp(self, serp_id, concise_summary, detailed_summary):
        self.serp.update_one(
            {"_id": ObjectId(serp_id)},
            {"$set": {
                "concise_summary": concise_summary,
                "detailed_summary": detailed_summary
            }}
        )

    def update_thumbnail(self):
        default_image = "https://via.placeholder.com/300"
        articles_genai = list(self.genai_news.find({
            "$or": [
                {"image": {"$exists": False}},
                {"image": None},
                {"image": ""}
            ]
        }))

        for article in articles_genai:
            thumbnail = self.fetch_thumbnail(article['url']) or default_image
            self.genai_news.update_one(
                {"_id": article["_id"]},
                {"$set": {"image": thumbnail}}
            )
            print(f"Updated genai_news article: {article['title']} with image: {thumbnail}")

        articles_serp = list(self.serp.find({
            "$or": [
                {"image": {"$exists": False}},
                {"image": None},
                {"image": ""}
            ]
        }))

        for article in articles_serp:
            thumbnail = self.fetch_thumbnail(article['url']) or default_image
            self.serp.update_one(
                {"_id": article["_id"]},
                {"$set": {"image": thumbnail}}
            )
            print(f"Updated serp article: {article['title']} with image: {thumbnail}")

    def ensure_image_field(self):
        self.genai_news.update_many(
            {"image": {"$exists": False}},
            {"$set": {"image": ""}}
        )
        self.serp.update_many(
            {"image": {"$exists": False}},
            {"$set": {"image": ""}}
        )

    # ----------------------------------------
    # Relevance updates
    # ----------------------------------------
    def set_relevance_in_collection(self, collection_name, doc_id, is_relevant):
        """
        Update is_genai_related field in the specified collection.
        collection_name can be 'genai_news', 'serp', or 'youtube'
        """
        collection = getattr(self.db, collection_name)
        collection.update_one(
            {"_id": ObjectId(doc_id)},
            {"$set": {"is_genai_related": is_relevant}}
        )

    def fetch_unclassified_docs(self, collection_name):
        """
        Return all documents where 'is_genai_related' is None
        """
        collection = getattr(self.db, collection_name)
        return list(collection.find({"is_genai_related": None}))

    # ----------------------------------------
    # Misc
    # ----------------------------------------
    def fetch_thumbnail(self, url):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            og_image = soup.find("meta", property="og:image")
            if og_image and og_image.get("content"):
                return og_image.get("content")
            img_tag = soup.find("img")
            if img_tag and img_tag.get("src"):
                return img_tag.get("src")
        except Exception as e:
            print(f"[DatabaseHandler] Error fetching thumbnail from {url}: {e}")
        return None

    def is_duplicate(self, title, url, collection_name):
        collection = getattr(self.db, collection_name)
        query = {"$or": [{"title": title}, {"url": url}]}
        return collection.count_documents(query) > 0

    def close_connection(self):
        self.client.close()
