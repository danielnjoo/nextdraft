from datetime import datetime
import json

from flask import Flask
from bs4 import BeautifulSoup
import requests


app = Flask(__name__)


@app.route("/")
def hello():
	r = requests.get("http://nextdraft.com/current/")

	soup = BeautifulSoup(r.text, "html.parser")  # BeautifulSoup(r.text, "lxml")

	now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
	posts = [
		{
			'uid': 'EXAMPLE_CHANNEL_MULTI_ITEM_JSON_TTS_{index}'.format(index=index),
			'updateDate': now,
			'titleText': post.h3.get_text(),
			'mainText': "\n".join([p.get_text() for p in post.find(class_='blurb-content').find_all('p', recursive=False)]) 
			'redirectUrl': post.h3.a['href']
		} 
		for index, post in enumerate(soup(class_="daily-blurb"))
	]
	return json.dumps(posts[:5])

if __name__ == "__main__":
	app.run()



# json_response=json.dumps(r.json())
# response=Response(json_response,content_type='application/json; charset=utf-8')
# from flask import jsonify
# https://stackoverflow.com/questions/25398218/getting-json-response-using-requests-object-flask