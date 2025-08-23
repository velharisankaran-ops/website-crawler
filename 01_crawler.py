import requests
from bs4 import BeautifulSoup, Comment
from urllib.parse import urljoin, urlparse
import time
from collections import deque, defaultdict
from typing import Set, List, Dict, Any, Optional
import re
import pandas as pd
from dataclasses import dataclass

@dataclass
class SEOMetrics:
    """Class to store SEO metrics for a single URL."""
    url: str
    status_code: int = 0
    title: str = ""
    meta_description: str = ""
    h1: str = ""
    h2s: List[str] = None
    canonical: str = ""
    meta_robots: str = ""
    word_count: int = 0
    internal_links: int = 0
    external_links: int = 0
    image_count: int = 0
    images_with_alt: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary for CSV export."""
        return {
            'URL': self.url,
            'Status Code': self.status_code,
            'Title': self.title,
            'Meta Description': self.meta_description,
            'H1': self.h1,
            'H2s': ' | '.join(self.h2s) if self.h2s else '',
            'Canonical': self.canonical,
            'Meta Robots': self.meta_robots,
            'Word Count': self.word_count,
            'Internal Links': self.internal_links,
            'External Links': self.external_links,
            'Image Count': self.image_count,
            'Images with Alt': self.images_with_alt,
            'Alt Text Coverage': f"{(self.images_with_alt / self.image_count * 100):.1f}%" if self.image_count > 0 else 'N/A'
        }

class EnhancedSEOCrawler:
    """Enhanced SEO crawler that collects comprehensive on-page SEO metrics."""
    
    def __init__(self, base_url: str, max_pages: int = 50):
        """
        Initialize the crawler.
        
        Args:
            base_url: Starting URL for crawling
            max_pages: Maximum number of pages to crawl
        """
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.max_pages = max_pages
        self.visited_urls: Set[str] = set()
        self.to_visit = deque([base_url])
        self.results: List[SEOMetrics] = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def is_internal_url(self, url: str) -> bool:
        """Check if a URL is internal (same domain)."""
        parsed_url = urlparse(url)
        return not parsed_url.netloc or parsed_url.netloc == self.domain
    
    def get_absolute_url(self, url: str) -> str:
        """Convert a relative URL to absolute."""
        return urljoin(self.base_url, url.split('#')[0])  # Remove fragments
    
    def get_page_content(self, url: str) -> Optional[str]:
        """Fetch the page content with error handling."""
        try:
            response = self.session.get(url, timeout=10, allow_redirects=True)
            response.raise_for_status()
            return response.text
        except (requests.RequestException, Exception) as e:
            print(f"Error fetching {url}: {str(e)}")
            return None
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        if not text:
            return ""
        # Remove extra whitespace and newlines
        return ' '.join(str(text).split())
    
    def get_visible_text(self, soup: BeautifulSoup) -> str:
        """Extract visible text from the page."""
        # Remove script and style elements
        for element in soup(["script", "style", "nav", "footer", "header", "iframe"]):
            element.decompose()
        
        # Remove comments
        for element in soup.find_all(string=lambda text: isinstance(text, Comment)):
            element.extract()
            
        # Get text and clean it
        text = soup.get_text(separator=' ', strip=True)
        return self.clean_text(text)
    
    def count_words(self, text: str) -> int:
        """Count words in the given text."""
        return len(re.findall(r'\b\w+\b', text)) if text else 0
    
    def extract_seo_data(self, soup: BeautifulSoup, url: str, status_code: int = 200) -> SEOMetrics:
        """Extract all required SEO data from the page."""
        metrics = SEOMetrics(url=url, status_code=status_code)
        
        try:
            # Get title
            metrics.title = self.clean_text(soup.title.string) if soup.title else ""
            
            # Get meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'}) or \
                       soup.find('meta', attrs={'property': 'og:description'})
            metrics.meta_description = self.clean_text(meta_desc.get('content', '')) if meta_desc else ""
            
            # Get h1 and h2s
            h1 = soup.find('h1')
            metrics.h1 = self.clean_text(h1.get_text()) if h1 else ""
            metrics.h2s = [self.clean_text(h2.get_text()) for h2 in soup.find_all('h2')[:3]]
            
            # Get canonical
            canonical = soup.find('link', rel='canonical')
            metrics.canonical = canonical.get('href', '') if canonical else ""
            
            # Get meta robots
            robots = soup.find('meta', attrs={'name': 'robots'})
            metrics.meta_robots = robots.get('content', '') if robots else ""
            
            # Get visible text and word count
            visible_text = self.get_visible_text(soup)
            metrics.word_count = self.count_words(visible_text)
            
            # Count links
            all_links = soup.find_all('a', href=True)
            metrics.internal_links = sum(1 for link in all_links 
                                      if self.is_internal_url(link.get('href', '')))
            metrics.external_links = len(all_links) - metrics.internal_links
            
            # Count images and alt text
            images = soup.find_all('img')
            metrics.image_count = len(images)
            metrics.images_with_alt = sum(1 for img in images if img.get('alt', '').strip())
            
        except Exception as e:
            print(f"Error extracting SEO data from {url}: {str(e)}")
        
        return metrics
    
    def crawl(self):
        """Start crawling the website and collect SEO data."""
        try:
            while self.to_visit and len(self.visited_urls) < self.max_pages:
                url = self.to_visit.popleft()
                
                if url in self.visited_urls:
                    continue
                    
                print(f"Crawling: {url}")
                
                try:
                    # Get page content
                    response = self.session.get(url, timeout=10, allow_redirects=True)
                    content = response.text
                    
                    if not content:
                        self.visited_urls.add(url)
                        continue
                    
                    # Parse the page
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # Extract SEO data
                    seo_data = self.extract_seo_data(soup, url, response.status_code)
                    self.results.append(seo_data)
                    
                    # Add new links to the queue
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        if self.is_internal_url(href):
                            abs_url = self.get_absolute_url(href)
                            if abs_url not in self.visited_urls and abs_url not in self.to_visit:
                                self.to_visit.append(abs_url)
                    
                except Exception as e:
                    print(f"Error processing {url}: {str(e)}")
                
                finally:
                    self.visited_urls.add(url)
                    time.sleep(1)  # Be nice to the server
                    
        except KeyboardInterrupt:
            print("\nCrawling stopped by user.")
        
        print(f"\nCrawling completed. Visited {len(self.visited_urls)} pages.")
    
    def save_to_csv(self, filename: str = 'seo_audit.csv') -> None:
        """Save the collected data to a CSV file."""
        if not self.results:
            print("No data to save!")
            return
        
        # Convert metrics to dictionaries
        data = [metrics.to_dict() for metrics in self.results]
        
        # Create DataFrame and save to CSV
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"SEO audit saved to {filename}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced SEO Crawler for Website Analysis')
    parser.add_argument('url', help='Starting URL (e.g., https://example.com)')
    parser.add_argument('--max-pages', type=int, default=50, 
                       help='Maximum number of pages to crawl (default: 50)')
    parser.add_argument('--output', default='seo_audit.csv',
                       help='Output CSV filename (default: seo_audit.csv)')
    
    args = parser.parse_args()
    
    print(f"Starting Enhanced SEO Crawler for: {args.url}")
    print(f"Maximum pages to crawl: {args.max_pages}")
    print("Press Ctrl+C to stop crawling early\n")
    
    try:
        crawler = EnhancedSEOCrawler(args.url, args.max_pages)
        crawler.crawl()
        crawler.save_to_csv(args.output)
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
