import csv
import json
import logging
import os
import threading
from queue import Queue
from typing import Dict

import yaml
from dataclasses import dataclass, field
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

from models import RequestHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)


@dataclass
class FileHandler:
    filepath: str
    lock: threading.Lock = threading.Lock()

    def write_to_csv(self, data):
        with self.lock, open(self.filepath, 'w', newline='', encoding='utf-8') as _file:
            writer = csv.writer(_file)
            writer.writerows(data)

    def read_from_csv(self):
        with self.lock, open(self.filepath, 'r', encoding='utf-8') as _file:
            reader = csv.reader(_file)
            data = [row for row in reader]
        return data


@dataclass
class CompanyScraper(RequestHandler):
    config: Dict
    _page = None

    playwright = sync_playwright()

    def __post_init__(self):
        super().__init__()
        self._cookies = None
        self._config_internal = self.config.get('internal', {})
        self._page = self.get_shared_page()
        self.login()

    @classmethod
    def get_shared_page(cls):
        if cls._page is None:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True)
                context = browser.new_context()
                page = context.new_page()
                stealth_sync(page)
                cls._page = page
        return cls._page

    def login(self):
        username = self.config['credentials']['username']
        if not os.path.exists(f"cookies/{username}.json"):
            logging.info(f"Cookies not found for {username}")
            page = self._login_new_user(username)
            self._page = page
        else:
            logging.info(f"Cookies found for {username}")
            filename = os.path.join(os.getcwd(), 'cookies', f"{username}.json")
            with open(filename, 'r') as _file:
                content = json.loads(_file.read())
                self._cookies = content
                if not self.test_cookie():
                    os.remove(filename)
                    self.sign_in(self._page, self.config)
                else:
                    logging.info(f"Cookies loaded from {username}.json")

    def _login_new_user(self, username):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            stealth_sync(page)
            login_page = self.config['linkedin']['login_page']
            page.goto(login_page)
            page.wait_for_load_state("load")
            self.sign_in(page, self.config)
            logging.info("Logged in successfully")
            self._save_cookies(page, username)
            return page

    def _save_cookies(self, page, username):
        cookies = page.context.cookies()
        with open(f"cookies/{username}.json", 'w') as _file:
            json.dump(cookies, _file)
            self.cookies = cookies

    def test_cookie(self):
        with self.playwright as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            page.context.add_cookies(self._cookies)
            page.goto("https://www.linkedin.com/feed/")
            page.wait_for_load_state("load")
            cookie_validity = not page.is_visible("text=Sign in")
            logging.info("Cookies are valid" if cookie_validity else "Cookies are invalid")
            return cookie_validity

    def search_on_bar(self, company):
        with self.playwright as playwright:
            browser = playwright.chromium.launch(headless=True, slow_mo=50)
            context = browser.new_context()
            page = context.new_page()
            page.context.add_cookies(self._cookies)
            page.goto("https://www.linkedin.com/feed/")
            search_bar_xpath = page.locator(self.config['linkedin']['search_bar_xpath'])
            search_bar_xpath.fill(company)
            search_bar_xpath.press("Enter")
            page.wait_for_load_state("load")
            first_element = self.config['linkedin']['first_search_element_xpath']
            page.locator(first_element).click()
            page.wait_for_load_state("load")
            link = page.url
            logging.info(f"Found link for {company}: {link}")
            return link


class ScrapperThread(threading.Thread):
    def __init__(self, _config):
        super().__init__()
        self.config = _config

    def run(self):
        logging.info(f"Starting scraper thread {self.name}")
        company_scraper = CompanyScraper(self.config)
        while True:
            value = self.config['input_queue'].get(timeout=1)
            if isinstance(value, list):
                for v in value:
                    self.config['input_queue'].put(v)
            else:
                company_scraper.search_on_bar(value)


def main():
    with open('configuration.yml', 'r') as file:
        config = yaml.safe_load(file)

    queues = ['input_queue', 'output_queue', 'csv_queue']
    config.update({queue: Queue() for queue in queues})

    file_input = FileHandler(config['files']['input_companies'])
    file_output = FileHandler(config['files']['output_companies'])
    input_companies = file_input.read_from_csv()

    for company in input_companies:
        config['input_queue'].put([company])
        logging.info(f"Added {company} to input queue")

    config['output_queue'] = file_output

    scraper = ScrapperThread(config)
    scraper.start()


if __name__ == '__main__':
    main()
