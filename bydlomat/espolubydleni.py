import requests
from lxml import html
from lxml import etree as xml

import sys
sys.path.append("..")
from xmat import Xmat
import db

address = db.load_or_write("sensitive", "email")
url = 'https://www.espolubydleni.cz/podnajem-spolubydlici/praha'
nabizim = b'Nab\xc3\xadz\xc3\xadm'.decode("utf-8")

class Espolubydlenimat(Xmat):
	def __init__(self):
		super().__init__('espolubydleni')
		self.db = db.table("espolubydleni")

	def update(self):
		for item in self.items_of_interest():
			self.send(*item)

	def items_of_interest(self):

		for i in range(1,4): # only first pages

			r = requests.post(url + "/" + str(i))

			try:
				html_etree = html.fromstring(r.content)
			except Error as e:
				self.send_error(e, address)

			bids = couples(html_etree.xpath('//div[@id="result1"]/table/tr')[1:])

			for head, tail in bids:
				head_td = head.xpath("./td")
				short = head_td[1].xpath("./a/h3")[0].text

				if short in self.db["sent"]:
					continue

				typ = head_td[3].xpath("./strong")[0].text

				if not nabizim in typ:
					continue


				try:
					price = head_td[3].xpath("./span/b[@style='color:#E72D2D;font-size:18px;']")[0].text
					price = to_price(price)
				except IndexError:
					self.log("no price")
					self.log("index", i)
					price = 0

				location = head_td[4].xpath("./a/b")[0].text
				
				if not location in self.db["locations"]:
					continue

				try:
					link = tail.xpath(".//a[@title='Send an e-mail']")[0].attrib["href"]
					link = "https://espolubydleni.cz" + link
				except IndexError:
					self.log("no link")
					self.log("index:", i)
					link = "no link"
				desc = tail.xpath("//div[@class='popis1']")[0].text

				"""
				self.log("short:", short)
				self.log("typ:", typ)
				self.log("price:", price)
				self.log("location:", location)
				self.log("link:", link)
				self.log("decs:", desc)
				"""
				subject = "[{}]:{},{},{}".format(self.name,location,price,short)
				text = "\n".join([location, str(price), typ, desc, link])

				self.db["sent"].append(short)
				self.db.commit()
				yield (address, subject, text)


def couples(l):
	return [(l[2*i],l[2*i+1]) for i in range(len(l)//2)]

def to_price(x):
	return int("".join(s for s in x if s.isdigit()))	

if __name__ == '__main__':
	Espolubydlenimat().loop()