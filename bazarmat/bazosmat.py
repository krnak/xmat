from bazarmat import Bazarmat


class Bazosmat(Bazarmat):
	def __init__(self):
		super().__init__('bazos')
		self.bazar_url     = "https://www.bazos.cz/search.php?hledat=lenovo+x1+carbon&rubriky=www&hlokalita=&humkreis=25&cenaod=&cenado=&Submit=Hledat&kitx=ano"
		self.inzerat_xpath = ".//span[@class=\"vypis\"]"
		self.inzerat_url   = ".//a[@href]"
		self.inzerat_img   = ".//img[@class=\"obrazek\"]"
		self.inzerat_popis = ".//div[@class=\"popis\"]"
		self.inzerat_cena  = ".//span[@class=\"cena\"]/b"
		self.inzerat_name  = self.inzerat_url

	def get_id(self, element):
		return element.xpath(self.inzerat_url)[0].get("href").split("/")[4]


if __name__ == '__main__':
	Bazosmat().loop()

