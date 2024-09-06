import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from datetime import datetime, timedelta
import urllib.parse

size_dict_women = {
    'XXXS': 1226, 'XXS': 102, 'XS': 2, 'S': 3, 'M': 4, 'L': 5, 'XL': 6, 'XXL': 7, 'XXXL': 310
}

size_dict_men = {
    'XS': 204, 'S': 205, 'M': 206, 'L': 207, 'XL': 208, 'XXL': 209, 'XXXL': 210
}

brand_dict = {
    'carhartt': 362, 'nike': 53, 'adidas': 14, 'zara': 12, 'h&m': 7
}

color_dict = {
    'noir': 1, 'blanc': 12, 'rouge': 7, 'bleu': 9, 'vert': 10, 'jaune': 8, 'rose': 7,
    'orange': 11, 'violet': 6, 'gris': 3, 'beige': 4, 'marron': 2, 'kaki': 16
}

def get_user_input():
    search_query = input("Entrez la recherche que vous souhaitez effectuer : ").strip()
    if not search_query:
        print("La recherche est obligatoire.")
        return get_user_input()

    gender = input("Entrez le genre (homme/femme) : ").strip().lower()
    if gender not in ['homme', 'femme']:
        print("Genre invalide, veuillez entrer 'homme' ou 'femme'.")
        return get_user_input()

    size_dict = size_dict_men if gender == 'homme' else size_dict_women

    size = input("Entrez la taille (optionnel, ex: M, L, XL) : ").strip().upper()
    brand = input("Entrez la marque (optionnel, ex: carhartt, nike) : ").strip().lower()
    color = input("Entrez la couleur (optionnel, ex: noir, blanc, rouge) : ").strip().lower()
    price_from = input("Entrez le prix minimum (optionnel) : ").strip()
    price_to = input("Entrez le prix maximum (optionnel) : ").strip()

    filters = {
        'size': size_dict.get(size),
        'brand': brand_dict.get(brand),
        'color': color_dict.get(color),
        'price_from': price_from if price_from else None,
        'price_to': price_to if price_to else None
    }

    return search_query, filters

def build_search_url(search_query, filters):
    base_url = 'https://www.vinted.fr/catalog'
    query_params = {'search_text': search_query}
    
    for key, value in filters.items():
        if value:
            query_params[f'{key}_ids[]' if key in ['size', 'brand', 'color'] else key] = value
    
    return f"{base_url}?{urllib.parse.urlencode(query_params, doseq=True)}"

def scrape_vinted_category(url, time_filter=False):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"
    service = Service(executable_path='Z:/WebDriver/bin/chromedriver.exe')

    sys.stderr = open(os.devnull, 'w')
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 10)
    items_data = []

    driver.get(url)

    try:
        while True:
            try:
                items = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.new-item-box__container')))
                for item in items:
                    try:
                        price = item.find_element(By.CSS_SELECTOR, 'p[data-testid*="price-text"]').text.strip()
                        size = item.find_element(By.CSS_SELECTOR, 'p[data-testid*="description-subtitle"]').text.strip()
                        brand = item.find_element(By.CSS_SELECTOR, 'p[data-testid*="description-title"]').text.strip()
                        article_url = item.find_element(By.CSS_SELECTOR, 'a[data-testid*="overlay-link"]').get_attribute('href')

                        if time_filter:
                            driver.execute_script("window.open('');")
                            driver.switch_to.window(driver.window_handles[1])
                            driver.get(article_url)
                            try:
                                time_posted_element = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, 'span[title]'))
                                )
                                time_posted = time_posted_element.get_attribute('title')
                                post_time = datetime.strptime(time_posted, "%d/%m/%Y %H:%M:%S")
                                if datetime.now() - post_time > timedelta(hours=24):
                                    driver.close()
                                    driver.switch_to.window(driver.window_handles[0])
                                    continue
                            except (NoSuchElementException, TimeoutException):
                                driver.close()
                                driver.switch_to.window(driver.window_handles[0])
                                continue
                            driver.close()
                            driver.switch_to.window(driver.window_handles[0])

                        items_data.append({'price': price, 'size': size, 'brand': brand, 'article_url': article_url})
                        print(f'Price: {price}, Size: {size}, Brand: {brand}, Article URL: {article_url}')
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
    while True:
        command = input("Entrez 'search' pour lancer une recherche, 'recent' pour les articles récents ou 'exit' pour quitter : ").strip().lower()
        if command == 'search':
            search_query, filters = get_user_input()
            search_url = build_search_url(search_query, filters)
            print(f"URL de recherche : {search_url}")
            scrape_vinted_category(search_url)
        elif command == 'recent':
            search_query, filters = get_user_input()
            search_url = build_search_url(search_query, filters)
            print(f"URL de recherche : {search_url}")
            scrape_vinted_category(search_url, time_filter=True)
        elif command == 'exit':
            print("Exiting the program.")
            break
        else:
            print("Commande non reconnue. Veuillez entrer 'search', 'recent' ou 'exit'.")

if __name__ == "__main__":
    main()