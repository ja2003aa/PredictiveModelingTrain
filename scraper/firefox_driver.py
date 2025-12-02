from selenium import webdriver
from selenium.webdriver.firefox.service import Service


def initialize_browser() -> webdriver:
    service = Service()
    options: webdriver.FirefoxOptions = webdriver.FirefoxOptions()
    options.add_argument("--no-sandbox")
    options.set_preference(
        "general.useragent.override",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    )

    # adding argument to disable the AutomationControlled flag
    options.add_argument("--disable-blink-features=AutomationControlled")

    # change user agent
    driver = webdriver.Firefox()

    # changing property of the navigator value for webdriver to undefined
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )

    return driver
