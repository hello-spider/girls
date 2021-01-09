import scrapy
import re
import os
from concurrent.futures import ThreadPoolExecutor

from scrapy.http import Response, Request

BASE_DIR = '/Volumes/T7/tmp/mm131_net'

thread_pool = ThreadPoolExecutor(max_workers=5)


class MainSpider(scrapy.Spider):
    name = 'main'
    allowed_domains = ['mm131.net']

    def closed(self, reason):
        thread_pool.shutdown()

    def start_requests(self):
        category_urls = [
            'https://www.mm131.net/xinggan/',
            'https://www.mm131.net/qingchun/',
            'https://www.mm131.net/xiaohua/',
            'https://www.mm131.net/chemo/',
            'https://www.mm131.net/qipao/',
            'https://www.mm131.net/mingxing/',
        ]
        for url in category_urls:
            yield Request(url, callback=self.parse_category_page)

    def parse_category_page(self, response: Response) -> None:
        # girls in the page
        girl_page_urls = response.css('.list-left dd:not(.page) a::attr(href)').getall()
        yield from response.follow_all(girl_page_urls, callback=self.parse_image_page)

        # other pages
        category_page_urls = response.css('.page a::attr(href)').getall()
        yield from response.follow_all(category_page_urls, callback=self.parse_category_page)

    def parse_image_page(self, response: Response):
        # other image page links
        image_page_links = response.css('.content-page a::attr(href)').getall()

        image_title = response.css('.content > h5::text').get()
        image_title = re.match(r'^(?P<title>.*?)(?P<index>\(\d+\))?$', image_title).groupdict().get('title')
        image_url = response.css('.content-pic img::attr(src)').get()

        meta = {'image_title': image_title}
        yield response.follow(image_url, callback=self.save_image, dont_filter=True, meta=meta)
        yield from response.follow_all(image_page_links, callback=self.parse_image_page)

    def save_image(self, response: Response):
        save_dir = self.settings['SAVE_DIR']
        def func():
            image_title = response.meta['image_title']
            image_url = response.url
            path = os.path.join(save_dir, image_title, image_url.split('/')[-1])
            try:
                with open(path, 'wb') as f:
                    f.write(response.body)
            except FileNotFoundError:
                os.makedirs(os.path.dirname(path))
                with open(path, 'wb') as f:
                    f.write(response.body)

        thread_pool.submit(func)
