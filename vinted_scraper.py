import os
import sys
import threading
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import urllib.parse
import time

# Dictionnaires de correspondance pour les tailles, marques et couleurs
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

stop_event = threading.Event()

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

def build_search_url(search_query, filters, sort_by_recent=False):
    base_url = 'https://www.vinted.fr/catalog'
    query_params = {'search_text': search_query}

    if sort_by_recent:
        query_params['order'] = 'newest_first'

    for key, value in filters.items():
        if value:
            query_params[f'{key}_ids[]' if key in ['size', 'brand', 'color'] else key] = value
    
    return f"{base_url}?{urllib.parse.urlencode(query_params, doseq=True)}"

def scrape_recent_item(url):
    global stop_event
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"
    service = Service(executable_path='Z:/Données/Bureau/botvinted/WebDriver/bin/chromedriver.exe')

    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 10)

    last_seen_url = None 

    while not stop_event.is_set():
        driver.get(url)
        try:
            item = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.new-item-box__container')))
            try:
                price = item.find_element(By.CSS_SELECTOR, 'p[data-testid*="price-text"]').text.strip()
                size = item.find_element(By.CSS_SELECTOR, 'p[data-testid*="description-subtitle"]').text.strip()
                brand = item.find_element(By.CSS_SELECTOR, 'p[data-testid*="description-title"]').text.strip()
                article_url = item.find_element(By.CSS_SELECTOR, 'a[data-testid*="overlay-link"]').get_attribute('href')

                if article_url != last_seen_url:
                    last_seen_url = article_url
                    print(f"Price: {price}, Size: {size}, Brand: {brand}, Article URL: {article_url}")

            except NoSuchElementException:
                print("Error retrieving item details.")
        
        except TimeoutException:
            print("No items found on the page.")

        for _ in range(10):
            if stop_event.is_set():
                break
            time.sleep(1)

    driver.quit()

def stop_searching():
    global stop_event
    input("Appuyez sur Entrée pour arrêter la recherche en temps réel...")
    stop_event.set()

def main():
    while True:
        command = input("Entrez 'search' pour lancer une recherche, 'recent' pour les articles récents ou 'exit' pour quitter : ").strip().lower()
        if command == 'search':
            search_query, filters = get_user_input()
            search_url = build_search_url(search_query, filters)
            print(f"URL de recherche : {search_url}")
            scrape_recent_item(search_url)
        elif command == 'recent':
            stop_event.clear()
            search_query, filters = get_user_input()
            search_url = build_search_url(search_query, filters, sort_by_recent=True)
            print(f"URL de recherche : {search_url}")
            
            search_thread = threading.Thread(target=scrape_recent_item, args=(search_url,))
            search_thread.start()

            stop_searching()

            search_thread.join()
        elif command == 'exit':
            print("Exiting the program.")
            break
        else:
            print("Commande non reconnue. Veuillez entrer 'search', 'recent' ou 'exit'.")

if __name__ == "__main__":
    main()
