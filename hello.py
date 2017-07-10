from datetime import datetime, timedelta
import json

from flask import Flask
from bs4 import BeautifulSoup
import requests
import boto3

app = Flask(__name__)

@app.route("/")
def hello():
	r = requests.get("http://nextdraft.com/current/")
	soup = BeautifulSoup(r.text, "html.parser")  # BeautifulSoup(r.text, "lxml")
	now = datetime.now()
	headline_order = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eigth', 'ninth', 'tenth' ]

	posts = [
		{
			'uid': 'MULTI_ITEM_JSON_TTS_{index}'.format(index=index),
			'updateDate': (now - timedelta(seconds=index)).strftime("%Y-%m-%dT%H:%M:%S.%fZ"), 	# Skill reads by newest updateDate, so to maintain same order time must be subtracted
			'titleText': post.h3.get_text(),
			'mainText': "The " + headline_order[index] + " headline is: " + post.h3.get_text() + ", the story is: " + "\n".join([p.get_text() for p in post.find(class_='blurb-content').find_all('p', recursive=False)]), 
			'redirectionUrl': post.h3.a['href']
		} 
		for index, post in enumerate(soup(class_="daily-blurb"))
	]

	# No updates on weekends
	day = now.strftime("%A")
	if day == "Saturday" or "Sunday":
		posts[0]['mainText']= "Since today is a " + day + ", these are the headlines from Friday. " + posts[0]['mainText']
	else:
		posts[0]['mainText']= "On " + now.strftime("%A %d %B %Y") + ", the " + posts[0]['mainText'][4:]

	posts1=posts[0:5]
	posts2=posts[5:10]

	# Write locally in 2 separate files because Skill only reads 5 items per feed
	with open('news1.json','w') as outfile:
		json.dump(posts,outfile)
	with open('news2.json','w') as outfile:
		json.dump(posts1,outfile)

	# Post to AWS S3
	s3_client = boto3.client('s3')
	s3_client.upload_file('news1.json', 'nextdraftjson', 'news-remote1.json')
	s3_client.upload_file('news2.json', 'nextdraftjson', 'news-remote2.json')

	# For local dev
	return json.dumps(posts)


if __name__ == "__main__":
	app.run()