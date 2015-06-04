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
