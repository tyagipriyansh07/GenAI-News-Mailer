# backend/main.py

from fastapi import FastAPI, Depends, HTTPException, status, APIRouter, Request # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import bcrypt, secrets, uvicorn  # type: ignore
from pymongo import MongoClient # type: ignore
from bson.objectid import ObjectId # type: ignore
from datetime import datetime, timedelta
# from .social_auth import router as social_router
from random import shuffle
import os
from dotenv import load_dotenv # type: ignore

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")  # Gmail app password
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://localhost:5000").rstrip("/")

# Mailing system modules from the sibling folder "Mailing_System"
from Mailing_System.database_handler import DatabaseHandler
from Mailing_System.email_sender import EmailSender
from Mailing_System.template_builder import TemplateBuilder
from Mailing_System.relevance_classifier import RelevanceClassifier
from Mailing_System.content_writer import ContentWriter, convert_markdown_to_html
from fastapi.staticfiles import StaticFiles # type: ignore
from fastapi.responses import FileResponse # type: ignore
###################################################
# 1) FastAPI, CORS, and Mongo Setup
###################################################
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# include the social router from social_auth
# app.include_router(social_router)

client = MongoClient(MONGO_URI)
db = client["genai_news_mailer"]

users_coll = db["users"]
feedback_coll = db["user_feedback"]
sent_articles_coll = db["user_sent_articles"]
saved_coll = db["saved_articles"]
news_coll = db["genai_news"]

###################################################
# 2) Pydantic Models
###################################################
class SignUpModel(BaseModel):
    email: str
    password: str
    name: str

class LoginModel(BaseModel):
    email: str
    password: str

class ForgotPasswordModel(BaseModel):
    email: EmailStr

class ResetPasswordModel(BaseModel):
    token: str
    new_password: str
    
class PreferencesModel(BaseModel):
    name: Optional[str]
    content_format: Optional[str]
    delivery_frequency: Optional[str]
    delivery_time: Optional[str]
    topics: Optional[List[str]] = []   
    goals: Optional[List[str]] = []
    industry_trends: Optional[List[str]] = []
    competitors: Optional[List[str]] = []
    keywords: Optional[List[str]] = []

class FeedbackModel(BaseModel):
    email: str
    rating: int
    comment: str

###################################################
# 3) Utility Functions
###################################################
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.hashpw(password.encode("utf-8"), hashed.encode("utf-8")) == hashed.encode("utf-8")

def get_user_by_email(email: str):
    return users_coll.find_one({"email": email})

reset_tokens = {}

###################################################
# 4) Auth Routes
###################################################
@app.post("/auth/signup")
def sign_up(payload: SignUpModel):
    existing_user = get_user_by_email(payload.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already in use."
        )

    hashed = hash_password(payload.password)
    user_doc = {
        "email": payload.email,
        "hashed_password": hashed,
        "name": payload.name,
        "preferences": {
            "topics": [],
            "frequency": None,
            "content_format": None,
            "delivery_time": None
        },
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    result = users_coll.insert_one(user_doc)
    return {"success": True, "user_id": str(result.inserted_id)}

@app.post("/auth/login")
def login(payload: LoginModel):
    user_doc = get_user_by_email(payload.email)
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials."
        )
    if not verify_password(payload.password, user_doc["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials."
        )
    return {
        "success": True,
        "user_id": str(user_doc["_id"]),
        "name": user_doc.get("name", ""),
        "email": user_doc["email"], 
    }

@app.post("/auth/forgot_password")
def forgot_password(payload: ForgotPasswordModel):
    user_doc = users_coll.find_one({"email": payload.email})
    if not user_doc:
        raise HTTPException(status_code=404, detail="Email not found")

    token = secrets.token_urlsafe(32)
    reset_tokens[token] = {
        "user_id": str(user_doc["_id"]),
        "expires": datetime.utcnow() + timedelta(hours=1)
    }

    reset_link = f"{PUBLIC_BASE_URL}/reset?token={token}"

    # Example: if you have an EmailSender class (adapt to whatever you're using)

    email_sender = EmailSender(sender_email=SENDER_EMAIL,
                               sender_password=SENDER_PASSWORD)
    subject = "Reset your password"
    content = f"""
    Hello,

    You requested a password reset. Click the link below to reset your password:
    {reset_link}

    This link is valid for 1 hour.

    If you didn't request a password reset, you can ignore this email.
    """

    # Send the reset link via email
    email_sender.send_email(
        recipient_email=payload.email,
        subject=subject,
        content=content
    )

    return {"success": True, "message": "Reset link emailed"}

@app.post("/auth/reset_password")
def reset_password(payload: ResetPasswordModel):
    data = reset_tokens.get(payload.token)
    if not data:
        raise HTTPException(status_code=400, detail="Invalid token")
    if datetime.utcnow() > data["expires"]:
        raise HTTPException(status_code=400, detail="Token expired")

    user_id = data["user_id"]

    # >>> Instead of 'somehashedvalue', do this:
    #     hashed = hash_password(payload.new_password)
    hashed = hash_password(payload.new_password)

    users_coll.update_one({"_id": ObjectId(user_id)}, {"$set": {"hashed_password": hashed}})

    # You can also remove the token from your dictionary once done:
    del reset_tokens[payload.token]

    return {"success": True, "message": "Password reset successful"}

###################################################
# 5) Preferences Routes
###################################################
@app.get("/preferences")
def get_preferences(user_email: str):
    user_doc = users_coll.find_one({"email": user_email})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "success": True,
        "preferences": user_doc.get("preferences", {}),
        "name": user_doc.get("name", "")
    }

@app.post("/preferences")
def update_preferences(user_email: str, prefs: PreferencesModel):
    user_doc = users_coll.find_one({"email": user_email})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")

    updated_prefs = user_doc.get("preferences", {})

    if prefs.name:
        user_doc["name"] = prefs.name
    if prefs.content_format:
        updated_prefs["content_format"] = prefs.content_format
    if prefs.delivery_frequency:
        updated_prefs["frequency"] = prefs.delivery_frequency
    if prefs.delivery_time:
        updated_prefs["delivery_time"] = prefs.delivery_time
    if prefs.topics is not None:
        updated_prefs["topics"] = prefs.topics
    if prefs.goals is not None:
        updated_prefs["goals"] = prefs.goals
    if prefs.industry_trends is not None:
        updated_prefs["industry_trends"] = prefs.industry_trends
    if prefs.competitors is not None:
        updated_prefs["competitors"] = prefs.competitors
    if prefs.keywords is not None:
        updated_prefs["keywords"] = prefs.keywords

    user_doc["preferences"] = updated_prefs
    user_doc["updated_at"] = datetime.utcnow()

    users_coll.replace_one({"_id": user_doc["_id"]}, user_doc)
    return {"success": True}

###################################################
# 7) Saved Articles
###################################################
@app.get("/articles/saved")
def get_saved_articles(user_email: str):
    saved_docs = list(saved_coll.find({"user_email": user_email}))
    if not saved_docs:
        return {"success": True, "articles": []}

    articles_data = []
    for doc in saved_docs:
        article_doc = news_coll.find_one({"_id": ObjectId(doc["article_id"])})
        if article_doc:
            articles_data.append({
                "id": str(article_doc["_id"]),
                "title": article_doc.get("title", "Untitled"),
                "summary": article_doc.get("concise_summary", ""),
                "date": article_doc.get("date", ""),
                "image": article_doc.get("image", ""),
                "url": article_doc.get("url", "") 
            })
    return {"success": True, "articles": articles_data}

@app.post("/articles/save")
def save_article(user_email: str, article_id: str):
    # Validate article_id format
    try:
        art_oid = ObjectId(article_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid article_id format")

    # Find user_id using email
    users_coll = db["users"]
    user = users_coll.find_one({"email": user_email})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_oid = user["_id"]  # Get user ObjectId

    # Check if article is already saved
    saved_articles_coll = db["saved_articles"]
    existing = saved_articles_coll.find_one({"user_id": user_oid, "article_id": art_oid})

    if existing:
        return {"success": True, "message": "Article already saved."}

    # Save article
    saved_articles_coll.insert_one({
        "user_id": user_oid,
        "user_email": user_email,  # Store email
        "article_id": art_oid,
        "saved_at": datetime.utcnow()
    })

    return {"success": True, "message": "Article saved successfully!"}

@app.get("/articles/save_legacy")
def save_article_legacy(
    user_id: Optional[str] = None,
    article_id: Optional[str] = None,
    email: Optional[str] = None
):
    """
    This replicates the old Flask code that uses query params:
      ?user_id=...&article_id=...&email=...
    Saves an article in 'saved_articles' based on user_id / user_email.
    """

    if not user_id or not article_id:
        # Return a 400 if missing user_id or article_id
        raise HTTPException(status_code=400, detail="Missing user_id or article_id")

    # Try to convert user_id and article_id to ObjectId
    try:
        user_obj_id = ObjectId(user_id)
        article_obj_id = ObjectId(article_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid user_id or article_id format")

    # If email wasn't provided, we look up the user by _id
    if not email:
        user = users_coll.find_one({"_id": user_obj_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        email = user.get("email", "Unknown")

    # Insert into 'saved_articles'
    existing = saved_coll.find_one({
        "user_id": user_obj_id,
        "article_id": article_obj_id
    })
    if existing:
        return {"success": True, "message": "Article already saved!"}

    saved_coll.insert_one({
        "user_id": user_obj_id,
        "user_email": email,  # store the final email
        "article_id": article_obj_id,
        "saved_at": datetime.utcnow()
    })
    return {"success": True, "message": "Article saved successfully!"}

###################################################
# 8) Feedback Route
###################################################
@app.post("/feedback")
def submit_feedback(data: FeedbackModel):
    user_doc = users_coll.find_one({"email": data.email})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    
    feedback_doc = {
        "user_email": data.email,
        "rating": data.rating,
        "comments": data.comment,
        "timestamp": datetime.utcnow(),
        "source": "dashboard"
    }
    feedback_coll.insert_one(feedback_doc)
    return {"success": True, "message": "Feedback received"}

@app.get("/feedback/email_rate")
def email_rate(request: Request, rating: int, user_email: str, articles: Optional[str] = None):
    """
    Handle 1-click star rating from the email.
    Example usage in the email:
       /feedback/email_rate?rating=3&user_email=some@domain.com&articles=abc123,def456

    We'll store:
      - user_email
      - rating
      - source = "email"
      - articles_sent = list of IDs if provided
      - timestamp
    """

    user_doc = users_coll.find_one({"email": user_email})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")

    articles_sent = []
    if articles:
        # articles param might be a comma-separated list of IDs
        articles_sent = articles.split(",")

    feedback_doc = {
        "user_email": user_email,
        "rating": rating,
        "comments": None,            # No text comment from a 1-click star
        "timestamp": datetime.utcnow(),
        "articles_sent": articles_sent,  # store the article IDs that were in this email
        "source": "email"           # Distinguish from dashboard feedback
    }

    feedback_coll.insert_one(feedback_doc)

    # Optional: redirect user to a "thank you" page or show a JSON response
    return {
        "success": True,
        "message": f"Email rating {rating} recorded for {user_email}, articles={articles_sent}"
    }

#####################################
#  SERVE THE FRONTEND BUILD
#####################################

# 1) Mount the React build static folder:
#    - This folder must exist, generated by `npm run build` in `frontend`
app.mount("/static", StaticFiles(directory="frontend/build/static"), name="static")
# 2) Serve files under build/images/ at /images
app.mount("/images", StaticFiles(directory="frontend/build/images"), name="images")
# 2) Root route → serve index.html
@app.get("/")
def serve_index():
    return FileResponse("frontend/build/index.html")

# 3) Catch-all for client-side routing
@app.get("/{full_path:path}")
def serve_spa(full_path: str):
    return FileResponse("frontend/build/index.html")


###################################################
# 9) Instant Send Route
###################################################
@app.post("/articles/send_now")
def send_now(user_email: str):
    user_doc = users_coll.find_one({"email": user_email})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    
    
    user_id = str(user_doc["_id"])


    db_handler = DatabaseHandler(uri=MONGO_URI, db_name="genai_news_mailer")
    email_sender = EmailSender(sender_email=SENDER_EMAIL,
                               sender_password=SENDER_PASSWORD)
    template_builder = TemplateBuilder()
    content_writer = ContentWriter(
        groq_api_key=GROQ_API_KEY,
        youtube_api_key=YOUTUBE_API_KEY,
        # base_url = "https://api.groq.com/openai/v1/chat/completions",
        db_handler=db_handler
    )
    # news_fetcher = NewsFetcher(api_key="YOUR_NEWS_API_KEY", db_handler=db_handler)
    # relevance_classifier = RelevanceClassifier(groq_api_key="YOUR_GROQ_KEY") 
    
    sent_article_ids = [
        str(article_id) for record in sent_articles_coll.find({"user_id": ObjectId(user_id)})
        for article_id in record.get("article_ids", [])
    ]


    # For "instant" demonstration, we might just pick existing relevant articles
    relevant_news = list(
        db_handler.genai_news.find({
            "is_genai_related": True,
            # "image": {"$exists": True, "$ne": ""},
            "_id": {"$nin": [ObjectId(article_id) for article_id in sent_article_ids]}
        }).sort("date", -1).limit(5)
    )
    if not relevant_news:
        return {"success": False, "message": "No valid summarized articles to send right now."}

    user_name = user_doc.get("name", "Valued Subscriber")
    user_email = user_doc["email"]
    relevant_news = [art for art in relevant_news if RelevanceClassifier.is_valid_summary(art.get("concise_summary", ""))]
    if not relevant_news:
        return {"success": False, "message": "No valid summarized articles to send right now."}

    shuffle(relevant_news)
    hero_article = relevant_news[0]

    raw_md_summary = hero_article.get('detailed_summary', '')
    hero_article['detailed_summary'] = convert_markdown_to_html(raw_md_summary)
    # hero_article['detailed_summary'] = content_writer.format_summary_with_ai(hero_article.get('detailed_summary', ''))
    top_stories = relevant_news[1:3]
    insights = relevant_news[3:5]
    
    tutorial_content = content_writer.generate_tutorial(topic="Multi-agent systems in AI")
    editorial_pov  = content_writer.generate_editorial_pov([hero_article] + top_stories + insights)
    
    feedback_url = f"{PUBLIC_BASE_URL}/feedback"
    email_html = template_builder.build_email(
        hero_article=hero_article,
        top_stories=top_stories,
        insights=insights,
        feedback_url=feedback_url,
        recipient_email=user_email,
        tutorial_content=tutorial_content,
        recipient_name=user_name,
        user_id=str(user_id),
        editorial_pov=editorial_pov
    )

    email_sender.send_email(
        recipient_email=user_email,
        subject="Your Instant Generative AI Update",
        content=email_html
    )

    # log in user_sent_articles
    db["user_sent_articles"].insert_one({
        "user_id": ObjectId(user_id),
        "article_ids": [art["_id"] for art in relevant_news],
        "collection_type": "genai_news",
        "date_sent": datetime.utcnow(),
        "email_id": user_email,
        "opened_timestamp": None,
        "clicked_timestamp": None
    })

    db_handler.close_connection()

    return {"success": True, "message": f"Email sent to {user_email} instantly"}

###################################################
# 10) Run the App
###################################################
if __name__ == "__main__":
    # IMPORTANT: specify "backend.main:app"
    uvicorn.run("backend.main:app", host="0.0.0.0", port=5000, reload=True)
