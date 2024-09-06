import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import urllib.parse

def get_user_input():
    search_query = input("Entrez la recherche que vous souhaitez effectuer : ").strip()
    if not search_query:
        print("La recherche est obligatoire.")
        return get_user_input()

    return search_query

def build_search_url(search_query):
    base_url = 'https://www.vinted.fr/catalog'
    query_params = {'search_text': search_query}
    return f"{base_url}?{urllib.parse.urlencode(query_params, doseq=True)}"

def scrape_vinted_category(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.binary_location = "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"
    service = Service(executable_path='Z:/WebDriver/bin/chromedriver.exe')

    sys.stderr = open(os.devnull, 'w')
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 10)

    driver.get(url)

    try:
        while True:
            try:
                items = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.new-item-box__container')))
                for item in items:
                    try:
                        price = item.find_element(By.CSS_SELECTOR, 'p[data-testid*="price-text"]').text.strip()
                        print(f'Price: {price}')
                    except NoSuchElementException:
                        continue
            except TimeoutException:
                break

            try:
                next_button = driver.find_element(By.CSS_SELECTOR, 'a[rel="next"]')
                next_button.click()
                wait.until(EC.staleness_of(items[0]))
            except NoSuchElementException:
                break

    except Exception as e:
        print(f'Error: {e}')

    driver.quit()
    sys.stderr = sys.__stderr__

def main():
    search_query = get_user_input()
    search_url = build_search_url(search_query)
    print(f"URL de recherche : {search_url}")
    scrape_vinted_category(search_url)

if __name__ == "__main__":
    main()