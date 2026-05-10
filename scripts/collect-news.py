#!/usr/bin/env python3
"""Collect news headlines from RSS feeds (global + Indonesia)."""

import json
import urllib.request
import xml.etree.ElementTree as ET
import time
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "docs" / "data"
OUTPUT_FILE = OUTPUT_DIR / "news.json"

FEEDS = [
    {
        "url": "https://feeds.bbci.co.uk/news/rss.xml",
        "source": "BBC News",
        "category": "Global",
        "max": 4,
    },
    {
        "url": "https://www.antaranews.com/rss/terkini.xml",
        "source": "Antara News",
        "category": "Indonesia",
        "max": 4,
    },
]


def fetch_text(url, timeout=15):
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except Exception as e:
        return None


def parse_rss(xml_bytes, source_name, max_items=5):
    """Parse RSS XML and extract items."""
    articles = []
    try:
        root = ET.fromstring(xml_bytes)
        # RSS 2.0: /rss/channel/item
        # Atom: /feed/entry
        channel = root.find("channel")
        if channel is not None:
            items = channel.findall("item")
        else:
            # Try Atom format
            items = root.findall("{http://www.w3.org/2005/Atom}entry")
        
        for item in items[:max_items]:
            title = ""
            link = ""
            pub_date = ""
            description = ""
            
            if channel is not None:
                # RSS 2.0
                title_el = item.find("title")
                link_el = item.find("link")
                date_el = item.find("pubDate")
                desc_el = item.find("description")
                
                title = title_el.text if title_el is not None and title_el.text else ""
                link = link_el.text if link_el is not None and link_el.text else ""
                pub_date = date_el.text if date_el is not None and date_el.text else ""
                
                if desc_el is not None and desc_el.text:
                    # Strip HTML tags from description
                    desc = desc_el.text
                    import re as re_module
                    desc = re_module.sub(r"<[^>]+>", "", desc)
                    description = desc[:200] if len(desc) > 200 else desc
            else:
                # Atom
                ns = {"atom": "http://www.w3.org/2005/Atom"}
                title_el = item.find("atom:title", ns)
                link_el = item.find("atom:link", ns)
                date_el = item.find("atom:published", ns)
                
                title = title_el.text if title_el is not None and title_el.text else ""
                link = link_el.get("href") if link_el is not None else ""
                pub_date = date_el.text if date_el is not None and date_el.text else ""
            
            articles.append({
                "title": title.strip(),
                "link": link.strip(),
                "published": pub_date.strip(),
                "description": description.strip(),
                "source": source_name,
            })
    except Exception as e:
        articles.append({"error": str(e), "source": source_name})
    
    return articles


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    all_articles = []
    
    for feed in FEEDS:
        xml_bytes = fetch_text(feed["url"])
        if xml_bytes:
            articles = parse_rss(xml_bytes, feed["source"], feed["max"])
            for art in articles:
                art["category"] = feed["category"]
            all_articles.extend(articles)
            print(f"  {feed['source']}: {len(articles)} articles")
        else:
            print(f"  {feed['source']}: failed to fetch")
    
    data = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "articles": all_articles,
    }
    
    OUTPUT_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"News data written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
