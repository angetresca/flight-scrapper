# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FlightScrapperItem(scrapy.Item):
    # define the fields for your item here like:
    route = scrapy.Field()
    day = scrapy.Field()
    is_best_offer = scrapy.Field()
    total_duration = scrapy.Field()
    offer_id = scrapy.Field()
    seats_available = scrapy.Field()
    total_fare = scrapy.Field()
