import requests
import sys
from datetime import datetime

# Your NewsAPI key
API_KEY = "9cf9ed92e278419ab7b279994f28bdb8"
BASE_URL = "https://newsapi.org/v2/"

# ANSI color codes
GREEN = "\033[92m"
BLUE = "\033[94m"
PINK = "\033[95m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def fetch_top_headlines(category=None, country=None, query=None):
    """Fetch top headlines by category and/or country, or fallback to everything."""
    params = {
        "apiKey": API_KEY,
        "language": "en",
        "pageSize": 10,
        "sortBy": "relevancy"
    }
    if category:
        params["category"] = category
    if country:
        params["country"] = country
    if query:
        params["q"] = query

    endpoint = "top-headlines" if (category or country) else "everything"
    try:
        response = requests.get(BASE_URL + endpoint, params=params)
        response.raise_for_status()
        data = response.json()
        if data["status"] == "ok":
            return data["articles"]
        else:
            print(f"Error: {data.get('message', 'Unknown error')}")
            return []
    except Exception as e:
        print(f"Request failed: {e}")
        return []

def fetch_local_ke(category=None, keywords=""):
    """Fetch Kenyan news. Try top-headlines first, if few results, fallback to everything."""
    articles = fetch_top_headlines(category=category, country="ke")
    if len(articles) >= 5:
        return articles
    # Fallback: use everything with Kenya + optional keywords
    query = f"Kenya {keywords}".strip()
    return fetch_top_headlines(query=query)

def fetch_international(category=None, keywords=""):
    """Fetch international news. For business/tech, use US top-headlines with category."""
    if category in ["business", "technology"]:
        return fetch_top_headlines(category=category, country="us")
    else:
        # For law/politics, use everything with keywords (no country filter)
        return fetch_top_headlines(query=keywords)

def print_articles(title, articles, color):
    """Print a list of articles with a colored heading."""
    if not articles:
        print(f"{color}--- {title} (no articles found) ---{RESET}")
        return
    print(f"\n{color}--- {title} ({len(articles)} articles) ---{RESET}")
    for idx, article in enumerate(articles, 1):
        pub_date = article.get("publishedAt", "")
        if pub_date:
            try:
                pub_date = datetime.fromisoformat(pub_date.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M")
            except:
                pub_date = ""
        print(f"{color}{idx}. {article['title']}{RESET}")
        print(f"   Source: {article['source']['name']} | Published: {pub_date}")
        print(f"   URL: {article['url']}")
        print()

def main():
    print(f"{YELLOW}=== News Aggregator (Business, Tech, Law, Politics) ==={RESET}")

    # Sector mapping
    sectors = {
        "1": {"name": "Business", "color": GREEN, "category": "business", "keywords": "business finance economy accounting"},
        "2": {"name": "Technology", "color": BLUE, "category": "technology", "keywords": "technology tech software"},
        "3": {"name": "Law", "color": PINK, "category": None, "keywords": "law legal court judiciary"},
        "4": {"name": "Politics", "color": YELLOW, "category": None, "keywords": "politics government parliament president"}
    }

    print("\nChoose a sector:")
    for key, sec in sectors.items():
        print(f"{key}. {sec['name']}")

    sector_choice = input("Enter number (1-4): ").strip()
    if sector_choice not in sectors:
        print("Invalid choice.")
        return

    sector = sectors[sector_choice]
    print(f"\nChoose scope for {sector['name']}:")
    print("1. Local (Kenya)")
    print("2. International")
    scope = input("Enter 1 or 2: ").strip()

    if scope == "1":
        print(f"{sector['color']}Fetching {sector['name']} news from Kenya...{RESET}")
        articles = fetch_local_ke(category=sector['category'], keywords=sector['keywords'])
        title = f"{sector['name']} News (Kenya)"
    elif scope == "2":
        print(f"{sector['color']}Fetching international {sector['name']} news...{RESET}")
        articles = fetch_international(category=sector['category'], keywords=sector['keywords'])
        title = f"{sector['name']} News (International)"
    else:
        print("Invalid scope.")
        return

    print_articles(title, articles, sector['color'])

if __name__ == "__main__":
    main()