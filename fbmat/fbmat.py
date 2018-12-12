from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, InvalidElementStateException
import time
import http

from xmat import Xmat

#xpath = "//div[@role='feed']/div[@role='article']"
xpath = "//div[@id='contentArea']//div[@data-fte='1']"

class FBmat(Xmat):
	def __init__(self):
		super().__init__('fbmat', hello_period=4*24*60*60,
			hello_email="tomas@krnak.cz")
		self.driver = webdriver.PhantomJS()

	def items_of_interest(self):
		for link_id, target_emails, link in self.settings['links']:
			#if link_id != 'mmit':
			#	continue
			self.log('check ' + link_id)
			self.driver.get(link)
			self.log("len " + str(len(self.driver.find_elements_by_xpath(xpath))))
			for article in self.driver.find_elements_by_xpath(xpath):
				iid = article.get_attribute('id')
				self.log('check iid' + str(iid))
				if iid in self.database:
					continue
				self.database.add(iid)
				try:
					article.find_element_by_xpath('//a[class="see_more_link"]').click()
					time.sleep(1)
					#new line
					self.log('klikám')
				except NoSuchElementException:
					#new line
					self.log('neklikám')
					pass
				author, stamp = article.text.split('\n')[:2]
				author = ' '.join(author.split(' ')[:2])
				lines = []
				for line in article.text.split('\n')[2:]:
					if line in ('To se mi líbí', 'Zobrazit překlad'):
						break
					lines.append(line)
				text = '\n'.join(lines)
				if not text or text == '\n':
					continue
				for target_email in target_emails:
					yield (target_email,
						   '[fb]: {} píše do {} id:{}'.format(
						   	author, link_id, iid[-8:-4]),
						   '\n'.join([author, stamp, text, link]))

	def login(self):
		self.log('logging in')
		self.driver = webdriver.PhantomJS()
		self.driver.get("https://www.facebook.com/")
		#driver.set_window_size(1024, 768)
		#driver.save_screenshot('now.png')
		self.driver.find_element_by_name('email').send_keys(self.settings['login'])
		self.driver.find_element_by_name('pass').send_keys(self.settings['pass'])
		self.driver.find_element_by_name('login').click()
		time.sleep(3)
		#self.iid = self.driver.execute_script('return dl_id')
		self.log('logged in')

	def update(self):
		if not self.logged_in():
			try:
				self.login()
			except (InvalidElementStateException, http.client.BadStatusLine):
				self.log('login failed')
				return
			except Exception as e:
				self.log('login failed\n\n' + str(e))
				return
		#self.show()
		"""while not self.logged_in():
			self.log('repeat')
			time.sleep(5)
			self.login()"""
		try:
			for article in self.items_of_interest():
				self.send(*article)
		except Exception as e:
			self.log('fail\n' + str(e))

		self.dump_db()

	def logged_in(self):
		'''A very very stupid test. Hmm. '''
		try:
			self.driver.get("https://www.facebook.com/")
			self.driver.find_element_by_name('pass')
			return False
		except NoSuchElementException:
			return True
		except Exception as e:
			self.log('login failed\n\n' + str(e))
			return False

	def outit(self):
		try:
			self.driver.close()
		except:
			self.log('closing driver was not successful')

	def show(self):
		self.driver.save_screenshot("now.png")



if __name__ == '__main__':
	FBmat().loop()
else:
	fb = FBmat()
	fb.load_db()
	fb.load_settings()