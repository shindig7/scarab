from pytest import fixture, mark
from pytest import raises as pytest_raises
from pytest_httpserver import HTTPServer
from loguru import logger
from html import unescape
import re

from scarab.crawlers import SeleniumCrawler, SimpleCrawler

@fixture(scope="module")
def httpserver():
    server = HTTPServer(
        port=8081,
    )
    server.start()
    yield server
    server.stop()

@fixture
def simple_crawler(httpserver: HTTPServer):
    base_url = f"http://{httpserver.host}:8081"
    return SimpleCrawler(base_url)

@fixture
def selenium_crawler(httpserver: HTTPServer):
    base_url = f"http://{httpserver.host}:8081"
    return SeleniumCrawler(base_url)

def normalize_html(html):
    return re.sub(r'\s+', ' ', html).strip()

def extract_and_unescape_html(page_source):
    start_index = page_source.find('<html>') + len('<html>')
    end_index = page_source.find('</pre>')
    extracted_html = page_source[start_index:end_index].strip()
    return unescape(extracted_html)

def test_crawl(simple_crawler, httpserver):
    html_content = """
    <html>
        <head>
            <title>Test</title>
        </head>
        <body>
            <h1>Hello, World!</h1>
        </body>
    </html>
    """.strip()
    httpserver.expect_request("/", method="GET").respond_with_data(html_content)

    simple_crawler.crawl()
    assert simple_crawler.page == html_content
    httpserver.check_assertions()

def test_selenium_crawl(selenium_crawler, httpserver: HTTPServer):
    html_content = """
    <html>
        <head>
            <title>Test</title>
        </head>
        <body>
            <h1>Hello, World!</h1>
        </body>
    </html>
    """.strip()
    httpserver.expect_request("/").respond_with_data(html_content, content_type="text/html")

    selenium_crawler.crawl()
    result_html = normalize_html(extract_and_unescape_html(selenium_crawler.page))
    expected_html = normalize_html(html_content)
    logger.info(f"Result HTML: {result_html}")
    logger.info(f"Expected HTML: {expected_html}")
    assert result_html == expected_html

if __name__ == "__main__":
    crawler = SeleniumCrawler("http://www.example.com")
    crawler.crawl()
    print(crawler.page)