import re
import webbrowser

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from tqdm import tqdm

URL = "https://www.rebohuurwoning.nl"
links = []
filtered_links = []

driver = webdriver.Chrome('./chromedriver')
page = requests.get(URL + "/nl/aanbod")
soup = BeautifulSoup(page.content, "html.parser")
aanbod_div = soup.find("div", class_="row js-object-items")

"""
Filtering appartments based on price, # bedrooms and area
"""
for property in aanbod_div.find_all("div", class_="property js-object-item"):
    price = int("".join(filter(str.isdigit, property.find(class_="price").text)))
    
    bedrooms_tag = property.find(class_="bedrooms") 
    bedrooms = int(bedrooms_tag.text) if bedrooms_tag is not None else None

    area_tag = property.find(class_="measurements")
    area =  int(re.split(' |,', area_tag.text)[0]) if area_tag is not None else None
    
    condition = (700 < price < 1500) and (bedrooms is None or bedrooms >=2) and (area is None or area >= 70)

    if condition: 
        links.append(property.find("a")['href'])

available_bar = tqdm(total=0, position=1, bar_format='{desc}')

"""
From the filtered appartments, checking which one is available.
"""
for link in tqdm(links, desc="Checking appartment availability", position=0):
    driver.get(URL + link)

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    status_label = soup.find("div", text="Status")
    status = status_label.find_next_sibling("div", class_="value").text
    if status == "Beschikbaar":
        filtered_links.append(URL + link)
    available_bar.set_description_str(f"Available appartments found: {len(filtered_links)}")

""""Automatically opening appartments"""
for x in filtered_links:
    webbrowser.open(x)

driver.close()


