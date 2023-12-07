
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
