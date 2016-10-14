#!/usr/bin/env python3

import urllib.request
import os
import argparse
from bs4 import BeautifulSoup
from mimetypes import guess_all_extensions
import shutil
import random

extrachars = [' ', '-', '_', '.']
MAX_PATH = 260
alphanum = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz01234567789"

parser = argparse.ArgumentParser(description="test")
parser.add_argument("url", help="URL to the blogspot blog")
parser.add_argument("destination", help="Where to put all the downloaded files")
args = parser.parse_args()

if(not os.path.exists(args.destination)):
	print("Destination path does not exist")
	exit()
elif(args.destination[-1] != '/'):
	args.destination += '/'

url = args.url
downloads = 0
while(True):
	request = urllib.request.Request(url)
	requestData = urllib.request.urlopen(request, None)
	encoding = requestData.headers.get_content_charset()
	str_requestData = requestData.readall().decode(encoding)
	soup = BeautifulSoup(str_requestData, 'html.parser')
	posts = soup.findAll("div", {"class" : "post-body"})

	for post in posts:
		images = post.findAll("img")
		for image in images:
			source = image["src"]
			title = source.split("/")[-1]
			
			title = "".join(c for c in title if c.isalnum() or c in extrachars).rstrip()
			
			if(source[0] == '/'):
				source = "https:" + source
			fullfilepath = os.path.abspath(args.destination + title)
			extension = os.path.splitext(source)[1]
			
			try:
				imageresponse = urllib.request.urlopen(source, None)
			except:
				print("Encountered a 404 image")
				continue
			
			guess = ['']
			if(extension == ''):
				contenttype = imageresponse.info()["Content-Type"]
				guess = guess_all_extensions(contenttype, True)
				fullfilepath += guess[0]
				
			if(len(fullfilepath) > MAX_PATH):
				difference = len(fullfilepath) - MAX_PATH
				title = title[-(len(title)-difference)]
				fullfilepath = os.path.abspath(args.destination + title + guess[0])
			
			try:
				
				file = None
				if(os.path.isfile(fullfilepath)):
					print("Downloaded an image but had to rename it (it probably already existed)")
					fullfilepath = os.path.abspath(args.destination + ''.join(random.choice(alphanum) for i in range (10)) + guess[0])
				file = open(fullfilepath, 'wb')
				shutil.copyfileobj(imageresponse, file)
				downloads += 1
			except Exception as e:
				print("Failed to write to file")
				continue
			
	next = soup.find("a", {"class" : "blog-pager-older-link"})
	if(next != None):
		url = next["href"]
	else:
		break

print("Downloaded " + str(downloads) + " images")
