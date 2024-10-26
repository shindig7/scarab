import asyncio
import http.server
import socketserver
import threading
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Literal

import aiohttp
import requests
from loguru import logger
from parsel import Selector
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry  # type: ignore
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager

from scarab.utils import open_browser, setup_loguru_intercept

setup_loguru_intercept()


UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    "(KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
)


class Crawler(ABC):
    def __init__(self, url: str):
        self.url = url
        self.page = None

    def crawl(self) -> None:
        logger.info(f"Starting crawl for {self.url}")
        try:
            self._crawl()
        except Exception as e:
            logger.error(f"Failed to crawl {self.url}")
            logger.error(e)
        finally:
            if hasattr(self, "driver"):
                self.driver.quit()

    @abstractmethod
    def _crawl(self) -> None:
        pass

    def get_element(
        self, method: Literal["xpath", "css", "class", "id"], filter_value: str
    ):
        selector = Selector(text=self.page)
        match method:
            case "xpath":
                return selector.xpath(filter_value).get()
            case "css":
                return selector.css(filter_value).get()
            case "class":
                return selector.xpath(f"//*[@class='{filter_value}']").get()
            case "id":
                return selector.xpath(f"//*[@id='{filter_value}']").get()
            case _:
                raise ValueError(
                    f"Invalid method: must be 'xpath', 'class', or 'id'. Currently: {method}"
                )

    def render(
        self, path: Path = Path("/tmp"), port: int = 1234, timeout: int = 60
    ) -> None:
        with open(path / "index.html", "w") as f:
            f.write(self.page)

        class Handler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=str(path), **kwargs)

        def shutdown_server(httpd):
            logger.info(f"Server shutting down after {timeout} seconds")
            httpd.shutdown()

        # Start the browser opening function in a separate thread
        threading.Timer(1, open_browser).start()

        with socketserver.TCPServer(("", port), Handler) as httpd:
            logger.info(f"Serving on http://localhost:{port}")
            shutdown_timer = threading.Timer(
                timeout, shutdown_server, args=(httpd,)
            )
            shutdown_timer.start()
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                pass
            finally:
                shutdown_timer.cancel()
                logger.info("Server shutting down")


class SimpleCrawler(Crawler):
    def __init__(self, url: str):
        super().__init__(url)
        self.session = self._get_session()

    def _get_session(
        retries: int = 5,
        backoff_factor: float = 0.5,
        status_forcelist: tuple[int, int, int] = (500, 502, 504),
    ) -> requests.Session:
        session = requests.Session()
        session.headers.update({"user-agent": UA})
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def _crawl(self):
        logger.info(f"Fetching {self.url}")
        response = requests.get(self.url)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch {self.url}")
        else:
            self.page = response.text
            self.status_code = response.status_code

    async def async_crawl(self):
        logger.info(f"Fetching {self.url}")
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch {self.url}")
                else:
                    self.page = await response.text()
                    self.status_code = response.status


class SeleniumCrawler(Crawler):
    def __init__(self, url: str, headless: bool = True):
        super().__init__(url)
        self.headless = headless
        self.driver: WebDriver = self._get_driver()

    def _get_driver(self) -> WebDriver:
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument("--headless")

        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--mute-audio")

        return webdriver.Chrome(
            service=ChromeService(
                executable_path=ChromeDriverManager().install()
            ),
            options=options,
        )

    def _crawl(self):
        logger.info(f"Fetching {self.url}")
        self.driver.get(self.url)
        self.page = self.driver.page_source

    async def async_crawl(self):
        logger.info(f"Fetching {self.url}")
        try:
            await asyncio.to_thread(self.driver.get, self.url)
            self.page = self.driver.page_source
        except Exception as e:
            logger.error(f"Failed to fetch {self.url}")
            logger.error(e)
        finally:
            await asyncio.to_thread(self.driver.quit)
