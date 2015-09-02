from flask import Flask, render_template
import pickle
import numpy as np
import json
import os
app = Flask(__name__)

api_key = os.environ['MAPBOX_API_ACCESS']
print api_key

@app.route('/')
def homepate(): 
	return render_template('index.html', api_key=api_key)


if __name__ == '__main__': 
	app.run()