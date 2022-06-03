import scrapy
import json
import logging
from scrapy.utils.project import get_project_settings
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import ElementNotSelectableException, ElementNotVisibleException
from flight_scrapper.items import FlightScrapperItem

logger = logging.getLogger('AerolineasLogger')

class AerolineasArgSpider(scrapy.Spider):
    name = 'aerolineas_arg'
    url = 'https://api.aerolineas.com.ar/v1/flights/offers?adt=1&inf=0&chd=0&flexDates=false&cabinClass=Economy&flightType=ROUND_TRIP&leg=COR-MIA-20220903&leg=MIA-COR-20220916'
    headers = {
                "Authorization": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik1EaEdRa0U0T0RNeE56WTRRemcxTVRjMVJERXhOekF5T0RCRU1EUTVSakl6TURjNU5qVTVNQSJ9.eyJpc3MiOiJodHRwczovL2Flcm9saW5lYXMtdGVzdC5hdXRoMC5jb20vIiwic3ViIjoib3k4MVpVbjZJWDFndjRlR2NlU0ZJeWFGZmhINmE2NkdAY2xpZW50cyIsImF1ZCI6ImFyLWF1dGgiLCJpYXQiOjE2NTQyOTE3NDIsImV4cCI6MTY1NDM3ODE0MiwiYXpwIjoib3k4MVpVbjZJWDFndjRlR2NlU0ZJeWFGZmhINmE2NkciLCJzY29wZSI6ImNhdGFsb2c6cmVhZCBydWxlczpwYXltZW50OnJlYWQgcnVsZXM6c2hvcHBpbmc6cmVhZCBydWxlczpjaGVja291dDpyZWFkIGxveWFsdHk6cmVhZCBsb3lhbHR5OmFkbWluIGNhdGFsb2c6cGF5bWVudDpyZWFkIiwiZ3R5IjoiY2xpZW50LWNyZWRlbnRpYWxzIiwicGVybWlzc2lvbnMiOlsiY2F0YWxvZzpyZWFkIiwicnVsZXM6cGF5bWVudDpyZWFkIiwicnVsZXM6c2hvcHBpbmc6cmVhZCIsInJ1bGVzOmNoZWNrb3V0OnJlYWQiLCJsb3lhbHR5OnJlYWQiLCJsb3lhbHR5OmFkbWluIiwiY2F0YWxvZzpwYXltZW50OnJlYWQiXX0.ViMoV5ced8pl6sDdl6XFGXX6qHxAtV9ed-tVpdMfhGtbdu1eEPbvcv4lf-LzyJ8lPTI2LYtvet7aoiFtej3ZWkjvj8wkR1GS98RYb-OIvvOqhQcI38Fd9-AthJhoVJv8J8vHpZluo7NMF_Gkjo1TBPopFuvsed0YnDVEfS0-mbgSY1acrDDtIhuWX5eClEXFgqwTNXiwyCC1D2Zam6olrhWxFgqJG4NUQQn1yfMQk8rXdQ6dh8lnxgr5SEEJCRwKDt8kJrRK6kkDKtjOks4e-GmOjhJSzV7RCqye2eiiQY2FEnsqMfRlqqFTqJNw6sbEcb5MK0L2ibqT4sZR23S-Ng",
                "accept": "application/json, text/plain, */*",
                "accept-encoding": "gzip, deflate, br",
                "accept-language": "es-AR",
                "origin": "https://www.aerolineas.com.ar",
                "referer": "https://www.aerolineas.com.ar/",
                "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "macOS",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-site",
                "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.61 Safari/537.36",
                "x-channel-id": "WEB_AR", 
                }

    def start_requests(self):
        return [scrapy.Request(self.url, headers=self.headers, callback=self.parse)]

    # def start_requests(self):
    #     options = webdriver.ChromeOptions()
    #     options.headless = True
    #     driver = webdriver.Chrome("/Users/atresca/flight-scrapper/chromedriver", options=options)
        
    #     wait = WebDriverWait(driver, timeout=60, poll_frequency=10, ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException])
    #     element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="label-fare"]')))

    #     driver.get(self.url)
        
    #     with open("pag_aa.html", "wb+") as f:
    #         f.write(driver.page_source.encode("utf-8"))

    #     price_elements = driver.find_elements_by_xpath('//*[@id="label-fare"]')
    #     logger.info("PRECIOSSS: %s", price_elements)

    #     requests = []
    #     for price in price_elements:
    #         logger.info("PRECIO: %s", price)
    #         requests.append(scrapy.Request(price.text, callback=self.parse))

    #     driver.quit()
    #     return requests

    def find_lower_price(self, offers):
        lowest_offer = None
        lowest_price = 999999999999999999999999
        for offer in offers:
            logger.info("OFFER: %s", offer)
            offer_price = offer.get("fare").get("total")
            if offer_price < lowest_price:
                lowest_offer = offer
                lowest_price = offer_price
        return lowest_offer

    def parse(self, response, **kwargs):
        logger.info("RESPONSE: %s", response.text)

        # with open("aa_response.json", "w+") as f:
        #     f.write(response.text)

        response = json.loads(response.text)

        alternate_offers = response.get("alternateOffers")
        branded_offers = response.get("brandedOffers")

        # logger.info("branded_offers: %s", branded_offers)
        items = []
        for index in branded_offers:
            branded_offer = branded_offers.get(index)
            for branded in branded_offer:
                if branded.get("bestOffer", False) is True:
                    total_duration = branded.get("legs")[0].get("totalDuration")
                    lowest_offer = self.find_lower_price(branded.get("offers"))

                    item = FlightScrapperItem(
                        total_duration=total_duration,
                        lowest_offer=lowest_offer
                    )
                    items.append(item)

        yield {"flights": items}