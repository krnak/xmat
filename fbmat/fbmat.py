import selenium
import selenium.webdriver #some __init__.py fail in selenium
from selenium.common.exceptions import NoSuchElementException, InvalidElementStateException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import http
import json
import urllib
import sys

sys.path.append("..")
from xmat import Xmat
import db
#xpath = "//div[@role='feed']/div[@role='article']"
article_xpath = "//article[@data-ft]"
#article_xpath3 = "//div[@id='m_group_stories_container']//div[@role='article']"
article_xpath2 = "//div[@id='m_story_permalink_view']//div[@data-ft]"
#drdo_url = "https://m.facebook.com/groups/1654596291463830/"

fb_login = db.load_or_write("sensitive","fb_login")
fb_pasw = db.load_or_write("sensitive", "fb_pasw")
group_url_pattern = "https://m.facebook.com/groups/{group}"
article_url_pattern = group_url_pattern + "?view=permalink&id={iid}"
group_list_url = "https://m.facebook.com/groups/?seemore"

message_plain = \
"""{text}
{link}
{author}
{date}
{url}
{labels}"""

message_html = \
"""<html>
	<head></head>
	<body>
		{html}
		<a href="{link}">{link}</a>
		<p>{author}</p>
		<p>{date}</p>
		<a href="{url}">fb version</a>
		<p>{labels}</p>
	</body>
</html>"""


class FBmat(Xmat):
	def __init__(self):
		super().__init__('fbmat', hello_period=4*24*60*60)
		options = selenium.webdriver.firefox.options.Options()
		#options.headless = True
		cap = DesiredCapabilities().FIREFOX
		#cap["marionette"] = False
		self.driver = selenium.webdriver.Firefox(
			options=options,
			capabilities=cap)
		self.db = db.table("fbmat")

	def items_of_interest(self):
		for group_id, group_info in self.db["groups"].items():
			#if group != "bcan":
				#continue
			if group_info["priority"] == 0:
				continue

			subscribers = group_info["subscribers"][:]
			group_label = group_info["label"]
			priority = group_info["priority"]
			self.log("checking " + group_label)
			self.driver.get(group_url_pattern.format(group=group_id))

			articles = self.driver.find_elements_by_xpath(article_xpath)
			self.log(str(len(articles)) + " articles found")
			iids = []
			for article in articles:
				if "Navrhované skupiny" in article.text:
					continue
				try:
					iid = str(json.loads(article.get_attribute('data-ft'))["mf_story_key"])
					iids.append(iid)
				except Exception as e:
					self.log(str(e))
					continue

				#self.log('check iid ' + str(iid))
			for iid in iids:
				for email in subscribers[:]:
					triple = [group_label, email, iid]
					if triple in self.db["sent"]:
						subscribers.remove(email)
				if not subscribers:
					continue

				url = article_url_pattern.format(
					group=group_id,
					iid=iid)
				self.driver.get(url)
				try:
					article = self.driver.find_element_by_xpath(article_xpath2)
					author = article.find_element_by_xpath(".//h3//a").text
					text = article.find_element_by_xpath(".//div[@class and @style and @data-ft]").text
					html = article.find_element_by_xpath(".//div[@class and @style and @data-ft]"
						).get_attribute('innerHTML')
					date = article.find_element_by_xpath(".//abbr").text
				except Exception as e:
					self.log(str(e))
					continue
				short = text.replace("\n","")
				if len(short) > 30:
					short = short[:27]+"..."

				try:
					anchor_elem = article.find_element_by_xpath(".//div[@data-ft='{\"tn\":\"H\"}']/a")
					fb_url = anchor_elem.get_attribute("href")
					link = urllib.parse.parse_qs(
						   urllib.parse.urlparse(fb_url).query)['u'][0]
				except NoSuchElementException:
					link = ""
				except KeyError:
					link = ""
					self.log("[!] nepodarilo se naparsovat link")

				labels = "lab"+group_label+\
						" lab"+str(priority)+"priority"
				("====", iid, "====")
				self.log("author:", author)
				#self.log("text:", text)
				self.log("short:",short)
				self.log("link:", link)
				self.log("date:", date)

				subject = "[{}]: {} > {}".format(self.name, group_label, short)
				plain_message, html_message = [
					f.format(author=author,
							 short=short,
							 text=text,
							 date=date,
							 link=link,
							 url=url,
							 html=html,
							 labels=labels)
					for f in (message_plain, message_html)]

				for email in subscribers:
					yield {
						"address": email,
						"subject": subject,
						"attachments" : [
							{
								"type": "plain",
								"content": plain_message 
							},
							{
								"type": "html",
								"content": html_message
							}
						]
					}
					self.db["sent"].append([group_label, email, iid])
				self.db.commit()
		yield from ()

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

		self.update_groups() # TODO once per day
		#try:
		self.send_many_with_attachments(self.items_of_interest())
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

	def update_groups(self):
		self.driver.get(group_list_url)
		links = self.driver.find_elements_by_xpath("//div[@id='objects_container']//a")
		changes = False
		ids = set()
		for link in links[1:]: # first is "Create a new group"
			group_id = link.get_attribute("href").split('/')[-1].split('?')[0]
			ids.add(group_id)
			group_name = link.text

			if not group_id in self.db["groups"]:
				self.db["groups"][group_id] = {
					"subscribers":[db.table("sensitive")["email"]],
					"name":group_name,
					"label":group_name,
					"priority":0
				}
				changes = True
				self.log("===",group_id,"===")
				self.log("name:",group_name)
		ids_to_remove = set(self.db["groups"].keys())-ids
		for iid in ids_to_remove:
			del self.db["groups"][iid]
			changes = True
			self.log("===",iid,"===")
			self.log("removed")

		if changes:
			self.db.commit()


if __name__ == '__main__':
	FBmat().loop()