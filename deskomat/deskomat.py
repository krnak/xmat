import requests
from lxml import html
import re
#import paho.mqtt.client as mqtt

import sys
sys.path.append("..")
from xmat import Xmat
import db

target_email = db.load_or_write("sensitive", "email")
source_xpath = "//table[@class='content edeska-vypis-vyveseni']/tbody/tr/td[@class='content edeska-sloupec-nazev']/a"
rows_xpath = "//table[@class='content edeska-vypis-vyveseni']/tbody/tr"

url = 'http://cztedeskaext.praha4.cz/eDeska/eDeskaAktualni.jsp'

class Deskomat(Xmat):
	def __init__(self):
		super().__init__('deskomat')
		self.db = db.table("deskomat")
		if not "ids" in self.db:
			self.db["ids"] = []
		if not "keywords" in self.db:
			self.db["keywords"] = []
		#self.mqtt_client = mqtt.Client()

	def update(self):
		#self.mqtt_client.publish("michle/deskomat/running", qos=0, retain=False)
		for item in self.items_of_interest():
			self.send(*item)

	#def init(self):
	#	self.mqtt_client.connect("mqtt.KRNAK", 1883, 1000)
	#	self.mqtt_client.loop_start()

	def items_of_interest(self):
		try:
			deska = requests.get(url, timeout=10)
		#except requests.exceptions.Timeout:
		except Exception as e:
			self.send_error(e, db.table("sensitive")["email"])
			return
			
		tree = html.fromstring(deska.content)
		for row in tree.xpath(rows_xpath):
			anchor = row.xpath("./td[@class='content edeska-sloupec-nazev']/a")[0]
			znacka = row.xpath("./td[@class='content edeska-sloupec-znacka']")[0].text_content().strip()
			print(znacka)
			text = anchor.text_content().strip()
			link = anchor.attrib['href']
			iid = int(re.findall(r'\d+', link)[0])
			link = 'http://cztedeskaext.praha4.cz/eDeska/' + link

			if iid in self.db["ids"]:
				continue
			self.db["ids"].append(iid)
			self.db.commit()

			word = ""
			for w in self.db['keywords']:
				if w in text.lower():
					word = w

			if "/OST/" in znacka:
				word = "/OST/"

			if word:
				subject = '[deskomat]: {} nalezeno'.format(word)
				text += '\n' + link
				yield (target_email, subject, text)

if __name__ == '__main__':
	Deskomat().loop()