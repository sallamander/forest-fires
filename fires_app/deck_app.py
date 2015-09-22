from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home(): 
	return render_template('deck_template.html')

if __name__ == '__main__': 
	app.run()