import requests
from lxml import html
from xmat import Xmat

class Duskomat(Xmat):
	def __init__(self):
		super().__init__('duskomat', hello_email='tomas@krnak.cz')

	def items_of_interest(self):
		page = requests.get('http://www.lavka.cz/divadlo/program/')
		tree = html.fromstring(page.content)
		for anchor in tree.xpath("//ul[@id='lcp_instance_0']/li/a"):
			text = anchor.text_content()
			if (not text in self.database) and ('Jaroslav' in text):
				self.dump_db(text)
				yield text

	def update(self):
		for item in self.items_of_interest():
			#self.send('773281310@SMS.t-mobile.cz', '[duskomat]: Nové představení', item)
			self.send(  'jit.novakova@seznam.cz' , '[duskomat]: Nové představení', item)



if __name__ == '__main__':
	Duskomat().loop()

