import json
from datetime import datetime
from urllib.parse import urljoin
import scrapy

# variable to determine page to start from
from scrapy.crawler import CrawlerProcess

page_no = 1
# variable to determine number of pages to scrape
pages_to_scrape_count = 1
scrape_counter = 0
all_data = []
start_page = 1
no_to_crawl = 1

class StackbotSpider(scrapy.Spider):
    name = 'stackbot'
    # allowed_domains = ['x']
    start_urls = [f"https://stackoverflow.com/jobs?pg={page_no}"]

    def parse(self, response):
        global scrape_counter
        scrape_counter += 1
        urls = response.css("h2 > a.s-link::attr(href)").getall()

        for link in urls:
            url = urljoin(response.url, link)
            yield scrapy.Request(url, callback=self.get_details)
        global page_no
        global pages_to_scrape_count
        page_no += 1
        if scrape_counter <= pages_to_scrape_count:
            next_page = f"https://stackoverflow.com/jobs?pg={page_no}"
            yield response.follow(next_page, callback=self.parse)

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
            "job_description ": job_description,
            "company_location": company_location,
            "company_name": company_name,
            "company_url": company_url,
            "company_size": company_size,
            "company_type": company_type
        }
        all_data.append(data)
        yield data


from scrapy import cmdline


def save_file(data):
    with open(f'jobs-pg{start_page}to{start_page + no_to_crawl - 1}.json', 'w') as f:
        f.write(json.dumps(data))


if __name__ == '__main__':

    try:
        page_no = int(input("enter start page number"))
        start_page = page_no
    except:
        print("invalid format, default of 1 will be used")

    try:
        pages_to_scrape_count = int(input("enter number of pages to scrape"))
        no_to_crawl = pages_to_scrape_count
    except:
        print("invalid format, default of 1 will be used")
    process = CrawlerProcess(
        #     {
        #     'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
        # }
    )

    process.crawl(StackbotSpider)
    process.start()
    save_file(all_data)

    # cmdline.execute("scrapy crawl stackbot -O jobs.json".split())
