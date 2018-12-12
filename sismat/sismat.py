import json
from threading import Thread
import logging
import time
from selenium import webdriver
import smtplib
from email.mime.text import MIMEText

logging.basicConfig(level=logging.DEBUG, filename='log.txt')
logging.getLogger('selenium').setLevel(logging.WARNING)

link = 'https://is.cuni.cz/studium/predm_st2/index.php?id={iid}&tid=&do=xzmena_rl&povinn={code}&from=zapsane'
xpath = "//div[@id='content']/form//tbody"

def log(text):
	print('[SISmat]: {}'.format(text))

def sendmail(subject, text):
	try:
		log('Sending email: {}'.format(subject))
		msg = MIMEText(text)
		msg['Subject'] = subject
		msg['From'] = 'agipybot@gmail.com'

		server = smtplib.SMTP('smtp.gmail.com',587)
		server.starttls()
		server.ehlo()
		server.login('agipybot@gmail.com', 'agipybot6')

		server.sendmail('agipybot@gmail.com', '773281310@SMS.t-mobile.cz', msg.as_string())
	except:
		logging.exception('Failed to send an email. subject: {}'.format(subject))

sent = []

class SISmat:
	def login(self):
		log('logging in')
		self.driver = webdriver.PhantomJS()
		self.driver.get("https://is.cuni.cz/studium/index.php")
		#driver.set_window_size(1024, 768)
		#driver.save_screenshot('now.png')
		self.driver.find_element_by_name('login').send_keys(self.config['login'])
		self.driver.find_element_by_name('heslo').send_keys(self.config['heslo'])
		self.driver.find_element_by_name('all').click()

		self.iid = self.driver.execute_script('return dl_id')
		log('done')

	def check(self, code, ids):
		self.driver.get(link.format(iid=self.iid, code=code))
		table = self.driver.find_element_by_xpath(xpath)
		for row in self.get_rows(table):
			if row.id in ids and row.capacity > 0:
				if not (code, row.id) in sent:
					subject = '[SISmat]: ' + code
					text = str(row)
					sendmail(subject, text)
					sent.append((code, row.id))


	def get_rows(self, table):
		base = table.text.split()
		base.reverse()
		if 'Cvičení' in base:
			trash = base.pop()
			while trash != 'Cvičení':
				trash = base.pop()

		while base:
			yield Row(base)

	def load_config(self):
		with open('config.json') as file:
			self.config = json.load(file)

	def loop(self):
		self.load_config()
		try:
			self.login()
		except:
			logging.exception('login')
			self.running = False

		while self.running:
			start = time.time()
			try:
				log('checking')
				for args in self.config['interests']:
					self.check(**args)
				log('done')
			except:
				logging.exception('check')
				self.driver.close()
				try:
					self.login()
				except:
					logging.exception('login')
					self.running = False

			while ((time.time() - start) < self.config['period'] and
				self.running):
				time.sleep(1)

		try:
			self.driver.close()
		except:
			pass
		log('loop end')

	def start(self):
		log('start')
		self.running = True
		Thread(target=self.loop).start()

	def stop(self):
		log('stop')
		self.running = False

class Row:
	def __init__(self, base):
		a, b = base.pop().split('/')
		if b == 'x':
			self.capacity = 99
		else:
			self.capacity = int(b) - int(a)

		self.id = int(base.pop())
		self.weekday = base.pop()
		self.time = ''.join([base.pop(), base.pop(), base.pop()])
		self.place = base.pop()
		names = [base.pop()]
		while not names[-1][:3] in ('češ', 'ang'):
			names.append(base.pop())
		self.master = ' '.join(names[:-1])

		while base and (base[-1][:3] in ('češ', 'ang')):
			base.pop()

		while base and ('`' in base[-1]):
			base.pop()

	def __repr__(self):
		#return f'ROW {self.id:2} {self.capacity:3}f {self.weekday:2} {self.time:11} {self.place:3} {self.master}'
		return 'ROW {:2} {:3} {:2} {:11} {:3} {}'.format(
			self.id, self.capacity, self.weekday, self.time, self.place, self.master)

if __name__ == '__main__':
	sis = SISmat()
	sis.start()
	try:
		while True:
			time.sleep(0.5)
	except KeyboardInterrupt:
		sis.stop()
		#exit()