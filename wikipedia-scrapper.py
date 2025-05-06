import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

def get_wikipedia_article(title):
    """
    Scraping a Wikipedia article based on its title.
    
    Args:
        title (str): The title of the Wikipedia article.
        
    Returns:
        dict: A dictionary containing the article title, summary, content, and sections.
    """
    # Format the URL
    url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
    
    # Add headers to avoid being blocked
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Get the page
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        return {
            "title": title,
            "error": f"Failed to retrieve page. Status code: {response.status_code}"
        }
    
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract the article title
    page_title = soup.find(id="firstHeading").text
    
    # Extract the summary (first paragraph of the article)
    content_div = soup.find(id="mw-content-text")
    paragraphs = content_div.find_all("p")
    summary = ""
    for p in paragraphs:
        if p.text.strip():
            summary = p.text.strip()
            break
    
    # Extract sections and their content
    sections = []
    for heading in soup.find_all(['h2', 'h3']):
        if heading.find('span', {'class': 'mw-headline'}):
            section_title = heading.find('span', {'class': 'mw-headline'}).text
            
            # Get content of section (paragraphs until next heading)
            section_content = ""
            for sibling in heading.next_siblings:
                if sibling.name in ['h2', 'h3']:
                    break
                if sibling.name == 'p':
                    section_content += sibling.text.strip() + "\n"
            
            if section_content.strip():
                sections.append({
                    "title": section_title,
                    "content": section_content.strip()
                })
    
    # Get all links in the article
    links = []
    for link in content_div.find_all('a', href=True):
        href = link.get('href')
        if href.startswith('/wiki/') and ':' not in href:
            links.append({
                "text": link.text,
                "url": "https://en.wikipedia.org" + href
            })
    
    return {
        "title": page_title,
        "summary": summary,
        "sections": sections,
        "links": links[:20]  # Limit to first 20 links to avoid overwhelming results
    }

def search_wikipedia(query, limit=5):
    """
    Search Wikipedia for articles matching the query.
    
    Args:
        query (str): The search query.
        limit (int): Maximum number of results to return.
        
    Returns:
        list: A list of search results.
    """
    base_url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": query,
        "srlimit": limit
    }
    
    response = requests.get(base_url, params=params)
    data = response.json()
    
    if "query" in data and "search" in data["query"]:
        return data["query"]["search"]
    else:
        return []

def get_category_members(category, limit=20):
    """
    Get articles that belong to a specific Wikipedia category.
    
    Args:
        category (str): The category name (without 'Category:' prefix).
        limit (int): Maximum number of results to return.
        
    Returns:
        list: A list of articles in the category.
    """
    base_url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "list": "categorymembers",
        "cmtitle": f"Category:{category}",
        "cmlimit": limit
    }
    
    response = requests.get(base_url, params=params)
    data = response.json()
    
    if "query" in data and "categorymembers" in data["query"]:
        return data["query"]["categorymembers"]
    else:
        return []

def crawl_wikipedia(start_article, depth=2, max_articles=10):
    """
    Crawl Wikipedia starting from a specific article, following links to a certain depth.
    
    Args:
        start_article (str): The title of the starting article.
        depth (int): How many links deep to crawl.
        max_articles (int): Maximum number of articles to crawl.
        
    Returns:
        list: A list of article data.
    """
    visited = set()
    to_visit = [(start_article, 0)]  # (article_title, depth)
    results = []
    
    while to_visit and len(results) < max_articles:
        current_title, current_depth = to_visit.pop(0)
        
        if current_title in visited:
            continue
            
        visited.add(current_title)
        
        print(f"Crawling: {current_title} (depth {current_depth})")
        article_data = get_wikipedia_article(current_title)
        results.append(article_data)
        
        # Add a delay to be respectful of Wikipedia's servers
        time.sleep(1 + random.random())
        
        # If we haven't reached the maximum depth, add links to the queue
        if current_depth < depth:
            for link in article_data.get("links", [])[:3]:  # Limit to first 3 links to avoid exponential growth
                if link["text"] not in visited:
                    to_visit.append((link["text"], current_depth + 1))
    
    return results

def save_to_csv(data, filename="wikipedia_data.csv"):
    """
    Save the extracted data to a CSV file.
    
    Args:
        data (list): List of article data.
        filename (str): Name of the output file.
    """
    rows = []
    for article in data:
        row = {
            "title": article["title"],
            "summary": article["summary"]
        }
        rows.append(row)
    
    df = pd.DataFrame(rows)
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

# Usage example
if __name__ == "__main__":
    # Example 1: Get a single Wikipedia article
    article_data = get_wikipedia_article("Python (programming language)")
    print(f"Title: {article_data['title']}")
    print(f"Summary: {article_data['summary'][:200]}...")
    print(f"Number of sections: {len(article_data['sections'])}")
    print(f"Number of links: {len(article_data['links'])}")
    
    # Example 2: Search Wikipedia
    print("\nSearching for 'machine learning':")
    search_results = search_wikipedia("machine learning")
    for i, result in enumerate(search_results):
        print(f"{i+1}. {result['title']}")
    
    # Example 3: Get category members
    print("\nArticles in 'Machine learning algorithms' category:")
    category_members = get_category_members("Machine learning algorithms")
    for i, member in enumerate(category_members[:5]):  # Show first 5
        print(f"{i+1}. {member['title']}")
    
    # Example 4: Crawl Wikipedia starting from a specific article
    print("\nCrawling Wikipedia starting from 'Artificial intelligence':")
    crawl_results = crawl_wikipedia("Artificial intelligence", depth=1, max_articles=3)
    save_to_csv(crawl_results, "ai_articles.csv")