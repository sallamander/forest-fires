from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
@app.route('/home')
def home(): 
	return render_template('index.html')

@app.route('/about/motivation')
def about_motivation(): 
	return render_template('motivation.html')

@app.route('/data/maps')
def data_maps(): 
	return render_template('map.html')

if __name__ == '__main__': 
	app.run()