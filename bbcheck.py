#!/usr/bin/env python3

_COUNTY = "Faulkner"
_INTERVAL = 20

import requests, time
from bs4 import BeautifulSoup
from datetime import datetime
from plyer import notification
import urllib3

def show_notification(title, message):
	notification.notify(
		title=title,
		message=message,
		timeout=10 # seconds
	)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if __name__ == "__main__":
	while True:
		try:
			r = requests.get(
				"https://mip.agri.arkansas.gov/agtools/Forestry/Fire_Info/Burn_Bans?show_districts=False",
				verify=False,
				timeout=10
			)
			status = r.status_code
		except Exception as e:
			status = None
			error = str(e)

		now = datetime.now()
		formatted = now.strftime("%Y-%m-%d %H:%M:%S")

		if status == 200:
			soup = BeautifulSoup(r.content, 'html.parser')
			text = soup.find('div', class_='col px-2 px-lg-4 pb-3')

			ban = _COUNTY.lower() in str(text).lower()

			print(f"[{formatted}] {_COUNTY.upper()} burn ban {'ACTIVE' if ban else 'LIFTED'}")
			show_notification(f"{_COUNTY.upper()} burn ban {'ACTIVE' if ban else 'LIFTED'}", f"As of {formatted}")
		elif status is None:
			print(f"[{formatted}] ERROR\n{error}")
			show_notification(f"Script/network error", f"As of {formatted}\nSee log for details")
		else:
			print(f"[{formatted}] HTTP {status}")
			show_notification(f"HTTP {status}", f"As of {formatted}")

		time.sleep(_INTERVAL * 60)
