import scrapy
from scrapy_playwright.page import PageMethod
from urllib.parse import urljoin

# from helper import should_abort_request


class LazadaSpiderSpider(scrapy.Spider):
    name = 'ssg_spider'

    global HEADERS

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }

    custom_settings = {
        'FEEDS': {'data/%(name)s_%(time)s.csv': {'format': 'csv', }},
        'PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT': '100000'
    }

    def start_requests(self):
        keyword_list = list(map(str, input('Search Keywords : ').split(',')))
        pages = int(input("Max Crawl Pages : "))

        for keyword in keyword_list:
            for page in range(1, int(pages)+1):
                search_url = f'https://www.ssg.com/search.ssg?target=all&query={keyword}&count=40&page={page}'

                yield scrapy.Request(
                    url=search_url,
                    callback=self.parse,
                    headers=HEADERS,
                    meta={"playwright": True,
                          "playwright_page_methods": [
                              PageMethod("wait_for_selector", '[data-unittype="item"]'),
                          ],
                          },
                )

    def parse(self, response):
        products_selector = response.css('[data-unittype="item"]')

        for product in products_selector:
            #link = response.urljoin(product.xpath('.//a[text()]/@href').get())

            relative_url = product.css('a.clickable::attr(href)').get()
            product_url = urljoin('https://www.ssg.com', relative_url) #.split("?")[0]
            yield scrapy.Request(product_url, callback=self.parse_product, headers=HEADERS, meta={"playwright": False})

    def parse_product(self, response):
        yield {
            "product_href": response.request.url,
            "product_src": response.css('div.zoomWindow > img::attr(src)').get(),
            'product_title': response.css('h2.cdtl_info_tit ::Text').get(),
            'product_price': response.css('em.ssg_price ::Text').get(),
            'product_seller': response.css('span.cdtl_store_tittx ::Text').get()
        }
