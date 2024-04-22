import random
from time import sleep
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

opts = Options()
opts.add_argument(
    "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
opts.add_argument("--headless")

driver = webdriver.Chrome(
    service = Service(ChromeDriverManager().install()), 
    options = opts
)
driver.get('https://www.homecenter.com.co/homecenter-co/'
           'search/?Ntt=cemento%2050kg')

def scroll_smooth(driver, i, scroll_multiplayer):
    """
    scrolling function to go down the page and load more games
    :param driver: selenium driver
    :param i: iteration number
    :param scroll_multiplayer: how many times pixels are going to be scrolled
    """
    scroll_to = 2000 * (i + 1)
    start = (i * 2000) 
    for number in range(start,  scroll_to, scroll_multiplayer):
        scrollingScript = f""" 
          window.scrollTo(0, {number})
        """
        driver.execute_script(scrollingScript)

# close a geolocation popup
try:
    dis = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, '//div[@id="geolocation-close-icon"]/*')
        )
    )
    dis.click()
    driver.refresh()
except Exception as e: 
    logging.info("No geolocation popup")

driver.refresh()
scroll_smooth(driver, 6, 600)

# to wait until next page button is available
try:
    navigation = WebDriverWait(driver, 2).until(
        EC.presence_of_element_located(
            (By.XPATH, "//button[@id='bottom-pagination-next-page']")
        )
    )
    pages = range(2)
except Exception as e:
    logging.info("No more pages available")
    pages = range(0)

output = {}
for i in pages:

    # to wait until page updates all the items
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "//div[@itemprop='offers']")
        )
    )

    products = driver.find_elements(
        By.XPATH, "//h2[(contains(text(), 'cemento')"
        " or contains(text(), 'Cemento')) and contains(text(), '50kg')]"
    )
    items = []
    for product in products:
        i = product.find_element(
            By.XPATH, "../../.." # go to parent
        )
        items.append(i)

    for item in items:
        price = item.find_element(
            By.XPATH, ".//div[contains(@class, 'desktop-price-cart')]"
            "//div[not(contains(@class, 'precios-pro'))]"
            "//span[contains(text(),'$')]"
        ).text
        name = item.find_element(
            By.XPATH, ".//h2"
        ).text
        logging.info(f"Nombre: {name}, Precio: {price}")
        output[name] = price
    
    try:
        navigation.click()
        sleep(random.uniform(10, 30))
    except:
        logging.info("No more pages available")
        break

# Write the output to a CSV file
with open('bases/output_sodimac.csv', 'w',
           newline='', encoding='utf-8') as csvfile:
    fieldnames = ['name', 'price']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    
    for name, price in output.items():
        writer.writerow(
            {'name': name, 'price': price}
       )
