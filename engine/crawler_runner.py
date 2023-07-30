import time

from engine.crawler import Crawler
from engine.crawler_queue import CrawlerQueue
from engine.models import CrawlerRequest, CrawlerResponse
from engine.url_extractor import UrlExtractor


class CrawlerRunner:
    def __init__(self, crawler: type[Crawler], crawler_queue: CrawlerQueue):
        self.crawler = crawler
        self.crawler_queue = crawler_queue

    def run(self):
        self.crawler = self.crawler()
        self.crawler.start_crawler()

        crawler_response = self.crawler.crawler_first_request()
        self.__add_urls_to_queue(crawler_response=crawler_response)
        self.__process_crawler_queue()

        self.crawler.stop_crawler()

    def __process_crawler_queue(self):
        while True:
            next_crawler_request = self.crawler_queue.get_request_from_queue()
            if not next_crawler_request:
                print('All requests were made')
                return True

            time.sleep(self.crawler.time_between_requests)
            crawler_response = self.crawler.process_request(crawler_request=next_crawler_request)
            self.__add_urls_to_queue(crawler_response=crawler_response)

            self.crawler.parse_crawler_response(crawler_response=crawler_response)

    def __add_urls_to_queue(self, crawler_response: CrawlerResponse):
        urls_to_extract = UrlExtractor.get_urls(
            site_current_url=crawler_response.site_url,
            html_body=crawler_response.site_body,
            regex_rules=self.crawler.regex_rules,
            allowed_domains=self.crawler.allowed_domains)
        for url in urls_to_extract:
            crawler_request = CrawlerRequest(site_url=url)
            self.crawler_queue.add_request_to_queue(crawler_request=crawler_request)
