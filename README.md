# SEO Analysis Toolkit

A comprehensive Python-based solution for website SEO analysis, including a web crawler and reporting tools. This toolkit helps identify SEO issues, track on-page elements, and generate comprehensive reports.

## Features

### 1. Enhanced SEO Crawler
- Crawls websites while respecting `robots.txt`
- Extracts key SEO elements (titles, meta descriptions, headings, etc.)
- Analyzes links (internal/external)
- Checks image alt text
- Handles pagination and dynamic content
- Implements crawl delays to be server-friendly

### 2. SEO Analyzer
- Processes crawl data to identify SEO issues
- Generates detailed Excel reports
- Covers technical, on-page, and content SEO factors
- Provides actionable insights

### 3. SEO Summarizer (New!)
- Creates executive summary dashboards
- Groups related issues
- Visualizes data with charts
- Prioritizes issues by severity

## Installation

1. Ensure you have Python 3.7+ installed
2. Install the required packages:
   ```bash
   pip install requests beautifulsoup4 pandas matplotlib xlsxwriter
   ```

## Usage

## Execution Order

### 1. Run the Web Crawler
```bash
python 01_crawler.py https://example.com
```

#### Crawler Options
```bash
python 01_crawler.py https://example.com \
    --max-pages 100 \
    --delay 1.0 \
    --output seo_audit_results.csv
```

### 2. Generate Detailed Analysis
```bash
python 02_analyzer.py seo_audit_results.csv --output full_analysis.xlsx
```

### 3. Create Executive Summary
```bash
python 03_summarizer.py seo_audit_results.csv --output reports/
```

#### Summarizer Options
- `input_csv`: Path to the analyzer output CSV file (required)
- `--output`, `-o`: Output directory (default: 'reports/')

## Output Columns

The generated CSV file includes the following columns:

| Column | Description |
|--------|-------------|
| URL | Page URL |
| Status_Code | HTTP status code |
| Title | Page title |
| Meta_Description | Meta description |
| H1 | Main heading |
| H2s | First 3 H2 headings (pipe-separated) |
| Canonical | Canonical URL |
| Meta_Robots | Meta robots tag content |
| Word_Count | Number of words in visible text |
| Internal_Links | Count of internal links |
| External_Links | Count of external links |
| Image_Count | Total images on page |
| Images_With_Alt_Count | Images with alt text |

## Example Analysis

After running the crawler, you can analyze the results using pandas:

```python
import pandas as pd

# Load the results
df = pd.read_csv('seo_audit_results.csv')

# Find pages missing meta descriptions
missing_desc = df[df['Meta_Description'] == ''][['URL', 'Title']]
print(f"Pages missing meta descriptions: {len(missing_desc)}")

# Find pages with multiple H1s (potential SEO issue)
multiple_h1 = df[df['H1'].str.contains('\|', na=False)][['URL', 'H1']]
print(f"Pages with multiple H1s: {len(multiple_h1)}")
```

## Best Practices

1. **Start Small**: Begin with a small `--max-pages` value to test
2. **Respect Servers**: Use appropriate `--delay` (1-2 seconds is recommended)
3. **Check Robots.txt**: The crawler respects `robots.txt` by default
4. **Review Output**: Always review the CSV output for data quality
5. **Monitor Performance**: Large sites may take time to crawl

## Troubleshooting

### Common Issues
- **Connection Errors**: Check your internet connection and the target website's availability
- **SSL Errors**: Try running with `--no-verify-ssl` (not recommended for production)
- **Memory Issues**: For large sites, reduce `--max-pages`

### Logs
- Progress is shown in the console
- Errors are logged with details about the failed URL

## License

This project is for educational purposes. Please ensure you have permission to crawl the target website.

## References

- [Google Search Central Documentation](https://developers.google.com/search/docs)
- [Moz Beginner's Guide to SEO](https://moz.com/beginners-guide-to-seo)
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Requests Library](https://docs.python-requests.org/)

---
*Note: Always ensure compliance with website terms of service and robots.txt when crawling.*
