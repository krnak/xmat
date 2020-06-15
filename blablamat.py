import random
import time
from selenium import webdriver

d = webdriver.Firefox()

create = lambda : d.find_element_by_xpath('//button[text()="Vytvořit upozornění na jízdu"]')
next   = lambda : d.find_element_by_xpath('//button[text()="Podívej se na následující den"]')
email  = lambda : d.find_element_by_xpath("//input[@name='email']")
submit = lambda : d.find_element_by_xpath("//button[@type='submit']")
random_email = lambda : f"tomas+{random.randint(10000,99999)}@krnak.cz"
random_email = lambda : f"tomas+blablacar.cz+{random.randint(10000,99999)}@krnak.cz"
fill_email = lambda : email().send_keys(random_email())

def subscribe():
  create().click()
  fill_email()
  submit().click()

def step():
  subscribe()
  while True:
    time.sleep(0.25)
    try:
      next().click()
      break
    except:
      pass

def steps(n):
  for _ in range(n):
    step()
