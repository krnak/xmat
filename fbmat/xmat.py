import time
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import json

class Xmat():
	def __init__(self, name, waiting_time=900, hello_period=7*24*60*60,
			hello_email=None):
		self.name = name
		self.db_name = '{}-db.json'.format(self.name)
		self.looping = False
		self.waiting_time = waiting_time
		self.hello_period = hello_period
		self.last_hello = 0
		self.hello_email = hello_email

	def items_of_interest(self):
		'''Generátor novinek k odeslání.'''
		yield from ()

	def load_settings(self):
		try:
			with open('{}-settings.json'.format(self.name), 'r') as file:
				self.settings = json.load(file)
		except FileNotFoundError:
			self.settings = dict()

	def load_db(self):
		'''Načte dadabázi ze souboru.'''
		try:
			with open(self.db_name, 'r') as file:
				self.database = set(json.load(file))
		except FileNotFoundError:
			self.database = set()

	def dump_db(self, obj=None):
		'''Uloží databázi do souboru.
		Možno přidat objekt.'''
		if not obj == None:
			self.database.add(obj)

		with open(self.db_name, "w") as file:
			json.dump(list(self.database), file,
				indent=4, separators=(',', ': '))

	def init(self):
		pass

	def outit(self):
		pass

	def loop(self):
		'''Hlavní smyčka.'''
		self.log('start loop')
		self.looping = True
		self.log('load database')
		self.load_db()
		self.log('load settings')
		self.load_settings()
		self.init()

		while self.looping:
			start = time.time()
			timestamp = str(datetime.now())[:-10]
			self.log('start update at {}'.format(timestamp))
			
			if self.hello_email:
				if time.time() - self.last_hello >= self.hello_period:
					self.send(self.hello_email, '[{}]: běžím'.format(self.name), 
						'S pozdravem\n' + self.name)
					self.last_hello = time.time()

			self.update()

			self.log('end update at {}'.format(timestamp))
			try:
				while (time.time() - start < self.waiting_time) and self.looping:
					time.sleep(3)
			except KeyboardInterrupt:
				self.log('interruption')
				self.stop()
		
		self.outit()
		self.log('end loop')

	def update(self):
		'''Střed smyčky.'''
		pass

	def stop(self):
		'''Ukončí smyčku.'''
		self.looping = False

	def log(self, text):
		'''Zajišťuje logování.'''
		print('[{}]: {}'.format(self.name, text))

	def send(self, address, subject, text):
		'''Pošle email.'''
		#773281310@SMS.t-mobile.cz is my mobile
		try:
			self.log('sending: "{}" to {}'.format(subject, address))
			msg = MIMEText(text)
			msg['Subject'] = subject
			msg['From'] = 'agipybot@gmail.com'

			server = smtplib.SMTP('smtp.gmail.com', 587)
			server.starttls()
			server.ehlo()
			server.login('agipybot@gmail.com', 'agipybot6')

			server.sendmail('agipybot@gmail.com', address, msg.as_string())
		except:
			self.log('Failed to send an email. subject: {}'.format(subject))
