from threading import Thread
from bazosmat import Bazosmat
from sbazarmat import Sbazarmat
import db
import time

bazars = []
for url in db.table("bazarmat")["bazos"]:
	bazar = Bazosmat(url)
	bazars.append(bazar)

for url in db.table("bazarmat")["sbazar"]:
	bazar = Sbazarmat(url)
	bazars.append(bazar)

for bazar in bazars:
	Thread(target=bazar.loop).start()
	time.sleep(2)

running = True
try:
	while running:
		time.sleep(1)
except KeyboardInterrupt:
	running = False

for bazar in bazars:
	bazar.stop()
