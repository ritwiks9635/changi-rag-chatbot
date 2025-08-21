import scrapy
from urllib.parse import urlparse
from airport_crawler.items import PageContentItem
from bs4 import BeautifulSoup

class ChangiSpider(scrapy.Spider):
    name = "changi_spider"
    allowed_domains = ["changiairport.com", "jewelchangiairport.com"]

    start_urls = [
        "https://www.changiairport.com/",
        "https://www.jewelchangiairport.com/"
    ]

    custom_settings = {
        "DEPTH_LIMIT": 3,  # crawl deep but controlled
        "DOWNLOAD_DELAY": 0.5,
        "ROBOTSTXT_OBEY": True,
        "FEEDS": {
            "data/scraped_pages.json": {
                "format": "json",
                "encoding": "utf8",
                "overwrite": True
            }
        },
    }

    def parse(self, response):
        # Clean up unwanted tags using BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "noscript", "svg", "img", "header", "footer"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        content = "\n".join(lines)

        yield PageContentItem(url=response.url, content=content)

        # follow internal links
        for href in response.css("a::attr(href)").getall():
            full_url = response.urljoin(href)
            if self._is_valid(full_url):
                yield response.follow(full_url, callback=self.parse)

    def _is_valid(self, url):
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and any(domain in parsed.netloc for domain in self.allowed_domains)
