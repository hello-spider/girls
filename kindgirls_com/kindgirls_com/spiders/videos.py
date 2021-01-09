import os

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


class MainSpider(CrawlSpider):
    name = 'videos'
    allowed_domains = ['kindgirls.com']
    start_urls = ['https://www.kindgirls.com/video-archive.php']
    rules = (
        Rule(LinkExtractor(allow=r'https://www\.kindgirls\.com/video-archive\.php')),
        Rule(LinkExtractor(allow=r'https://www\.kindgirls\.com/video\.php'),
             callback='download_video'),
    )
    count = 0

    def save_file(self, file_path, content):
        try:
            with open(file_path, 'wb') as f:
                f.write(content)
        except FileNotFoundError:
            file_folder = os.path.dirname(file_path)
            os.makedirs(file_folder)
            with open(file_path, 'wb') as f:
                f.write(content)

    def get_video_path(self, url):
        save_dir = self.settings.get('SAVE_DIR')
        video_folder = os.path.join(save_dir, 'videos')
        file_name = url.split('/')[-1]
        file_path = os.path.join(video_folder, file_name)
        return file_path

    def download_video(self, response):
        video_url = response.css('video source[type=video\/mp4]::attr(src)').get()
        file_path = self.get_video_path(video_url)
        if os.path.exists(file_path):
            return
        yield response.follow(video_url, callback=self.save_video)

    def save_video(self, response):
        file_path = self.get_video_path(response.url)
        self.save_file(file_path, response.body)
