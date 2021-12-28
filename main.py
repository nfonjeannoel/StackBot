import json
from time import sleep

import requests
from scrapy import Selector


class StackSpider:
    all_data = []

    def crawl(self):
        for scrape_counter in range(1, 20, 2):
            urls = [
                f"https://stackoverflow.com/jobs?pg={scrape_counter}",
                f"https://stackoverflow.com/jobs?pg={scrape_counter + 1}"
            ]
            for url in urls:
                response = requests.get(url=url)
                # print(response.text)
                selector = Selector(text=response.text)
                # pri
                self.parse(selector)
            self.save_data(scrape_counter)

            sleep(30 * 60)

    def parse(self, response):
        urls = response.css("h2 > a.s-link::attr(href)").getall()
        for job_link in urls:
            # join url
            job_link = "https://stackoverflow.com" + job_link
            response = requests.get(url=job_link)

            self.get_details(Selector(text=response.text), job_link)

    def get_details(self, response, job_link):
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
        company_size = response.css(
            "#overview-items > section:nth-child(2) > div > div:nth-child(2) > div:nth-child(2) > span.fw-bold::text").get()

        company_type = response.css(
            "#overview-items > section:nth-child(2) > div > div:nth-child(2) > div:nth-child(1) > span.fw-bold::text").get()
        date_posted = response.css("#overview-items .mb24 li ::text").get()
        company_url = response.css(".sticky\:sm\:fs-caption .fc-black-700 ::text").get()
        data = {
            "title": title,
            "location": location,
            "salary ": salary,
            "industry ": industry,
            "work_type": work_type,
            "job_type": job_type,
            "experience_level": experience_level,
            "job_url": job_link,
            "company_url": company_url,
            "date_posted": date_posted,
            "job_description ": job_description,
            "company_location": company_location,
            "company_name": company_name,
            "company_size": company_size,
            "company_type": company_type,
            "about": {}
        }
        print(data)
        # follow the link to about page and pass data as argument
        more_info_url = response.css("#content .truncate ::attr(href)").get()
        if more_info_url is None:
            self.all_data.append(data)
            print(f"page {title} does not contain more information")
            return
        more_info_url = "https://www.stackoverflow.com" + more_info_url
        response = requests.get(url=more_info_url)
        self.get_more_info(Selector(text=response.text), data)

    def get_more_info(self, response, data):
        about = {"website": response.css(".d-block .js-gps-track ::attr(href)").get(),
                 "industry": response.css(".mt12 > .d-block ::text").get(),
                 "size": response.css(".mt12:nth-child(3) .flex--item:nth-child(1) .d-block ::text").get(),
                 "founded": response.css(".mt12:nth-child(3) .flex--item:nth-child(2) .d-block ::text").get(),
                 "status": response.css(".mt12:nth-child(3) .flex--item:nth-child(3) .d-block ::text").get(),
                 "followers": response.css(".flex__fl1+ .mt12 .d-block ::text").get(),
                 "social_links": response.css("#right-column .flex--item .js-gps-track ::attr(href)").getall()}
        data["about"] = about
        self.all_data.append(data)

    def save_data(self, scrape_counter):
        with open(f"jobs{scrape_counter}.json", "w") as f:
            f.write(json.dumps(self.all_data))
            self.all_data = []
        f.close()


crawler = StackSpider()
crawler.crawl()
