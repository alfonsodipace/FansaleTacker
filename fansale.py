import os
import requests
from dotenv import load_dotenv
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent

load_dotenv()


def send_discord_message(webhook_url, message):
    data = {"content": message}
    response = requests.post(webhook_url, json=data)
    if response.status_code != 204:
        raise ValueError(
            f"Request to Discord returned an error: {response.status_code}, {response.text}"
        )


url = os.getenv("FANSALE_URL")
discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
discord_user_id = os.getenv("DISCORD_USER_ID")
ua = UserAgent()
options = webdriver.ChromeOptions()
# options.add_argument("--headless=new")
# options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
options.add_argument(ua.random)
profile = webdriver.ChromeProfile('/usr/bin/chromedriver')
driver = webdriver.Chrome(profile)
driver.options = options
# driver = webdriver.Chrome(options=options)

ua = UserAgent()
# Fetch the webpage
try:
    driver.get("https://www.fansale.it")
    driver.get("https://www.fansale.it/fansale/tickets/pop-amp-rock/marracash/464447/")
    driver.get("https://www.fansale.it/fansale/tickets/pop-amp-rock/marracash/464447/16316142")
except Exception as e:
    print(e)
    driver.quit()
    exit(1)


# Check if the specified xpath exists with the given value
try:
    element = WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element(
            (
                By.XPATH,
                # '//*[@id="pageContent"]/main/section[5]/div/div/div/div[2]/div[3]/div[3]'
                '//*[@id="pageContent"]/main/section[6]/div/div/div/div[2]/div[3]/div[@class="js-AvailabilityInfo-TextOfferList AvailabilityInfo-Text AvailabilityInfo-TextOfferList AvailabilityInfo-TextOfferList-isVisible"]',
            ),
            "Valitettavasti sopivia tarjouksia ei löytynyt.",
        )
    )
    print("No tickets")
except:
    print("Found tickets")
    # If the xpath does not exist or the value is different, process the required elements
    divTable = driver.find_element(
        By.XPATH,
        '//*[@id="pageContent"]/main/section[5]/div/div/div/div[2]/div[3]/div[3]'
    )
    elements = divTable.find_elements(
        By.CLASS_NAME,
        'EventEntry-isClickable'
    )
    for element in elements:
        quantities = element.get_attribute('data-splitting-possibilities')
        if "," in quantities:
            quantities = quantities.split(",")
            quantity = int(quantities[0])
        else:
            quantity = int(quantities)

        prices = element.get_attribute('data-splitting-possibility-prices')
        if "," in prices:
            prices = prices.split(",")
            if quantity == 1 and float(prices[0]) > 52.29:
                print(prices[0])
                # Send a Discord message with the new data
                message = f"Ticket price {prices[0]}\nurl: {url}"
                send_discord_message(discord_webhook_url, message)
        else:
            if quantity == 1 and float(prices) > 52.29:
                print(prices)
                # Send a Discord message with the new data
                message = f"Ticket price {prices[0]}\nurl: {url}"
                send_discord_message(discord_webhook_url, message)

# Close the WebDriver
driver.quit()
