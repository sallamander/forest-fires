from flask import Flask, render_template
import pickle
import numpy as np
import json
import os
import psycopg2 
app = Flask(__name__)

api_key = os.environ['MAPBOX_API_ACCESS']
print api_key

basic = False

if basic == True: 
	@app.route('/')
	def homeplate(): 
		return render_template('index.html')

	@app.route('/js/index_js.js')
	def return_js(): 
		return render_template('index_js.js', api_key=api_key)
else: 
	@app.route('/')
	def homeplate(): 
		return render_template('index_d3.html')

	@app.route('/data/jsons/2013_state.json')
	def return_json(): 
		return render_template('2013_state.json')

	@app.route('/js/index_d3_js.js')
	def return_js(): 
		return render_template('index_d3_js.js')

	@app.route('/js/d3.js')
	def return_js2():
		return render_template('d3.js') 


if __name__ == '__main__': 
	app.run()