import requests
from lxml import html
import re

import sys
sys.path.append("..")
from xmat import Xmat
import db

class Bazarmat(Xmat):
	def __init__(self,name):
		super().__init__(name)
		self.db = db.table(name)

		if 'ids' not in self.db:
			self.db["ids"] = []

		self.target_email = db.load_or_write("sensitive", "email")

	def update(self):
		for item in self.items_of_interest():
			self.send(*item)

		self.db.commit()

	def get_id(self, element):
		pass

	def items_of_interest(self):
		try:
			bazar = requests.get(self.bazar_url, timeout=10)
		except Exception as e:
			self.send_error(e, self.target_email)
			return
		
		tree = html.fromstring(bazar.content)

		for inzerat in tree.xpath(self.inzerat_xpath):
			iid = self.get_id(inzerat)

			if iid in self.db["ids"]:
				continue

			url  = inzerat.xpath(self.inzerat_url)[0].attrib['href']
			name = inzerat.xpath(self.inzerat_name)[0].text_content()
			text = inzerat.xpath(self.inzerat_popis)[0].text_content()
			cena = inzerat.xpath(self.inzerat_cena)[0].text_content()

			self.log("new item discovered: " + name[:25])

			self.db["ids"].append(iid)
			self.db.commit()

			if "x1 carbon" in name.lower():
				yield (self.target_email, "[{}]: lenovo found".format(self.name),
					   cena + "\n" + text + "\n" + url)