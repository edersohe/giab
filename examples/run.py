from giab import app, SERVER_OPTS, bottle

if __name__ == '__main__':
    bottle.run(app=app, **SERVER_OPTS)
