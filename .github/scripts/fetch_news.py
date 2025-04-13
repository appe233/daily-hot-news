#!/usr/bin/env python3
import json
import datetime
import requests
from bs4 import BeautifulSoup
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def fetch_sina_news():
    """Fetch hot news from Sina news website."""
    logger.info("Fetching news from Sina...")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get('https://news.sina.com.cn/', headers=headers)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch Sina news: {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Find the hot news section
        hot_news_section = soup.select_one('.news-hot')
        
        if not hot_news_section:
            logger.warning("Could not find hot news section in Sina")
            
            # Try alternative method
            hot_news_items = []
            all_links = soup.find_all('a')
            
            for link in all_links:
                if link.text and len(link.text.strip()) > 5 and not link.find('img'):
                    hot_news_items.append({
                        "title": link.text.strip(),
                        "source": "新浪新闻",
                        "category": "热点",
                        "url": link.get('href', 'https://news.sina.com.cn/')
                    })
            
            # Return only the first 10 items if we found any
            if hot_news_items:
                return hot_news_items[:10]
            return []
        
        news_items = []
        links = hot_news_section.find_all('a')
        
        for link in links:
            if link.text and len(link.text.strip()) > 5:
                news_items.append({
                    "title": link.text.strip(),
                    "source": "新浪新闻",
                    "category": "热点",
                    "url": link.get('href', 'https://news.sina.com.cn/')
                })
        
        return news_items[:10]  # Return top 10 news
    
    except Exception as e:
        logger.error(f"Error fetching Sina news: {e}")
        return []

def fetch_toutiao_news():
    """Fetch hot news from Toutiao website."""
    logger.info("Fetching news from Toutiao...")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get('https://www.toutiao.com/', headers=headers)
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch Toutiao news: {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.text, 'lxml')
        news_items = []
        
        # Find news items
        articles = soup.select('div.feed-card-item')
        
        if not articles:
            logger.warning("Could not find news articles in Toutiao")
            return []
        
        for article in articles[:10]:
            title_elem = article.select_one('a.feed-card-title')
            if title_elem and title_elem.text:
                news_items.append({
                    "title": title_elem.text.strip(),
                    "source": "今日头条",
                    "category": "热点",
                    "url": "https://www.toutiao.com" + title_elem.get('href', '/')
                })
        
        return news_items
    
    except Exception as e:
        logger.error(f"Error fetching Toutiao news: {e}")
        return []

def update_news_file():
    """Update the news.json file with the latest news."""
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    
    # Fetch news from different sources
    sina_news = fetch_sina_news()
    toutiao_news = fetch_toutiao_news()
    
    # Combine news from different sources
    all_news = sina_news + toutiao_news
    
    # Remove duplicates based on title
    unique_news = []
    seen_titles = set()
    
    for item in all_news:
        if item["title"] not in seen_titles:
            unique_news.append(item)
            seen_titles.add(item["title"])
    
    # Create the news data structure
    news_data = {
        "date": today,
        "news": unique_news[:15]  # Keep only top 15 news items
    }
    
    # Write to file
    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(news_data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Successfully updated news.json with {len(news_data['news'])} news items")

if __name__ == "__main__":
    update_news_file()