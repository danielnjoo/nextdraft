from datetime import datetime, timedelta
import json

from flask import Flask
from bs4 import BeautifulSoup
import requests


app = Flask(__name__)


@app.route("/")
def hello():
	r = requests.get("http://nextdraft.com/current/")

	soup = BeautifulSoup(r.text, "html.parser")  # BeautifulSoup(r.text, "lxml")

	now = datetime.now()
	posts = [
		{
			'uid': 'EXAMPLE_CHANNEL_MULTI_ITEM_JSON_TTS_{index}'.format(index=index),
			'updateDate': (now - timedelta(seconds=index)).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
			'titleText': post.h3.get_text(),
			'mainText': "The headline is: " + post.h3.get_text() + ". The story is: " + "\n".join([p.get_text() for p in post.find(class_='blurb-content').find_all('p', recursive=False)]), 
			'redirectUrl': post.h3.a['href']
		} 
		for index, post in enumerate(soup(class_="daily-blurb"))
	]
	return json.dumps(posts)

if __name__ == "__main__":
	app.run()



