import os
from typing import Optional, List

PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://localhost:5000").rstrip("/")
def get_safe_image(url: str, fallback: str) -> str:
    if not url:
        return fallback
    lower = url.lower()
        # If it ends with ".webp" or there's something that indicates a .webp
    if lower.endswith(".webp"):
            # Return your known-safe fallback (e.g., JPG or PNG).
        return fallback
       # Otherwise return the original
    return url

class TemplateBuilder:
    @staticmethod
    def build_email(
        hero_article,
        top_stories,
        insights,
        feedback_url, 
        recipient_email,
        tutorial_content=None,
        recipient_name='recipient_email',
        editorial_pov=None,
        user_id=None  
    ):
        """
        Builds the HTML email with:
         - Greeting
         - Hero article
         - Top Stories
         - Market Pulse
         - Industry Insights
         - Editor's POV
         - Tutorial
         - Footer with star rating
        """

        # Fallback image
        placeholder_image = "https://i.ibb.co/3yB7gQN7/thumb.jpg"
        
        # Bookmark icon
        bookmark_icon_url = "https://i.ibb.co/r2jTS83m/bookmark-filled.png"

        # Gather article IDs to pass to the footer (so we can store them in user_feedback when user rates)
        article_ids = []
        def safe_id(item):
            return str(item["_id"]) if item and "_id" in item else ""

        # hero
        hero_id = safe_id(hero_article)
        if hero_id:
            article_ids.append(hero_id)

        # top stories
        for art in top_stories:
            art_id = safe_id(art)
            if art_id:
                article_ids.append(art_id)

        # insights
        for ins in insights:
            ins_id = safe_id(ins)
            if ins_id:
                article_ids.append(ins_id)

        # Hero article image or placeholder
        hero_image = get_safe_image(
            hero_article.get('image'),
            placeholder_image
        )


        # Start email
        email_content = f"""
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 0;
            background-color: #f9f9f9;
        }}
        .container {{
            max-width: 700px;
            margin: 20px auto;
            padding: 20px;
            background-color: #ffffff;
            border-radius: 8px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        }}
        .header {{
            background-color: #1A73E8;
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 8px 8px 0 0;
        }}
        .hero {{
            text-align: center;
            margin: 20px 0;
        }}
        .hero img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
        }}
        .hero h1 {{
            font-size: 24px;
            color: #333;
            margin-top: 10px;
        }}
        .hero p {{
            font-size: 14px;
            color: #555;
            margin: 10px 0;
        }}
        .section-title {{
            color: #1A73E8;
            font-size: 22px;
            margin: 20px 0 10px;
            border-bottom: 2px solid #1A73E8;
            padding-bottom: 5px;
        }}
        .article {{
            display: flex;
            margin-bottom: 20px;
            border-bottom: 1px solid #ddd;
            padding-bottom: 10px;
        }}
        .article img {{
            max-width: 120px;
            height: auto;
            border-radius: 8px;
            margin-right: 15px;
        }}
        .article-details {{
            flex: 1;
        }}
        .article-title-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .article-details h3 {{
            font-size: 18px;
            color: #333;
            margin: 0;
        }}
        .article-details p {{
            font-size: 14px;
            color: #666;
            margin: 5px 0;
        }}
        .bookmark-icon {{
            width: 24px;
            height: 24px;
            margin-left: 8px;
            vertical-align: middle;
            cursor: pointer;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>Your Weekly Generative AI Update</h1>
        </div>

        <!-- Hero + Greeting -->
        <div class="hero">
            <h2>Hi {recipient_name},</h2>
            <img src="{hero_image}" alt="Hero Image">
            <div class="article-title-row">
                <h1>{hero_article['title']}</h1>
                <a href="{PUBLIC_BASE_URL}/articles/save_legacy?user_id={user_id}&article_id={hero_id}&email={recipient_email}"
                   style="text-decoration:none;">
                    <img src="{bookmark_icon_url}" alt="Bookmark" class="bookmark-icon">
                </a>
            </div>
            <p>Published on {hero_article.get('date', 'No Date Available')}</p>
            <div style="text-align: justify; margin-top: 10px;">
    {hero_article.get('detailed_summary', 'No summary')}
</div>
            <a href="{hero_article.get('url', '#')}">Read More →</a>
        </div>

        <!-- Top Stories -->
        <h2 class="section-title">Top Stories</h2>
"""
        # Build top stories
        for art in top_stories:
            raw_img = get_safe_image(art.get('image'), placeholder_image)            
            art_id = safe_id(art)
            email_content += f"""
        <div class="article">
            <img src="{raw_img}" alt="Thumbnail">
            <div class="article-details">
                <div class="article-title-row">
                    <h3>{art['title']}</h3>
                    <a href="{PUBLIC_BASE_URL}/articles/save_legacy?user_id={user_id}&article_id={art_id}&email={recipient_email}"
                       style="text-decoration:none;">
                        <img src="{bookmark_icon_url}" alt="Bookmark" class="bookmark-icon">
                    </a>
                </div>
                <p>Published on {art.get('date', 'No Date Available')}</p>
                <p>{art.get('concise_summary', 'No concise summary available')}</p>
                <a href="{art.get('url', '#')}">Read more →</a>
            </div>
        </div>
"""

        # Industry Insights
        email_content += """
        <h2 class="section-title">Industry Insights</h2>
"""
        for ins in insights:
            raw_img = get_safe_image(ins.get('image'), placeholder_image)
            ins_id = safe_id(ins)
            email_content += f"""
        <div class="article">
            <img src="{raw_img}" alt="Thumbnail">
            <div class="article-details">
                <div class="article-title-row">
                    <h3>{ins['title']}</h3>
                    <a href="{PUBLIC_BASE_URL}/articles/save_legacy?user_id={user_id}&article_id={ins_id}&email={recipient_email}"
                       style="text-decoration:none;">
                        <img src="{bookmark_icon_url}" alt="Bookmark" class="bookmark-icon">
                    </a>
                </div>
                <p>Published on {ins.get('date', 'No Date Available')}</p>
                <p>{ins.get('concise_summary', 'No concise summary available')}</p>
                <a href="{ins.get('url', '#')}">Read more →</a>
            </div>
        </div>
"""

        # Editor's POV
        if editorial_pov:
            email_content += f"""
        <h2 class="section-title">Editor's point of view</h2>
        <div style="margin-bottom:20px; font-size: 14px">
            {editorial_pov}
        </div>
"""

        # Tutorial
        if tutorial_content:
            email_content += f"""
        <h2 class="section-title">Tutorial: Multi-Agent Systems</h2>
        <div style="margin-bottom:20px;">
            {tutorial_content}
        </div>
"""

        # ******* FOOTER *******
        footer_html = build_footer_email_rating(
            feedback_base_url=feedback_url, 
            user_email=recipient_email, 
            article_ids=article_ids
        )
        email_content += footer_html

        email_content += """
    </div> <!-- end container -->
</body>
</html>
"""
        return email_content



def build_footer_email_rating(feedback_base_url: str, user_email: str, article_ids: Optional[List[str]] = None):
    """
    Builds the dynamic footer including:
      - 5-star rating links to /feedback/email_rate?rating=?&user_email=?...
      - Two buttons (Update Preferences, Visit Dashboard)
      - Some "Lorem ipsum" text
      - Footer links
    """
    # article_ids might be None or empty
    joined_articles = ",".join(article_ids) if article_ids else ""

    stars_html = ""
    for rating_value in range(1, 6):
        star_link = (
            f"{feedback_base_url}/email_rate"
            f"?rating={rating_value}&user_email={user_email}"
        )
        if joined_articles:
            star_link += f"&articles={joined_articles}"

        stars_html += f"""
          <a href="{star_link}"
             style="text-decoration:none; font-size:28px; color:#ffa500; margin:0 4px;">
              ★
          </a>
        """

    return f"""
    <div style="text-align:center; margin-top:50px;">
        <h3 style="font-weight:bold; color:#333;">Rate Your Reading Experience</h3>
        <div style="margin-bottom:20px;">
            {stars_html}
        </div>

        <div style="display:inline-block;">
            <a href="{PUBLIC_BASE_URL}/preferencespage?user_email={user_email}"
               style="display:inline-block; margin:0 10px; padding:12px 20px; border:1px solid #ccc; border-radius:5px; background:#f5f5f5; color:#333; text-decoration:none;">
                Update Preferences
            </a>
            <a href="{PUBLIC_BASE_URL}/dashboard?user_email={user_email}"
               style="display:inline-block; margin:0 10px; padding:12px 20px; border:1px solid #ccc; border-radius:5px; background:#f5f5f5; color:#333; text-decoration:none;">
                Visit Your Dashboard
            </a>
        </div>

        <div style="margin-top:30px; color:#999; font-size:14px; line-height:1.4; max-width:600px; margin-left:auto; margin-right:auto;">
            <p style="margin:0;">
                © 2025 GenAI News Mailer
            </p>

            <p style="margin:0; color:#777;">
                <a href="#" style="color:#1A73E8; text-decoration:none;">Privacy policy</a> •
                <a href="#" style="color:#1A73E8; text-decoration:none;">Terms of service</a> •
                <a href="#" style="color:#1A73E8; text-decoration:none;">Help center</a> •
                <a href="#" style="color:#1A73E8; text-decoration:none;">Unsubscribe</a>
            </p>
        </div>
    </div>
    """