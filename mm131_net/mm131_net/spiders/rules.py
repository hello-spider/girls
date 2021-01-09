import os
import re
from concurrent.futures import ThreadPoolExecutor

from scrapy.http import Response
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

thread_pool = ThreadPoolExecutor(max_workers=1)


class MainSpider(CrawlSpider):
    name = 'rules'

    allowed_domains = ['mm131.net']
    start_urls = ['https://www.mm131.net']
    categories = (
        'xinggan',
        'qingchun',
        'xiaohua',
        'chemo',
        'qipao',
        'mingxing',
    )
    cat_str = '|'.join(categories)

    image_page_le = LinkExtractor(allow=rf"^https://www\.mm131\.net/({cat_str})/\d+(_\d+)?\.html$")

    rules = (
        Rule(image_page_le, callback='parse_image_page', follow=True),  # image page
        Rule(follow=True),  # others
    )

    def parse_image_page(self, response: Response):
        image_title = response.css('.content > h5::text').get()
        image_title = re.match(r'^(?P<title>.*?)(?P<index>\(\d+\))?$', image_title).groupdict().get('title')
        image_url = response.css('.content-pic img::attr(src)').get()
        meta = {'image_title': image_title}
        yield response.follow(image_url, callback=self.save_image, dont_filter=True, meta=meta)

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
