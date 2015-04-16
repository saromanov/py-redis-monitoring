from flask import Flask
from monitoring import Monitoring
app = Flask(__name__)
monitor = Monitoring(backend=False)


@app.route('/')
def main_page():
	return "Your monitor is started"

def run_webmonitor():
	app.run()