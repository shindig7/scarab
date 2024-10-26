from pytest import fixture, mark
from pytest import raises as pytest_raises

from scarab.crawlers import SeleniumCrawler, SimpleCrawler


@fixture
def url() -> str:
    return "https://www.example.com"


@fixture
def error_url() -> str:
    return "https://www.google.com/404"


def test_SeleniumCrawler(url, error_url):
    crawler = SeleniumCrawler(url)
    crawler.crawl()
    assert crawler.page is not None

    crawler.render(timeout=1)


def test_SimpleCrawler(url, error_url):
    crawler = SimpleCrawler(url)
    crawler.crawl()
    assert crawler.page is not None

    # crawler.render(timeout=5)

    error_crawler = SimpleCrawler(error_url)
    error_crawler.crawl()
    assert error_crawler.page is None


def test_SelC_get_element(url):
    crawler = SeleniumCrawler(url)
    crawler.crawl()
    assert (
        crawler.get_element("xpath", "//a/@href")
        == "https://www.iana.org/domains/example"
    )

    assert crawler.get_element("css", "h1").startswith("<h1>")

    with pytest_raises(ValueError):
        crawler.get_element("totally", "//a/@href")


def test_SimC_get_element(url):
    crawler = SimpleCrawler(url)
    crawler.crawl()

    assert (
        crawler.get_element("xpath", "//a/@href")
        == "https://www.iana.org/domains/example"
    )


@mark.asyncio
async def test_SelC_async(url):
    crawler = SeleniumCrawler(url)
    await crawler.async_crawl()
    assert crawler.page is not None


@mark.asyncio
async def test_SimC_async(url):
    crawler = SimpleCrawler(url)
    await crawler.async_crawl()
    assert crawler.page is not None
