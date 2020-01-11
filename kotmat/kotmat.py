import requests
from lxml import html
from lxml import etree as xml

import sys
sys.path.append("..")
from xmat import Xmat
import db

address = db.load_or_write("sensitive", "sms_email")
url = 'https://icts.kuleuven.be/apps/kotwijs/search/index.php'
headers = {'Content-Type': 'application/x-www-form-urlencoded'}
with open("raw_data.txt") as file:
	raw_data = file.read()

class Kotmat(Xmat):
	def __init__(self):
		super().__init__('kotmat')
		self.db = db.table("kotmat")

	def update(self):
		for item in self.items_of_interest():
			self.send(*item)


	def items_of_interest(self):
		for i in "12":

			r = requests.post(
				url,
				data=raw_data.format(i),
				headers=headers
			)
			xml_tree = xml.fromstring(r.content)
			html_etree = html.fromstring(xml_tree.getchildren()[0].getchildren()[-4].text)
			for kot in html_etree.xpath('//div[@class="dtr_kamer kamer result"]'):
				price = kot.xpath('.//div[@class="prijs result__price"]')[0].text_content()
				iid   = kot.xpath('./a')[0].attrib["onclick"]
				if not iid in self.db["ids"]:
					self.db["ids"].append(iid)
					self.db.commit()
					yield (address, "[kotmat]: new kot", "price: " + price + "\n" + url)

if __name__ == '__main__':
	Kotmat().loop()