import requests
from lxml import html
import re
import paho.mqtt.client as mqtt

from xmat import Xmat

source_xpath = "//table[@class='content edeska-vypis-vyveseni']/tbody/tr/td[@class='content edeska-sloupec-nazev']/a"
url = 'http://cztedeskaext.praha4.cz/eDeska/eDeskaAktualni.jsp'

bazos_url="https://sport.bazos.cz/?hledat=kolo&rubriky=sport&hlokalita=&humkreis=25&cenaod=&cenado=5000&Submit=Hledat&kitx=ano"
inzerat_xpath="//span[@class=vypis]"
inzerat_url="//a[@href]"
inzerat_img="//img[@class=obrazek]"
pocet_xpath="//table[@class=listainzerat]/tbody/tr/td"



class Bazosmat(Xmat):
	def __init__(self):
		super().__init__('bazosmat')
	def update(self):
		for item in self.items_of_interest():
			self.send(*item)
		self.dump_db()

	def init(self):
		self.target_email = self.setting["email"]
		if not self.target_email:
			self.target_email = input('Zadej cílovou emailovou adresu: ')

	def items_of_interest(self):
		bazos_pageing = bazos_url
		
		try:
			bazos = requests.get(bazos_pageing, timeout=10)
		except Exception as e:
			self.send_error(e, self.target_email)
			return
		
		tree = html.fromstring(bazos.content)
		pocet = int(tree.xpath[pocet_xpath][0].text_content().split()[-1])
		while True:
			tree = html.fromstring(bazos.content)
			for inzerat in tree.xpath(inzerat_xpath):
				text = anchor.text_content().strip()
				anchor = inzerat.xpath(inzerat_url)[0].attrib['href']
				iid = anchor.split('/')[1]
				anchor = 'bazos.cz' + anchor

				if iid in self.database:
					continue
				self.database.add(iid)

				# search mechanism here

			# paging mechanism


if __name__ == '__main__':
	Bazosmat().loop()

