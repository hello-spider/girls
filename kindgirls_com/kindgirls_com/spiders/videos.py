import os

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


class MainSpider(CrawlSpider):
    name = 'videos'
    allowed_domains = ['kindgirls.com']
    start_urls = ['https://www.kindgirls.com/video-archive.php']
    rules = (
        Rule(LinkExtractor(allow=r'https://www\.kindgirls\.com/video-archive\.php')),
        Rule(LinkExtractor(allow=r'https://www\.kindgirls\.com/video\.php')),
        Rule(LinkExtractor(allow=r'.*?\.mp4', tags='source', attrs='src', deny_extensions=[]),
             callback='save_video'),
    )

    def save_file(self, file_path, content):
        try:
            with open(file_path, 'wb') as f:
                f.write(content)
        except FileNotFoundError:
            file_folder = os.path.dirname(file_path)
            os.makedirs(file_folder)
            with open(file_path, 'wb') as f:
                f.write(content)

    def save_video(self, response):
        save_dir = self.settings.get('SAVE_DIR')
        video_folder = os.path.join(save_dir, 'videos')
        file_name = response.url.split('/')[-1]
        file_path = os.path.join(video_folder, file_name)
        self.save_file(file_path, response.body)
