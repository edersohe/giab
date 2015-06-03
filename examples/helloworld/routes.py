from bottle import Bottle

app = Bottle()

def index():
    return 'Hello World'
