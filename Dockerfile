FROM python:3.9

WORKDIR /app

COPY . /app

RUN pip install pipenv
RUN pipenv install --system --deploy --ignore-pipfile

RUN apt-get update && apt-get install -y supervisor
# playwright install
RUN apt-get install -y wget gnupg ca-certificates apt-transport-https
RUN wget -qO - https://playwright.dev/docs/api/md/docs/cli/playwright-cli.md | grep -oP 'https://playwright.azureedge.net/[^"]+' | xargs -n1 wget -qO -
RUN apt-get install -y ./playwright-1.14.0-focal_amd64.deb
RUN playwright install

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
