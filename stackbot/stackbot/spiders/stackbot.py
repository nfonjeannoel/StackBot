import json
from datetime import datetime
from urllib.parse import urljoin
import scrapy
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from time import sleep
from pathlib import Path
# variable to determine page to start from
from scrapy import crawler
from scrapy.crawler import CrawlerProcess

# variable to determine number of pages to scrape
pages_to_scrape_count = 4
scrape_counter = 0
all_data = []

pagination_counter = 1


class StackbotSpider(scrapy.Spider):
    name = 'stackbot'
    start_urls = [
        f"https://www-stackoverflow-com.translate.goog/jobs?pg={scrape_counter}&_x_tr_sl=en&_x_tr_tl=en&_x_tr_hl=en&_x_tr_pto=sc",
        f"https://www-stackoverflow-com.translate.goog/jobs/?pg={scrape_counter+1}&_x_tr_sl=en&_x_tr_tl=en&_x_tr_hl=en&_x_tr_pto=sc"
    ]

    # start_urls = [f"https://stackoverflow.com/jobs?pg={page_no}"]

    def parse(self, response):
        urls = response.css("h2 > a.s-link::attr(href)").getall()
        for link in urls:
            response.follow(url=link, callback=self.get_details)

    def get_details(self, response):
        title = response.css(".mb4 .fc-black-900::text").get()
        location = response.css("div.flex--item.fl1.sticky\:ml2 > div > span::text").get()
        if len(location.split()[0]) == 1:
            location = " ".join(location.split()[1:])
        salary = response.css("ul.horizontal-list li::attr(title)").get()
        industry = response.css(
            "#overview-items > section:nth-child(2) > div > div:nth-child(1) > div:nth-child(3) > span.fw-bold::text").get()
        work_type = response.css("div.flex--item.fl1.sticky\:ml2 > ul > li:nth-child(2) > span::text").get()
        job_type = response.css(
            "#overview-items > section:nth-child(2) > div > div:nth-child(1) > div:nth-child(1) > span.fw-bold::text").get()
        experience_level = response.css(
            "#overview-items > section:nth-child(2) > div > div:nth-child(1) > div:nth-child(2) > span.fw-bold::text").get()
        job_description = response.css("#overview-items > section.mb32.fs-body2.fc-medium > div p::text").getall()
        company_location = response.css("div.mb4 span.fc-black-500::text").get()
        if len(company_location.split()[0]) == 1:
            company_location = " ".join(company_location.split()[1:])
        company_name = response.css("div.mb4 .fc-black-700::text").get()
        company_url = urljoin(response.url, response.css("div.mb4 .fc-black-700::attr(href)").get())
        company_size = response.css(
            "#overview-items > section:nth-child(2) > div > div:nth-child(2) > div:nth-child(2) > span.fw-bold::text").get()

        company_type = response.css(
            "#overview-items > section:nth-child(2) > div > div:nth-child(2) > div:nth-child(1) > span.fw-bold::text").get()

        data = {
            "title": title,
            "location": location,
            "salary ": salary,
            "industry ": industry,
            "work_type": work_type,
            "job_type": job_type,
            "experience_level": experience_level,
            "job_url": response.url,
            "job_description ": job_description,
            "company_location": company_location,
            "company_name": company_name,
            "company_url": company_url,
            "company_size": company_size,
            "company_type": company_type
        }

        # follow the link to about page and pass data as argument

        more_info_url = response.css("#content .truncate ::attr(href)").get()
        print(data)
        if more_info_url is None:
            all_data.append(data)
            print(f"page {title} does not contain more information")
            return
        yield response.follow(url=more_info_url, callback=self.get_more_info, meta={"basic_info": data})

    def get_more_info(self, response):
        data = response.meta.get("basic_info")
        about = {"website": response.css(".d-block .js-gps-track ::attr(href)").get(),
                 "industry": response.css(".mt12 > .d-block ::text").get(),
                 "size": response.css(".mt12:nth-child(3) .flex--item:nth-child(1) .d-block ::text").get(),
                 "founded": response.css(".mt12:nth-child(3) .flex--item:nth-child(2) .d-block ::text").get(),
                 "status": response.css(".mt12:nth-child(3) .flex--item:nth-child(3) .d-block ::text").get(),
                 "followers": response.css(".flex__fl1+ .mt12 .d-block ::text").get(),
                 "social_links": response.css("#right-column .flex--item .js-gps-track ::attr(href)").getall()}
        data["about"] = about
        all_data.append(data)


def save_file(data):
    with open(f'jobs{scrape_counter}.json', 'w') as f:
        f.write(json.dumps(data))


if __name__ == '__main__':
    # process = CrawlerProcess()
    # process.crawl(StackbotSpider)
    # process.start()
    # save_file(all_data)
    # process = CrawlerProcess()
    # process.crawl(StackbotSpider)
    # scrape_counter will be used to get the pg variable for the url
    for scrape_counter in range(1, 20, 2):
        process = CrawlerProcess()
        process.crawl(StackbotSpider)
        process.start()
        process.stop()
        save_file(all_data)
        all_data = []
        # sleeping 30 munites
        sleep(30)
