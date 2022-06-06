from array import array
import scrapy
import json
import logging
from urllib.parse import parse_qs
import os
from flight_scrapper.items import FlightScrapperItem
from dotenv import load_dotenv

load_dotenv()

destination = os.getenv("DESTINATION")
if destination == "NY":
   from .urls_ny import AA_URLS
elif destination == "BSAS":
    from.urls_bsas import AA_URLS

logger = logging.getLogger("AerolineasLogger")


class AerolineasArgSpider(scrapy.Spider):
    name = "aerolineas_arg"
    req_number = 0
    headers = {
        "Authorization": os.getenv("AEROLINEAS_TOKEN"),
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
        urls = AA_URLS
        for url in urls:
            yield scrapy.Request(url, headers=self.headers, callback=self.parse)

    def get_lowest_offer(self, offers: array) -> dict:
        lowest_offer = None
        lowest_price = 999999999999999999999999
        for offer in offers:
            offer_price = offer.get("fare").get("total")
            if offer_price < lowest_price:
                lowest_offer = offer
                lowest_price = offer_price
        return lowest_offer

    def get_requested_dates(self, request_url: str) -> array:
        req_query_params = parse_qs(request_url)

        # Raw param with the rout in it
        departure_date = req_query_params["leg"][0]
        return_date = req_query_params["leg"][1]

        # Removes the route from the param
        departure_date = departure_date.split("-")[2]
        return_date = return_date.split("-")[2]

        # Get only the day from the date
        departure_date = departure_date[-2:]
        return_date = return_date[-2:]

        return [departure_date, return_date]

    def create_item(
        self,
        route: str,
        departure_date: str,
        return_date: str,
        is_best_offer: bool,
        total_duration: str,
        offer_id: str,
        seats_available: int,
        total_fare: int,
    ) -> FlightScrapperItem:
        return FlightScrapperItem(
            route=route,
            departure_date=departure_date,
            is_best_offer=is_best_offer,
            return_date=return_date,
            total_duration=total_duration,
            offer_id=offer_id,
            seats_available=seats_available,
            total_fare=total_fare,
        )

    def parse(self, response, **kwargs):
        self.req_number += 1

        # responses_path = os.getenv("RESPONSES_PATH")
        # with open(f"{responses_path}/aa_response_{self.req_number}.json", "w+") as f:
        #     f.write(response.text)

        departure_date, return_date = self.get_requested_dates(response.request.url)

        response = json.loads(response.text)

        branded_offers = response.get("brandedOffers")
        routes = response.get("searchMetadata").get("routes")

        if not branded_offers:
            return

        departure_offers = branded_offers.get("0")
        return_offers = branded_offers.get("1")

        if departure_offers is None or return_offers is None:
            logger.error(
                "ERROR in response Nº %s: \n departure_offers = %s \n return_offers = %s", self.req_number, departure_offers, return_offers
            )
            departure_offers, return_offers = [], []

        for offer in departure_offers:
            total_duration = offer.get("legs")[0].get("totalDuration")
            lowest_offer = self.get_lowest_offer(offer.get("offers"))

            yield FlightScrapperItem(
                route=routes[0],
                day=departure_date,
                is_best_offer=offer.get("bestOffer", False),
                total_duration=total_duration,
                offer_id=lowest_offer.get("offerId"),
                seats_available=lowest_offer.get("seatAvailability").get("seats"),
                total_fare=lowest_offer.get("fare").get("total"),
            )

        for offer in return_offers:
            total_duration = offer.get("legs")[0].get("totalDuration")
            lowest_offer = self.get_lowest_offer(offer.get("offers"))

            yield FlightScrapperItem(
                route=routes[1],
                day=return_date,
                is_best_offer=offer.get("bestOffer", False),
                total_duration=total_duration,
                offer_id=lowest_offer.get("offerId"),
                seats_available=lowest_offer.get("seatAvailability").get("seats"),
                total_fare=lowest_offer.get("fare").get("total"),
            )
