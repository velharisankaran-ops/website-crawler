import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from typing import List, Dict, Set
import json
import csv
from datetime import datetime

class WebsiteCrawler:
    def __init__(self, base_url: str, max_pages: int = 50, delay: float = 1.0):
        """
        Initialize the website crawler.
        
        Args:
            base_url: The starting URL to begin crawling
            max_pages: Maximum number of pages to crawl
            delay: Delay between requests in seconds
        """
        self.base_url = base_url
        self.max_pages = max_pages
        self.delay = delay
        self.visited_urls: Set[str] = set()
        self.results: List[Dict] = []
        self.domain = urlparse(base_url).netloc
        
    def is_valid_url(self, url: str) -> bool:
        """Check if URL belongs to the same domain and is valid."""
        parsed = urlparse(url)
        return bool(parsed.netloc) and parsed.netloc == self.domain and parsed.scheme in ['http', 'https']
    
    def get_page_metadata(self, url: str) -> Dict:
        """Extract metadata from a single webpage."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            title = soup.title.string if soup.title else 'No title'
            
            # Extract meta description
            meta_desc = ''
            meta_tag = soup.find('meta', attrs={'name': 'description'}) or \
                      soup.find('meta', attrs={'property': 'og:description'})
            if meta_tag:
                meta_desc = meta_tag.get('content', '')
            
            # Extract keywords
            keywords = ''
            keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
            if keywords_tag:
                keywords = keywords_tag.get('content', '')
            
            # Extract all heading levels (H1-H6)
            headings = {}
            for level in range(1, 7):
                heading_tags = soup.find_all(f'h{level}')
                if heading_tags:
                    headings[f'h{level}'] = [tag.get_text(strip=True) for tag in heading_tags]
                else:
                    headings[f'h{level}'] = []
            
            return {
                'url': url,
                'title': title,
                'meta_description': meta_desc[:500] if meta_desc else '',  # Limit description length
                'keywords': keywords[:200] if keywords else '',  # Limit keywords length
                'headings': headings,
                'status_code': response.status_code,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error processing {url}: {str(e)}")
            return {
                'url': url,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def find_links(self, url: str) -> Set[str]:
        """Extract all valid links from a webpage."""
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            links = set()
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                full_url = urljoin(url, href)
                if self.is_valid_url(full_url) and full_url not in self.visited_urls:
                    links.add(full_url)
            return links
            
        except Exception as e:
            print(f"Error finding links on {url}: {str(e)}")
            return set()
    
    def crawl(self) -> List[Dict]:
        """Start crawling the website."""
        urls_to_visit = {self.base_url}
        
        while urls_to_visit and len(self.visited_urls) < self.max_pages:
            current_url = urls_to_visit.pop()
            
            if current_url in self.visited_urls:
                continue
                
            print(f"Crawling: {current_url}")
            
            # Get page metadata
            metadata = self.get_page_metadata(current_url)
            self.results.append(metadata)
            self.visited_urls.add(current_url)
            
            # Find new links
            new_links = self.find_links(current_url)
            urls_to_visit.update(new_links - self.visited_urls)
            
            # Respect crawl delay
            time.sleep(self.delay)
        
        return self.results
    
    def save_to_csv(self, filename: str = 'crawl_results.csv') -> None:
        """Save crawl results to a CSV file."""
        if not self.results:
            print("No results to save. Run crawl() first.")
            return
            
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.results[0].keys())
                writer.writeheader()
                writer.writerows(self.results)
            print(f"Results saved to {filename}")
        except Exception as e:
            print(f"Error saving to CSV: {str(e)}")
    
    def save_to_json(self, filename: str = 'crawl_results.json') -> None:
        """Save crawl results to a JSON file."""
        if not self.results:
            print("No results to save. Run crawl() first.")
            return
            
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            print(f"Results saved to {filename}")
        except Exception as e:
            print(f"Error saving to JSON: {str(e)}")

def crawl_website(url: str, max_pages: int = 50) -> List[Dict]:
    ""
    Crawl a website and return metadata for each page.
    
    Args:
        url: The starting URL to crawl
        max_pages: Maximum number of pages to crawl
        
    Returns:
        List of dictionaries containing page metadata
    ""
    crawler = WebsiteCrawler(url, max_pages)
    return crawler.crawl()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Crawl a website to extract URLs, titles, and metadata.")
    parser.add_argument("url", help="Starting URL to crawl")
    parser.add_argument("--max-pages", type=int, default=50, help="Maximum pages to crawl")
    parser.add_argument("--output", choices=['csv', 'json', 'console'], default='console', 
                       help="Output format (default: console)")
    parser.add_argument("--output-file", help="Output file name (default: crawl_results.[csv|json])")
    
    args = parser.parse_args()
    
    crawler = WebsiteCrawler(args.url, args.max_pages)
    results = crawler.crawl()
    
    if args.output == 'csv':
        output_file = args.output_file or 'crawl_results.csv'
        crawler.save_to_csv(output_file)
    elif args.output == 'json':
        output_file = args.output_file or 'crawl_results.json'
        crawler.save_to_json(output_file)
    else:
        # Print to console
        for result in results:
            print("\n" + "="*80)
            print(f"URL: {result.get('url')}")
            print(f"Title: {result.get('title', 'N/A')}")
            print(f"Status: {result.get('status_code', 'N/A')}")
            print(f"Meta Description: {result.get('meta_description', 'N/A')[:100]}{'...' if len(result.get('meta_description', '')) > 100 else ''}" if result.get('meta_description') else "Meta Description: N/A")
            # Print all headings
            for level in range(1, 7):
                h_tags = result.get('headings', {}).get(f'h{level}', [])
                if h_tags:
                    print(f"H{level}:")
                    for i, h in enumerate(h_tags, 1):
                        print(f"  {i}. {h}")
        print(f"\nCrawled {len(results)} pages.")
        print("Use --output csv or --output json to save results to a file.")
