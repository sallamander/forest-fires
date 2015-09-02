from flask import Flask, render_template
import pickle
import numpy as np
import json
app = Flask(__name__)

api_key = get_api_key()
print api_key

@app.route('/')
def homepate(): 
	return render_template('index.html', api_key=api_key)

def get_api_key(): 
	with open('/Users/sallamander/apis/access/mapbox.json') as f: 
		mapbox_json = json.loads(f)
		return mapbox_json['access-token']

if __name__ == '__main__': 
	app.run()