# Scarab
_Author: Jonathan Law_

**Scarab** is a modular Python package for web crawling and file handling. It includes tools for downloading files, scraping websites, and handling logging with robust customization.

## Features

1. **File Downloader**: 
   - Downloads files from URLs with optional file type detection and extension fixing.
   - Automatically sets modification dates for downloaded files.

2. **Crawlers**:
   - **SimpleCrawler**: Fetches web pages using the `requests` library with retry mechanisms.
   - **SeleniumCrawler**: Uses Selenium for dynamic web page rendering.
   - Supports both synchronous and asynchronous crawling.
   - Provides easy access to HTML elements via XPath, CSS selectors, class, or ID.

3. **Utilities**:
   - Browser automation to render locally hosted HTML files.
   - Enhanced logging setup using `loguru` for better log management and debugging.

---

## Getting Started

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/crawler-suite.git
   cd crawler-suite
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

### Downloading Files

```python
from download import download_file

download_file(
    url="https://example.com/sample.pdf",
    filename="sample.pdf",
    fix_extension=True
)
```

### Web Crawling

#### Simple Crawler
```python
from crawlers import SimpleCrawler

crawler = SimpleCrawler("https://example.com")
crawler.crawl()
print(crawler.page)
```

#### Selenium Crawler
```python
from crawlers import SeleniumCrawler

crawler = SeleniumCrawler("https://example.com", headless=True)
crawler.crawl()
print(crawler.page)
```

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.
