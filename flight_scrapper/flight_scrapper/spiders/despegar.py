import scrapy
import json
import logging
import os
from flight_scrapper.items import FlightScrapperItem
from dotenv import load_dotenv

logger = logging.getLogger("DespegarLogger")

load_dotenv()

destination = os.getenv("DESTINATION")
if destination == "NY":
    from .urls_ny import DESPEGAR_URLS
elif destination == "BSAS":
    from .urls_bsas import DESPEGAR_URLS


class DespegarSpider(scrapy.Spider):
    name = "despegar"
    req_number = 0
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "es-419,es;q=0.9",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        # Requests sorts cookies= alphabetically
        # 'Cookie': 'trackerid=fe9df6e1-8879-4645-9df6-e188794645f6; xdesp-rand-usr=751; _gcl_au=1.1.635103425.1654611974; _gid=GA1.3.1866671445.1654611974; __sessionId_cookie=b2b751c0f3fee7987530e43bbab5bcc4; _fbp=fb.2.1654611976175.2044148697; __gads=ID=a9970591f81dc0ae-2261396a537c0001:T=1654611977:S=ALNI_MYULIYT73VieNIFAZlwN6o4XfVF3g; __gpi=UID=000006981fe4ca5b:T=1654611977:RT=1654611977:S=ALNI_MYPD9hINl7xpvadKR_1xwv9BwmMnw; x-locale=es-AR; _ga=GA1.3.1993442852.1654611974; _dc_gtm_UA-36944350-52=1; trackeame_cookie=%7B%22id%22%3A%22fe9df6e1-8879-4645-9df6-e188794645f6%22%2C%22upa_id%22%3A%22fe9df6e1-8879-4645-9df6-e188794645f6%22%2C%22creation_date%22%3A%222022-06-07T20%3A07%3A20Z%22%2C%22company_id%22%3A%221%22%2C%22version%22%3A%227.0%22%7D; _dc_gtm_UA-36944350-8=1; datadome=DctD8_d~z_qqYYyYKEjWh.o3zMHkLnXZgGKVKwI~aOciHlaxz6zQCrnsJAmJVHSbKcV9UfpGF.vc9XaSw0rH9SGoDzBFc5DmY~qgzBac~NKv5SyxE-OylAHVqfEswV0; resultsVisited=COR_BUE-2|COR_BUE_BUE_COR-2; _ga_DFR269QBZR=GS1.1.1654631520.2.1.1654632473.24',
        "Pragma": "no-cache",
        "Referer": "https://www.despegar.com.ar/shop/flights/results/oneway/COR/BUE/2022-10-25/1/0/0/NA/NA/NA/NA?from=SB&di=1-0&reSearch=true",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.61 Safari/537.36",
        "X-Gui-Version": "21.24.6",
        "X-REFERRER": "https://www.despegar.com.ar/shop/flights/results/roundtrip/COR/BUE/2022-10-25/2022-10-30/1/0/0/NA/NA/NA/NA/NA?from=SB&di=1-0",
        "X-RequestId": "8etOwmrNlK",
        "X-Requested-With": "XMLHttpRequest",
        "X-TrackingCode": "4152",
        "X-UOW": "results-05-1654632473485",
        "sec-ch-device-memory": "8",
        "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
        "sec-ch-ua-arch": '"x86"',
        "sec-ch-ua-full-version-list": '" Not A;Brand";v="99.0.0.0", "Chromium";v="102.0.5005.61", "Google Chrome";v="102.0.5005.61"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
    }

    def start_requests(self):
        token_despegar = os.getenv("DESPEGAR_TOKEN")
        for url in DESPEGAR_URLS:
            url += f"&h={token_despegar}"
            yield scrapy.Request(url, headers=self.headers, callback=self.parse)

    def parse(self, response, **kwargs):
        self.req_number += 1

        responses_path = os.getenv("RESPONSES_PATH")
        with open(f"{responses_path}/dsp_response_{self.req_number}.json", "w+") as f:
            f.write(response.text)

        response = json.loads(response.text)
        items = response.get("items")

        for item in items:
            if item.get("itemType") == "BIG_CLUSTER":
                item_data = item.get("item")
                total_fare = item_data.get("priceDetail").get("totalFare").get("amount")
                route_choices = item_data.get("routeChoices")
                for route_choice in route_choices:
                    for route_info in route_choice.get("routes"):
                        for segment in route_info.get("segments"):
                            route = f"{route_info.get('arrival').get('airportCode')}-{route_info.get('departure').get('airportCode')}"
                            yield FlightScrapperItem(
                                route=route,
                                day=segment.get("departure").get("date"),
                                is_best_offer="N/A",
                                total_duration=route_info.get("totalDuration"),
                                offer_id=segment.get("flightId"),
                                seats_available=route_info.get("seatsRemaining"),
                                total_fare=total_fare,
                            )
