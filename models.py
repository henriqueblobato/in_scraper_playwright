import json
from abc import ABC, abstractmethod
from dataclasses import dataclass

import yaml


@dataclass
class RequestHandler(ABC):
    def sign_in(self, page, configuration):
        """Performs login if the login modal is present on the page"""
        username_xpath = page.locator(configuration['linkedin']['username_xpath'])
        password_xpath = page.locator(configuration['linkedin']['password_xpath'])
        sign_in_button_xpath = page.locator(configuration['linkedin']['sign_in_button_xpath'])
        username_value = configuration['credentials']['username']
        password_value = configuration['credentials']['password']
        username_xpath.fill(username_value)
        password_xpath.fill(password_value)
        sign_in_button_xpath.click()
        page.wait_for_load_state("load")
        self.check_mfa(page, configuration)
        cookies = page.context.cookies()
        username = configuration['credentials']['username']
        with open(f"cookies/{username}.json", 'w') as _file:
            _file.write(json.dumps(cookies, indent=4))
            print(f"Cookies saved to {username}.json")

    def check_mfa(self, page, configuration):
        """Checks if MFA is enabled for the account and enters the MFA code if it is enabled"""
        username = configuration['credentials']['username']
        if page.is_visible(configuration['mfa']['mfa_input_xpath']):
            mfa_code = input("Enter the MFA code: ")
            mfa_input = page.locator(configuration['mfa']['mfa_input_xpath'])
            mfa_input.fill(mfa_code)
            mfa_verify_button = page.locator(configuration['mfa']['mfa_verify_button_xpath'])
            mfa_verify_button.click()
            page.wait_for_load_state("load")
            print(f"MFA verified successfully for {username}")
        else:
            print(f"MFA not enabled for {username}")
