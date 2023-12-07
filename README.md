
# LinkedIn Playwright Scraper

This project automates LinkedIn data scraping using Playwright, fetching details of companies from a provided list.

## Why Use This Project?

- **Automated Data Extraction**: Efficiently retrieves LinkedIn company details from a list of companies.
- **Reliable Automation**: Utilizes Playwright for browser automation, ensuring stability and reliability in web interactions.
- **Configurability**: Supports configurations via a YAML file to set login credentials, LinkedIn URLs, and file paths.

## How to Run

### Installation

- Ensure you have Python installed (preferably Python 3.x).
- Install Pipenv (if not already installed):
  ```bash
  pip install pipenv
  ```

### Setup

- Clone the repository and navigate to the project directory.
- Install dependencies using Pipenv:
  ```bash
  pipenv install
  ```

### Configuration

- Modify the `configuration.yml` file:
  - Set your LinkedIn `credentials`.
  - Define LinkedIn URLs and necessary settings.

### Login Information:

- The initial login checks for the existence of a cookie file on disk to load it. If no cookie exists, it performs a login using provided credentials and saves the cookies for subsequent logins.
- MFA (Multi-Factor Authentication) is supported. Upon login, if MFA is enabled for the account, the script prompts for an MFA code received via email. Enter the code in the terminal to continue the login process through Playwright.
- Note: Please adhere to LinkedIn's terms of service and data privacy policies while using this tool. Use responsibly and ethically.

### Execution

- Activate the virtual environment:
  ```bash
  pipenv shell
  ```
- Run the script `main.py`:
  ```bash
  python main.py
  ```
  The program reads input companies from the CSV file, initiates the scraping process, and writes results to an output file.

## Requirements

- Python 3.x
- Dependencies listed in `Pipfile`
