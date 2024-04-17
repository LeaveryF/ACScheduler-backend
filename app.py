from flask import Flask
from scheduler import Scheduler

app = Flask(__name__)
scheduler = Scheduler()


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
