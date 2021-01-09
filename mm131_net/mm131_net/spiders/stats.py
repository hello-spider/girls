import scrapy
import re
import os

from scrapy.http import Response, Request

stats = []


def parse_category_page(response: Response) -> None:
    # girls in the page
    girl_page_urls = response.css('.list-left dd:not(.page) a::attr(href)').getall()
    yield from response.follow_all(girl_page_urls, callback=parse_image_page)

    # other pages
    category_page_urls = response.css('.page a::attr(href)').getall()
    yield from response.follow_all(category_page_urls, callback=parse_category_page)


def parse_image_page(response: Response):
    image_count = response.css('.page-ch::text').get()
    image_count = int(re.match(r'^共(\d+)页$', image_count).group(1))
    stats.append(image_count)


class StatsSpider(scrapy.Spider):
    name = 'stats'
    allowed_domains = ['mm131.net']

    def closed(self, reason):
        print(f'Statistics: {len(stats)} albums, {sum(stats)} pictures, {sum(stats) / len(stats)} pictures per album.')

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
            yield Request(url, callback=parse_category_page)
