import os

from scrapy.spiders import CrawlSpider
from scrapy import Request
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor


class MainSpider(CrawlSpider):
    name = 'rules'
    allowed_domains = ['kindgirls.com']
    rules = (
        Rule(LinkExtractor(allow=r'https://www\.kindgirls\.com/girls\.php?.*')),
        Rule(LinkExtractor(allow=r'https://www\.kindgirls\.com/gallery-full\.php?.*'),
             callback='parse_gallery_full'),
        Rule(LinkExtractor(allow=r'.*?\.mp4', deny_extensions=[]), callback='save_video'),
        Rule(LinkExtractor(deny=r'.*?\.jpg')),
    )

    def start_requests(self):
        yield from self.start_initial_requests()

    def start_initial_requests(self):
        initials = [chr(i) for i in range(ord('a'), ord('z') + 1)]
        urls = [f'https://www.kindgirls.com/girls.php?i={initial}'
                for initial in initials]
        yield from (Request(url) for url in urls)

    def parse_gallery_full(self, response):
        img_urls = response.css('.gal_full img::attr(src)').getall()
        yield from response.follow_all(img_urls, callback=self.save_image)

    def save_file(self, file_path, content):
        try:
            with open(file_path, 'wb') as f:
                f.write(content)
        except FileNotFoundError:
            file_folder = os.path.dirname(file_path)
            os.makedirs(file_folder)
            with open(file_path, 'wb') as f:
                f.write(content)

    def save_image(self, response):
        save_dir = self.settings.get('SAVE_DIR')
        file_name = response.url.split('/')[-1]
        girl_name = file_name.rsplit('_', 2)[0]
        file_path = os.path.join(save_dir, girl_name, file_name)
        self.save_file(file_path, response.body)

    def save_video(self, response):
        save_dir = self.settings.get('SAVE_DIR')
        video_folder = os.path.join(save_dir, 'videos')
        file_name = response.url.split('/')[-1]
        file_path = os.path.join(video_folder, file_name)
        self.save_file(file_path, response.body)
