import re
import webbrowser

import requests
import tomllib

from bs4 import BeautifulSoup
from selenium import webdriver
from tqdm import tqdm

from util import mail, log


BASE_PATH = "C:/Users/Dominique/Documents/GitHub/huurwoning-scraper/"


def get_available_homes(config: dict, region: str) -> list[str]:
    """
    Retrieve all available homes given the config in city 'city'.
    """

    links = []
    filtered_links = []
    driver = webdriver.Chrome(f"{BASE_PATH}/chromedriver")
    page = requests.get(config["url"] + f"/nl/direct-te-huur/regio-{region}/")
    soup = BeautifulSoup(page.content, "html.parser")
    aanbod_div = soup.find("div", class_="row js-object-items")

    """
    Filtering appartments based on price, # bedrooms and area
    """
    for property in aanbod_div.find_all("div", class_="property js-object-item"):

        price_tag = property.find(class_="price")
        price = int("".join(filter(str.isdigit, property.find(class_="price").text))) if price_tag else None

        bedrooms_tag = property.find(class_="bedrooms")
        bedrooms = int(bedrooms_tag.text) if bedrooms_tag else None

        area_tag = property.find(class_="measurements")
        area = int(re.split(' |,', area_tag.text)[0]) if area_tag else None

        location = property.find('h4').text.lower()
        if config["strict_location"] and location != region:
            continue

        condition = (
            not price or (config["min_price"] < price < config["max_price"])) \
            and (not bedrooms or bedrooms >= config["min_bedrooms"]) \
            and (not area or area >= config["min_area"])

        if condition:
            links.append(property.find("a")['href'])

    available_bar = tqdm(total=0, position=1, bar_format='{desc}')

    """
    From the filtered appartments, checking which one is available.
    """
    for link in tqdm(links, desc="Checking apartment availability", position=0):
        driver.get(config["url"] + link)

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        status_label = soup.find("div", text="Status")
        status = status_label.find_next_sibling("div", class_="value").text

        if status == "Beschikbaar":
            filtered_links.append(config["url"] + link)

        available_bar.set_description_str(f"Available appartments found: {len(filtered_links)}")

    # """"
    # Automatically opening apartments
    # """
    # for x in filtered_links:
    #     webbrowser.open(x)

    driver.close()
    return filtered_links


if __name__ == '__main__':
    with open(f"{BASE_PATH}/config.toml", "rb") as f:
        conf = tomllib.load(f)

    rebo_conf = conf["rebo"]
    loc_conf = conf["location"]

    urls = []
    for region in loc_conf["regions"]:
        links = get_available_homes(config=rebo_conf, region=region)
        new_homes = log.log_homes(links)
        urls.extend(new_homes)

    if urls:
        mail.send_email(conf, urls)
