import os
import scrapy
from scrapy import Request
from scrapy.http import Response
from scrapy.spiders import CrawlSpider, Spider


class MainSpider(Spider):
    name = 'main'
    allowed_domains = ['kindgirls.com']

    def start_requests(self):
        # yield from self.start_initial_requests()
        url = 'https://vids.kindgirls.com/dvv9/stella-cardo-2.mp4'
        yield Request(url, callback=self.save_video)

    def start_initial_requests(self):
        initials = [chr(i) for i in range(ord('a'), ord('z') + 1)]
        urls = [f'https://www.kindgirls.com/girls.php?i={initial}'
                for initial in initials]
        yield from (Request(url, callback=self.parse_initial)
                    for url in urls)

    def parse_initial(self, response):
        girl_urls = response.css('.model_list a::attr(href)').getall()
        yield from response.follow_all(girl_urls, callback=self.parse_girl)

    def parse_girl(self, response):
        gallery_urls = response.css('.gal_list a::attr(href)').getall()
        gallery_full_urls = [gallery_url.replace('gallery.php', 'gallery-full.php')
                             for gallery_url in gallery_urls]
        yield from response.follow_all(gallery_full_urls, callback=self.parse_gallery_full)

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
