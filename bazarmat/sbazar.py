from bazarmat import Bazarmat


class Sbazarmat(Bazarmat):
	def __init__(self):
		super().__init__('sbazar')
		self.bazar_url="https://www.sbazar.cz/hledej/lenovo%20x1%20carbon"
		self.inzerat_xpath=".//li[@data-e2e=\"item\"]"
		self.inzerat_url=".//a[@class=\"c-item__link\"]"
		self.inzerat_img=".//img[@class=\"c-item__image\"]/img"
		self.inzerat_popis=".//span[@class=\"c-item__name-text\"]"
		self.inzerat_cena=".//span[@class=\"c-item__price\"]"
		self.inzerat_name=".//span[@class=\"c-item__name-text\"]"

	def get_id(self, element):
		return element.get("id")


if __name__ == '__main__':
	Sbazarmat().loop()
