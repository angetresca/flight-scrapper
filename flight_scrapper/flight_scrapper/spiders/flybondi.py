import scrapy
import json
import logging
import os
from flight_scrapper.items import FlightScrapperItem
from dotenv import load_dotenv

logger = logging.getLogger("FlybondiLogger")

load_dotenv()

destination = os.getenv("DESTINATION")
if destination == "NY":
    logger.error("FLYBONDI DOESN'T GO TO NY")
    raise Exception("FLYBONDI DOESN'T GO TO NY")
elif destination == "BSAS":
    from .urls_bsas import FLYBONDI_BODY


class FlybondiSpider(scrapy.Spider):
    name = "flybondi"
    req_number = 0
    url = "https://flybondi.com/graphql"

    headers = {
        "authority": "flybondi.com",
        "accept": "application/json",
        "accept-language": "es-ES,es;q=0.9",
        "authorization": "Key b64ead64fb26d64668838ac2ef8c0c3222c3d285cf5a2fd1ce49281c140bcdaa",
        "content-type": "application/json",
        "cookie": "FBSessionX-ar-ibe=SFO-f708999d-fd95-474a-b2ee-9c619cdd2e80; _gcl_au=1.1.62148998.1654552996; _gid=GA1.2.2067561013.1654552996; _gat_UA-84809339-8=1; _fbp=fb.1.1654552996539.2098865957; _hjFirstSeen=1; _hjIncludedInSessionSample=0; _hjSession_1316071=eyJpZCI6IjY5ODg0YzQwLWUxZjQtNDUwMy1hNjFhLWJjNzRhZmY5NjVjYSIsImNyZWF0ZWQiOjE2NTQ1NTI5OTY4MjYsImluU2FtcGxlIjpmYWxzZX0=; _hjAbsoluteSessionInProgress=1; _hjSessionUser_1316071=eyJpZCI6ImYwZTBkNjZjLTRhMWQtNWVmZi05ZmRhLTI0OTJkNjcxZjY4YSIsImNyZWF0ZWQiOjE2NTQ1NTI5OTY3ODgsImV4aXN0aW5nIjp0cnVlfQ==; _ga=GA1.1.792410976.1654552996; _ga_1HGSJR4WPQ=GS1.1.1654552997.1.1.1654553045.12",
        "origin": "https://flybondi.com",
        "referer": "https://flybondi.com/ar/search/results?adults=1&children=0&currency=ARS&departureDate=2022-10-25&fromCityCode=COR&infants=0&returnDate=2022-10-28&toCityCode=BUE",
        "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.61 Safari/537.36",
        "x-fo-flow": "ibe",
        "x-fo-market-origin": "ar",
        "x-fo-ui-version": "2.55.1",
        "x-market-origin": "ar",
    }

    def start_requests(self):
        body = json.dumps(FLYBONDI_BODY)
        yield scrapy.Request(self.url, body=body, headers=self.headers, callback=self.parse, method="POST")

    def parse(self, response, **kwargs):
        self.req_number += 1

        responses_path = os.getenv("RESPONSES_PATH")
        with open(f"{responses_path}/fb_response_{self.req_number}.json", "w+") as f:
            f.write(response.text)

        response = json.loads(response.text)
        response = response.get("data")

        departures = response.get("departures")
        arrivals = response.get("arrivals")

        for offer in departures:
            route = offer.get("id")[:7]

            yield FlightScrapperItem(
                route=route,
                day=offer.get("departure")[:10],
                is_best_offer="N/A",
                total_duration="N/A",
                offer_id=offer.get("id"),
                seats_available="N/A",
                total_fare=offer.get("lowestPrice"),
            )

        for offer in arrivals:
            route = offer.get("id")[:7]

            yield FlightScrapperItem(
                route=route,
                day=offer.get("departure")[:10],
                is_best_offer="N/A",
                total_duration="N/A",
                offer_id=offer.get("id"),
                seats_available="N/A",
                total_fare=offer.get("lowestPrice"),
            )
