# 🌐 Website Metadata Crawler

A powerful Python tool to crawl websites and extract valuable SEO metadata. Perfect for SEO audits, content analysis, and website structure analysis.

## ✨ Features

- 🕷️ Crawl websites and extract metadata
- 📊 Export results to CSV or JSON
- 🔍 Extract titles, meta descriptions, keywords, and H1s
- ⚡ Respects robots.txt (coming soon)
- 🚀 Fast and efficient with configurable delays
- 📦 Easy to use CLI interface

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/velharisankaran/website-crawler.git
cd website-crawler
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## 🛠️ Usage

### Basic Usage
```bash
python crawler.py https://example.com
```

### Advanced Options
```bash
# Crawl up to 100 pages and save to CSV
python crawler.py https://example.com --max-pages 100 --output csv

# Save to a specific file
python crawler.py https://example.com --output json --output-file my_results.json

# Show results in console only
python crawler.py https://example.com --output console
```

### As a Python Module
```python
from crawler import WebsiteCrawler

# Initialize crawler
crawler = WebsiteCrawler('https://example.com', max_pages=50)

# Start crawling
results = crawler.crawl()

# Save results
crawler.save_to_csv('results.csv')
# or
crawler.save_to_json('results.json')
```

## 📋 Output

The crawler extracts the following information for each page:
- URL
- Page Title
- Meta Description
- Keywords
- H1 Heading
- HTTP Status Code
- Timestamp

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for educational and legitimate SEO purposes only. Please:
- Respect website terms of service
- Don't overload servers (use appropriate delays)
- Only crawl websites you own or have permission to crawl
- Check robots.txt before crawling

## 📬 Contact

Velhari Sankaran - [@velharisankaran](https://twitter.com/velharisankaran)

Project Link: [https://github.com/velharisankaran/website-crawler](https://github.com/velharisankaran/website-crawler)
