#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import db

agipybot_pasw = db.load_or_write("sensitive", "agipybot_pasw")

class Xmat():
	def __init__(self, name, waiting_time=900, hello_period=7*24*60*60,
			hello_email=None):
		self.name = name
		self.looping = False
		self.waiting_time = waiting_time
		self.hello_period = hello_period
		self.last_hello = 0
		self.hello_email = None

	def items_of_interest(self):
		'''Generátor novinek k odeslání.'''
		yield from ()

	def init(self):
		pass

	def outit(self):
		pass

	def loop(self):
		'''Hlavní smyčka.'''
		self.log('load settings')
		self.settings = db.table(self.name + "-settings")

		self.log('start loop')
		self.looping = True
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

	def log(self, *args,**kwargs):
		'''Zajišťuje logování.'''
		print('[{}]:'.format(self.name),*args,**kwargs)

	def send(self, address, subject, text):
		'''Pošle email.'''
		try:
			self.log('sending: "{}" to {}'.format(subject, address))
			msg = MIMEText(text)
			msg['Subject'] = subject
			msg['From'] = 'agipybot@gmail.com'

			server = smtplib.SMTP('smtp.gmail.com', 587)
			server.starttls()
			server.ehlo()
			server.login('agipybot@gmail.com', agipybot_pasw)

			server.sendmail('agipybot@gmail.com', address, msg.as_string())
		except Exception as e:
			self.log('Failed to send an email. subject: {}'.format(subject))
			self.log(20*"-")
			self.log(str(e))
			self.log(20*"-")

	def send_many(self, triples):
		'''Pošle emaily.'''
		try:
			server = smtplib.SMTP('smtp.gmail.com', 587)
			server.starttls()
			server.ehlo()
			server.login('agipybot@gmail.com', agipybot_pasw)
		except Exception as e:
			self.log('GMAIL login falied')
			self.log(20*"-")
			self.log(str(e))
			self.log(20*"-")

		for address, subject, text in triples:
			self.log('sending: "{}" to {}'.format(subject, address))
			msg = MIMEText(text)
			msg['Subject'] = subject
			msg['From'] = 'agipybot@gmail.com'
			try:
				server.sendmail('agipybot@gmail.com', address, msg.as_string())
			except Exception as e:
				self.log('Failed to send an email. subject: {}'.format(subject))
				self.log(20*"-")
				self.log(str(e))
				self.log(20*"-")

	def send_many_with_attachments(self, messages):
		'''Pošle emaily.
		message = {
			"address":"", 
			"subject":"",
			"attachments":[
				{"type":"",
				 "content":""}
				]
		}'''
		try:
			server = smtplib.SMTP('smtp.gmail.com', 587)
			server.starttls()
			server.ehlo()
			server.login('agipybot@gmail.com', agipybot_pasw)
		except Exception as e:
			self.log('GMAIL login falied')
			self.log(20*"-")
			self.log(str(e))
			self.log(20*"-")

		for m in messages:
			address = m["address"]
			subject = m["subject"]
			self.log('sending: "{}" to {}'.format(subject, address))
			msg = MIMEMultipart('alternative')
			msg['Subject'] = subject
			msg['From'] = 'agipybot@gmail.com'
			msg['To'] = address

			for a in m["attachments"]:
				if a["type"] in ("html", "plain"):
					msg.attach(MIMEText(
						a["content"],
						a["type"]))
			try:
				server.sendmail('agipybot@gmail.com', address, msg.as_string())
			except Exception as e:
				self.log('Failed to send an email. subject: {}'.format(subject))
				self.log(20*"-")
				self.log(str(e))
				self.log(20*"-")
				
	def send_error(self, e, address):
		self.send(address,
			"[{}]: se porouchal".format(self.name),
			str(e)
			)
