import selenium
import selenium.webdriver #some __init__.py fail in selenium
from selenium.common.exceptions import NoSuchElementException, InvalidElementStateException
import time
import http
import json
import urllib
import sys

sys.path.append("..")
from xmat import Xmat
import db
#xpath = "//div[@role='feed']/div[@role='article']"
article_xpath = "//div[@id='m_group_stories_container']//div[@role='article']"
article_xpath2 = "//div[@id='m_story_permalink_view']//div[@data-ft]/div[@class]"
drdo_url = "https://m.facebook.com/groups/1654596291463830/"
fb_login = db.load_or_write("sensitive","fb_login")
fb_pasw = db.load_or_write("sensitive", "fb_pasw")
article_url = "https://m.facebook.com/groups/1654596291463830?view=permalink&id="


class FBmat(Xmat):
	def __init__(self):
		super().__init__('fbmat', hello_period=4*24*60*60)
		options = selenium.webdriver.firefox.options.Options()
		options.headless = True
		self.driver = selenium.webdriver.Firefox(options=options)
		self.db = db.table("fbmat")

	def items_of_interest(self):
		for group, link in self.db["links"].items():
			#if group != "bcan":
				#continue
			self.log("checking " + group)

			subscribers = link["subscribers"][:]
			self.driver.get(link["url"])

			articles = self.driver.find_elements_by_xpath(article_xpath)
			self.log(str(len(articles)) + " articles found")
			iids = []
			for article in articles:
				if "Navrhované skupiny" in article.text:
					continue
				iid = str(json.loads(article.get_attribute('data-ft'))["mf_story_key"])
				iids.append(iid)

				#self.log('check iid ' + str(iid))
			for iid in iids:
				for email in subscribers[:]:
					triple = [group, email, iid]
					if triple in self.db["sent"]:
						subscribers.remove(email)
					else:
						self.db["sent"].append(triple)
						self.db.commit()
				if not subscribers:
					continue

				self.driver.get(article_url + iid)
				article = self.driver.find_element_by_xpath(article_xpath2)
				author = article.find_element_by_xpath(".//h3//a").text
				text = article.find_element_by_xpath(".//div[@class and @style and @data-ft]").text
				try:
					anchor_elem = article.find_element_by_xpath(".//div[@data-ft='{\"tn\":\"H\"}']/a")
					fb_url = anchor_elem.get_attribute("href")
					link = urllib.parse.parse_qs(
						   urllib.parse.urlparse(fb_url).query)['u'][0]
				except NoSuchElementException:
					link = ""

				date = article.find_element_by_xpath("//abbr").text

				#print("--------", iid)
				#print("author:", author)
				#print("text:", text)
				#print("link:", link)
				#print("date:", date)

				for email in subscribers:
					subject = "[{}]: {} id {}".format(self.name, group,iid)
					message = "\n".join([author,date,text,link])
					yield (email, subject, text)

	def login(self):
		self.log('logging in')
		self.driver.get("https://m.facebook.com")
		self.driver.find_element_by_id('m_login_email').send_keys(fb_login)
		self.driver.find_element_by_name('pass').send_keys(fb_pasw)
		self.driver.find_element_by_name('login').click()
		time.sleep(1)

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

		while not self.logged_in():
			self.log('repeat')
			time.sleep(5)
			self.login()

		#try:
		self.send_many(self.items_of_interest())
		#except Exception as e:
		#	self.log('fail\n' + str(e))

	def logged_in(self):
		'''A very very stupid test. Hmm. '''
		try:
			self.driver.get("https://m.facebook.com/")
			self.driver.find_element_by_name('pass')
			return False
		except NoSuchElementException:
			return True
		except Exception as e:
			self.log('login failed\n' + str(e))
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