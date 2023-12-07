import csv
import json
import logging
import os
import threading
from pprint import pprint
from threading import Thread
from queue import Queue
from typing import Dict

import yaml
from dataclasses import dataclass, field

from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

from models import RequestHandler

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", handlers=[logging.StreamHandler()]
)


@dataclass
class FileHandler:
    filepath: str
    lock: threading.Lock = threading.Lock()

    def write_to_csv(self, data):
        with self.lock:
            with open(self.filepath, 'w', newline='', encoding='utf-8') as _file:
                writer = csv.writer(_file)
                writer.writerows(data)

    def read_from_csv(self):
        with self.lock:
            data = []
            with open(self.filepath, 'r', encoding='utf-8') as _file:
                reader = csv.reader(_file)
                for row in reader:
                    if isinstance(row, list):
                        data.extend(row)
                    else:
                        data.append(row)
                return data


@dataclass
class CompanyScraper(RequestHandler):
    config: Dict

    config_internal: Dict = field(init=False)
    credentials: Dict = field(init=False)

    playwright = sync_playwright()
    _page = None

    def __post_init__(self):
        super(RequestHandler).__init__()
        self._cookies = None
        self.login()

    def __call__(self, *args, **kwargs):
        return self.playwright

    def __enter__(self):
        return self.playwright

    def __exit__(self, exc_type, exc_value, traceback):
        if any([exc_type, exc_value, traceback]):
            logging.error(f"Exception occurred in {self.__class__.__name__}")
            logging.error(f"Exception type: {exc_type}")
            logging.error(f"Exception value: {exc_value}")
            logging.error(f"Traceback: {traceback}")
        return self.playwright.__exit__()

    @property
    def cookies(self):
        return self._cookies

    @cookies.setter
    def cookies(self, cookies):
        self._cookies = cookies

    @property
    def page(self):
        return self._page

    @page.setter
    def page(self, page):
        self.page = page

    def login(self):
        username = self.config['credentials']['username']
        if not os.path.exists(f"cookies/{username}.json"):
            logging.info(f"Cookies not found for {username}")
            page = self._login_new_user(username)
            self.page = page
        else:
            logging.info(f"Cookies found for {username}")
            filename = os.path.join(os.getcwd(), 'cookies', f"{username}.json")
            with open(filename, 'r') as _file:
                content = json.loads(_file.read())
                self.cookies = content
                if not self.test_cookie():
                    os.remove(filename)
                    self.sign_in(self.page, self.config)
                else:
                    logging.info(f"Cookies loaded from {username}.json")

    def _login_new_user(self, username):
        with self.playwright as playwright:
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
            page.context.add_cookies(self.cookies)
            page.goto("https://www.linkedin.com/feed/")
            page.wait_for_load_state("load")
            if page.is_visible("text=Sign in"):
                logging.info("Cookies are invalid")
                return False
            logging.info("Cookies are valid")
            return True

    def search_on_bar(self, company):
        with self.playwright as playwright:
            browser = playwright.chromium.launch(headless=True, slow_mo=50)
            context = browser.new_context()
            page = context.new_page()
            page.context.add_cookies(self.cookies)
            page.goto("https://www.linkedin.com/feed/")
            search_bar_xpath = page.locator(self.config['linkedin']['search_bar_xpath'])
            search_bar_xpath.fill(company)
            search_bar_xpath.press("Enter")
            page.wait_for_load_state("load")
            first_element = self.config['linkedin']['first_search_element_xpath']
            page.locator(first_element).click()
            page.wait_for_load_state("load")
            # get browser url
            link = page.url
            logging.info(f"Found link for {company}: {link}")
            return link

class ScrapperThread(Thread):
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


if __name__ == '__main__':
    with open('configuration.yml', 'r') as file:
        config = yaml.safe_load(file)

    for i in ['input_queue', 'output_queue', 'csv_queue']:
        config[i] = Queue()

    file_input = FileHandler(config['files']['input_companies'])
    file_output = FileHandler(config['files']['output_companies'])
    input_companies = file_input.read_from_csv()

    for i in input_companies:
        config['input_queue'].put([i])
        logging.info(f"Added {i} to input queue")

    config['output_queue'] = file_output

    scraper = ScrapperThread(config)
    scraper.start()
