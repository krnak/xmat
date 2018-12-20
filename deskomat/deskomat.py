import requests
from lxml import html
import re
import paho.mqtt.client as mqtt

from xmat import Xmat

source_xpath = "//table[@class='content edeska-vypis-vyveseni']/tbody/tr/td[@class='content edeska-sloupec-nazev']/a"
url = 'http://cztedeskaext.praha4.cz/eDeska/eDeskaAktualni.jsp'
class Deskomat(Xmat):
	def __init__(self):
		super().__init__('deskomat')
		self.mqtt_client = mqtt.Client()

	def update(self):
		self.mqtt_client.publish("michle/deskomat/running", qos=0, retain=False)
		for item in self.items_of_interest():
			self.send(*item)
		self.dump_db()

	def init(self):
		self.mqtt_client.connect("mqtt.KRNAK", 1883, 1000)
		self.mqtt_client.loop_start()

		self.target_email = self.setting["email"]
		if not self.target_email:
			self.target_email = input('Zadej cílovou emailovou adresu: ')

	def items_of_interest(self):
		try:
			deska = requests.get(url, timeout=10)
		except Exception as e:
			self.send("tomas@krnak.cz")
			return 
			
		tree = html.fromstring(deska.content)
		for anchor in tree.xpath(source_xpath):
			text = anchor.text_content().strip()
			link = anchor.attrib['href']
			iid = int(re.findall(r'\d+', link)[0])
			link = 'http://cztedeskaext.praha4.cz/eDeska/' + link

			if iid in self.database:
				continue
			self.database.add(iid)

			for word in self.settings['keywords']:
				if word in text.lower():
					subject = '[deskomat]: {} nalezeno'.format(word)
					text += '\n' + link
					yield (self.target_email, subject, text)

if __name__ == '__main__':
	Deskomat().loop()

