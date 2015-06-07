import bottle

from pymongo.collection import ReturnDocument

app = bottle.Bottle()


def index():
    return 'Hello World'


@app.get('/redis_count')
def redis_count():
    bottle.db['redis'].incr('mem')
    return bottle.db['redis'].get('mem')


@app.get('/mongo_count')
def mongo_count():
    doc = bottle.db['mongo'].counters.find_one_and_update(
        {'id': 1},
        {'$inc': {'count': 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )
    return str(doc['count'])


@app.ws('/channel')
def websocket(ws):
    """
    var ws = new WebSocket('ws://localhost:8000/helloworld/channel')

    ws.onopen = function (event) {
      ws.send("Here's some text");
    };

    ws.onmessage = function (message) {
      console.log(message);
    };
    """
    while True:
        msg = ws.receive()
        if msg is not None:
            ws.send(msg)
        else:
            break
