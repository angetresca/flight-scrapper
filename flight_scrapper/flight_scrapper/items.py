# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FlightScrapperItem(scrapy.Item):
    # define the fields for your item here like:
    total_duration = scrapy.Field()
    lowest_offer = scrapy.Field()
