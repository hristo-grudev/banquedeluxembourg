import scrapy

from scrapy.loader import ItemLoader
from ..items import BanquedeluxembourgItem
from itemloaders.processors import TakeFirst


class BanquedeluxembourgSpider(scrapy.Spider):
	name = 'banquedeluxembourg'
	start_urls = ['https://www.banquedeluxembourg.com/en/bank/bl/all-news#page-02']

	def parse(self, response):
		post_links = response.xpath('//div[@class="topics-index-item"]')
		for post in post_links:
			date = post.xpath('./a/div[@class="topics-index-item-date"]/text()').get()
			print(post)
			url = post.xpath('./a/@href').get()
			title = post.xpath('./a/div[@class="topics-index-item-title"]/text()').get()
			yield response.follow(url, self.parse_post, cb_kwargs=dict(date=date, title=title))

		next_page = response.xpath('//ul[@class="lfr-pagination-buttons pager"]/li[2]/a/@href').getall()
		if next_page != 'javascript:;':
			yield from response.follow_all(next_page, self.parse)

	def parse_post(self, response, date, title):
		description = response.xpath('//div[@class="portlet-body"]/div[@class="article-wrapper"]//text()[normalize-space() and not(ancestor::div[contains(@class, "contact")])]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()

		item = ItemLoader(item=BanquedeluxembourgItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()