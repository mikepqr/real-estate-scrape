import logging
import os
import re
from datetime import datetime, timezone

import matplotlib.pyplot as plt
import pandas as pd
import requests
from lxml import html

csvfile = "data.csv"
plotfile = "data.png"
sites = [
    {
        "name": "redfin",
        "xpath": "//div[@class='statsValue']//span/text()",
    },
    {
        "name": "zillow",
        "xpath": (
            # find the button containing "Zestimate"
            "//button[contains(text(), 'Zestimate')]"
            # find its parent
            "/parent::node()"
            # find its span descendent containing a "$"
            "//span[contains(text(), '$')]/text()"
        ),
    },
]


def get_page(url: str) -> bytes:
    session = requests.Session()
    # User-Agent required otherwise you get blocked
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    if "SCRAPERAPI_KEY" in os.environ:
        logging.info("Configuring requests session to use scraper API")
        session.params = {
            "api_key": os.environ["SCRAPERAPI_KEY"],
            "url": url,
        }
        url = "http://api.scraperapi.com"
        logging.info(f"Start  getting {session.params['url']} via {url}")
    else:
        logging.info(f"Start  getting {url=}")
    response = session.get(url, timeout=60)
    logging.info(f"Finish getting {url=}")
    return response.content


def get_value(url: str, xpath: str) -> str:
    page = get_page(url)
    tree = html.fromstring(page)
    try:
        value = tree.xpath(xpath)[0]
        return re.sub(r"[\$,\,]", "", value)
    except IndexError:
        logging.error(f"Could not find {xpath=} in {url=}")
        logging.error(f"Last 1000 characters of page: {page[-1000:].decode()}")
        raise


def retry_get_value(url: str, xpath: str, n: int = 3) -> str:
    exceptions = 0
    while exceptions < n:
        logging.info(f"Start  scrape {exceptions+1}/{n}: {url=} {xpath}")
        try:
            value = get_value(url, xpath)
            logging.info(f"Finish scrape {exceptions+1}/{n}. {value=}")
            return value
        except Exception as e:
            logging.error(f"Finish scrape {exceptions+1}/{n}. Failed: {e}")
            exceptions += 1
    return "NaN"


def ensure_csv() -> None:
    """Make sure a CSV with the appropriate header exists."""
    expected_header = "date," + ",".join(site["name"] for site in sites) + "\n"
    try:
        with open(csvfile) as f:
            header = next(f)
            assert header == expected_header
    except (FileNotFoundError, AssertionError):
        with open(csvfile, mode="w") as f:
            f.write(expected_header)


def append_csv(values) -> None:
    # https://stackoverflow.com/a/28164131/409879
    ensure_csv()
    datetime_string = datetime.now(timezone.utc).astimezone().isoformat()
    line = f"{datetime_string},{','.join(str(v[1]) for v in values)}\n"
    with open(csvfile, mode="a") as f:
        f.write(line)


def plot_file() -> None:
    df = pd.read_csv(csvfile, index_col="date", parse_dates=True)
    ax = df.plot()
    ax.ticklabel_format(style="plain", axis="y")  # no exponential notation on y-axis
    ax.set_ylabel("Estimated value ($)")
    ax.set_xlabel(f"Date (last updated {df.index[-1].date().isoformat()})")
    ax.grid()
    plt.rcParams["savefig.dpi"] = 144
    ax.get_figure().savefig(plotfile, bbox_inches="tight")


def main():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)-8s %(message)s"
    )
    values = []
    for site in sites:
        logging.info(f"Start  getting {site['name']}")
        try:
            url = site["url"]
        except KeyError:
            url = os.environ[site["name"].upper() + "_URL"]
        value = retry_get_value(url=url, xpath=site["xpath"])
        logging.info(f"Finish getting {site['name']}. {value=}")
        values.append((site["name"], value))
    append_csv(values)
    plot_file()


if __name__ == "__main__":
    main()
