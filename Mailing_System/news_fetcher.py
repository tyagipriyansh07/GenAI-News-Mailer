import requests
from datetime import datetime, timedelta

class NewsFetcher:
    def __init__(self, api_key, db_handler):
        self.api_key = api_key
        self.db_handler = db_handler
        
    def fetch_news(self, queries, per_query_limit=None):
        """
        Fetch news articles for given queries from NewsAPI.org
        """
        two_weeks_ago = datetime.now() - timedelta(weeks=2)
        total_fetched = 0
        query_results = {}

        for query in queries:
            page = 1
            query_fetched = 0
            while True:
                url = (
                    f'https://newsapi.org/v2/everything?q={query}&from={two_weeks_ago.date()}'
                    f'&sortBy=publishedAt&pageSize=100&page={page}&language=en&apiKey={self.api_key}'
                )
                response = requests.get(url).json()
                if response['status'] != 'ok' or not response.get('articles'):
                    break

                for article in response['articles']:
                    if per_query_limit and query_fetched >= per_query_limit:
                        break

                    date = datetime.strptime(article['publishedAt'], "%Y-%m-%dT%H:%M:%SZ")
                    if date >= two_weeks_ago:
                        title = article['title']
                        article_url = article['url']
                        image = article.get('urlToImage', '') 
                        concise_summary = "Concise summary placeholder"
                        detailed_summary = "Detailed summary placeholder"
                        category = query

                        if not self.db_handler.is_duplicate(title, article_url, 'genai_news'):
                            self.db_handler.insert_genai_news(
                                title, article_url, date.isoformat(), category,
                                concise_summary, detailed_summary, image
                            )
                            query_fetched += 1
                            total_fetched += 1
                
                if per_query_limit and query_fetched >= per_query_limit:
                    break
                page += 1
                
            query_results[query] = query_fetched
        return query_results, total_fetched

    # def fetch_youtube_videos(self, youtube_api_key, query, max_results=100):
    #     """
    #     Fetch YouTube videos by query
    #     """
    #     print("Starting the fetching process for YouTube")
    #     two_weeks_ago = datetime.now() - timedelta(weeks=2)
    #     url = (f"https://www.googleapis.com/youtube/v3/search?"
    #            f"part=snippet&q={query}&maxResults={max_results}&type=video&key={youtube_api_key}")
    #     total_results = 0
    #     next_page_token = None

    #     while total_results < max_results:
    #         paginated_url = url + (f"&pageToken={next_page_token}" if next_page_token else "")
    #         response = requests.get(paginated_url).json()

    #         if 'items' not in response:
    #             break

    #         for item in response.get('items', []):
    #             video_date = datetime.strptime(item['snippet']['publishedAt'], "%Y-%m-%dT%H:%M:%SZ")
    #             if video_date >= two_weeks_ago:
    #                 video_title = item['snippet']['title']
    #                 video_url = f"https://www.youtube.com/watch?v={item['id']['videoId']}"
    #                 transcript = None
    #                 concise_summary = "Concise transcript summary placeholder"
    #                 detailed_summary = "Detailed transcript summary placeholder"

    #                 if not self.db_handler.is_duplicate(video_title, video_url, 'youtube'):
    #                     self.db_handler.insert_youtube(
    #                         video_title, video_url, video_date.isoformat(),
    #                         transcript, concise_summary, detailed_summary
    #                     )
    #                 total_results += 1
    #                 if total_results >= max_results:
    #                     break

    #         next_page_token = response.get('nextPageToken')
    #         if not next_page_token:
    #             break

    # def fetch_serp_data(self, serp_api_key, query, num_results=100, limit=None):
    #     """
    #     Fetch SERP results using SerpAPI
    #     """
    #     print("Starting the fetching process for SERP data")
    #     two_weeks_ago = datetime.now() - timedelta(weeks=2)
    #     url = f"https://serpapi.com/search.json?q={query}&num={num_results}&api_key={serp_api_key}"
    #     response = requests.get(url).json()
    #     total_fetched = 0

    #     for result in response.get('organic_results', []):
    #         if limit and total_fetched >= limit:
    #             return total_fetched

    #         date = datetime.now()  # Not all SERP results have a date, so just use "now"
    #         if date >= two_weeks_ago:
    #             title = result['title']
    #             link = result['link']
    #             snippet = result.get('snippet', '')
    #             image = result.get('thumbnail', '') 
    #             concise_summary = "Concise SERP summary placeholder"
    #             detailed_summary = "Detailed SERP summary placeholder"

    #             if not self.db_handler.is_duplicate(title, link, 'serp'):
    #                 self.db_handler.insert_serp(
    #                     title, link, date.isoformat(), snippet,
    #                     concise_summary, detailed_summary, image
    #                 )
    #                 total_fetched += 1

    #     return total_fetched
