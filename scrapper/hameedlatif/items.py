# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class HameedlatifItem(scrapy.Item):
    # Basic page information
    url = scrapy.Field()
    title = scrapy.Field()
    page_type = scrapy.Field()
    main_content = scrapy.Field()
    scraped_at = scrapy.Field()
    word_count = scrapy.Field()
    
    # STRUCTURED DATA FIELDS
    departments = scrapy.Field()
    doctors = scrapy.Field()
    doctor_qualifications = scrapy.Field()
    phone_numbers = scrapy.Field()
    email_addresses = scrapy.Field()
    addresses = scrapy.Field()
    services = scrapy.Field()
    procedures = scrapy.Field()
    faqs = scrapy.Field()
    visitor_info = scrapy.Field()
    news_events = scrapy.Field()
    appointment_info = scrapy.Field()
    
    # DETAILED STRUCTURED INFORMATION
    doctor_profile = scrapy.Field()  # Complete doctor information
    department_info = scrapy.Field()  # Complete department information
    
    # ADDITIONAL COMPREHENSIVE FIELDS
    specialties = scrapy.Field()  # Medical specialties
    facilities = scrapy.Field()  # Hospital facilities
    descriptions = scrapy.Field()  # Detailed descriptions
