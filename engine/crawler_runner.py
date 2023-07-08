from engine.crawler import Crawler
from engine.crawler_queue import CrawlerQueue
from engine.crawler_request import CrawlerRequest
from engine.crawler_response import CrawlerResponse
from engine.url_extractor import UrlExtractor


class CrawlerRunner:
    def __init__(self, crawler: Crawler):
        self.crawler = crawler
        self.crawler_queue = CrawlerQueue(crawler_name=self.crawler.crawler_name)
        self.rules = None

    def run(self):
        self.rules = self.__get_crawler_rules()

        first_request = True
        crawler_response = self.__run_star_crawler()

        while True:
            if first_request:
                first_request = False
                self.__add_urls_to_queue(crawler_response=crawler_response)

            next_request_url = self.crawler_queue.get_request_from_queue()
            if not next_request_url:
                print('todas as request feitas')
                return True
            next_request = CrawlerRequest(site_url=next_request_url)

            crawler_response = self.crawler.process_request(crawler_request=next_request)
            self.crawler.parse_crawler_response(crawler_response=crawler_response)

    def __add_urls_to_queue(self, crawler_response: CrawlerResponse):
        urls_to_extract = UrlExtractor.get_urls(
            html_body=crawler_response.site_body,
            regex_rules=self.rules,
            site_domain=self.crawler.site_domain,
            internet_protocol=self.crawler.internet_protocol)

        for url in urls_to_extract:
            self.crawler_queue.add_request_to_queue(url=url)

    def __run_star_crawler(self) -> CrawlerResponse:
        crawler_response = self.crawler.start_crawler()
        if not isinstance(crawler_response, CrawlerResponse):
            raise ValueError('star_crawler return type must be a CrawlerResponse')
        return crawler_response

    def __get_crawler_rules(self):
        return self.crawler.extraction_rules()
