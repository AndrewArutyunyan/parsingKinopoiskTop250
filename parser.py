# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import time
import browser_cookie3
import os
from selenium import webdriver
from collections import Counter
import matplotlib.pyplot as plt


# Load website and write html-pages into file
# Faster way with no need in external webdrivers
def load_data(urls):
    ch_c = browser_cookie3.chrome(domain_name='.kinopoisk.ru', cookie_file=os.path.join(
        os.getenv('APPDATA', '')) + '\\..\\Local\\Google\\Chrome\\User Data\\Default\\Network\\Cookies')
    with requests.Session() as s:
        # ch_c = None
        s.headers.update({'User-Agent': 'Mozilla/5.0 (Linux; Android 8.0.0; Pixel 2 XL Build/OPD1.170816.004) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Mobile Safari/537.36'})
        idx = 1
        for url in urls:
            response = s.get(url, cookies=ch_c)
            time.sleep(3)
            with open(f'output_example{idx}.html', "w", encoding="utf-8") as file:
                file.write(response.content.decode('utf-8'))
            idx += 1


# Load website and write html-pages into file
# Using selenium solves the problem with AJAX but needs external webdrivers to run
def load_data2(urls):
    browser = webdriver.ChromiumEdge()
    idx = 1
    for url in urls:
        browser.implicitly_wait(5)
        page = browser.get(url, )
        browser.implicitly_wait(5)
        time.sleep(3)
        html = browser.page_source
        with open(f'output_page{idx}.html', "w", encoding="utf-8") as file:
            file.write(html)
        # time.sleep(5)
        idx += 1
    browser.close()


if __name__ == '__main__':
    # Get the html of 5 pages of top-250 and write to file
    # Use fake user-agent and cookies because Kinopoisk.ru uses captcha against parsers
    base_url = "https://www.kinopoisk.ru/lists/series-top250/"
    num_pages = 5
    page_urls = set()
    for i in range(num_pages):
        page_urls.add(base_url + '?page=' + str(i + 1) + '&tab=all')
    load_data2(page_urls)

    # Extract contents of each html file
    items = []
    for page_num in range(num_pages):
        with open(f'output_page{page_num + 1}.html', 'r', encoding="utf-8") as file:
            text = file.read()
            soup = BeautifulSoup(text, 'html.parser')
            # Collect genres of top-250 from *_meta-additional-item class
            additional_items = soup.find_all('span', class_="selection-film-item-meta__meta-additional-item")
            idx = 0
            for i, item in enumerate(additional_items):
                if not i % 2:
                    continue
                idx += 1
                span_item = item.text.split(', ')
                items.extend(span_item)
    print(items)

    # Plot bar chart of genres popularity
    fig, ax = plt.subplots(figsize=(12, 10))
    bars = ax.bar(Counter(items).keys(), Counter(items).values())
    ax.set_title('Статистика жанров')
    ax.set_ylabel('Число упоминаний в Топ-250 Кинопоиска')
    plt.xticks(rotation=60)
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom')
    plt.show()