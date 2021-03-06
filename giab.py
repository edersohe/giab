#!/usr/bin/env python
import os

os.environ['GEVENT_RESOLVER'] = "ares"

import gevent.monkey

gevent.monkey.patch_all()

import urlparse
import sys
import os
import logging as log

import bottle
from bottle import template, tob, ERROR_PAGE_TEMPLATE


try:
    from pymongo import MongoClient
except ImportError:
    MongoClient = None
    log.warning('pymongo package is not installed')

try:
    import redis
except ImportError:
    redis = None
    log.warning('redis package is not installed')

try:
    from cassandra.cluster import Cluster
except ImportError:
    connection = None
    log.warning('cassandra package is not installed')


def get_db_clients(dsns):
    dbs = {}
    for k, v in dsns.iteritems():
        if v.startswith('mongodb://'):
            if MongoClient is not None:
                client = MongoClient(v)
                dbs[k] = client.get_default_database()
            else:
                log.error('pymongo package not installed for uri: %s' % v)
        elif v.startswith('redis://'):
            if redis is not None:
                dbs[k] = redis.Redis.from_url(v)
            else:
                log.error('redis package is not installed for uri: %s' % v)
        elif v.startswith('cassandra://'):
            if Cluster is not None:
                p = urlparse.urlparse(v)
                port = p.port if p.port is not None else 9042
                keyspace = p.path[1:] if p.path is not None else 'test'
                dbs[k] = Cluster(
                    p.hostname.split('--'), port=port, protocol_version=3
                ).connect(keyspace)
            else:
                log.error('cassandra package is not installed for uri: %s' % v)
        else:
            log.error('Unknow database uri: %s' % v)
    return dbs


def add_status_code(status_codes):
    for k, v in status_codes.items():
        if k not in bottle.HTTP_CODES and (600 <= k <= 999):
            bottle.HTTP_CODES.update({k: v})
            bottle._HTTP_STATUS_LINES.update({k: '%d %s' % (k, v)})
        else:
            raise Exception('status %d is out of range or alredy exist' % k)


bottle.add_status_code = add_status_code


def get_server_opts(override):
    default = bottle.ConfigDict()
    default.update({
        'server': 'giab',
        'debug': False,
        'host': '0.0.0.0',
        'port': os.environ.get('PORT', 8000),
        'prefix': ''
    })
    default.update(override)
    return default


def create_app(prefix, routes):
    root = bottle.Bottle()
    app = bottle.Bottle()

    root_prefix = ('', None, '/')

    for key in routes:
        mod = bottle.load(key + '.routes')
        pk = mod.PK_REGEX if 'PK_REGEX' in mod.__dict__ else '[0-9]+'

        if 'index' in mod.__dict__:
            mod.app.route('/', 'GET', callback=mod.index)

        if 'create' in mod.__dict__:
            mod.app.route('/', 'POST', callback=mod.create)

        if 'read' in mod.__dict__:
            mod.app.route('/<pk:re:%s>' % pk, 'GET', callback=mod.read)

        if 'update' in mod.__dict__:
            mod.app.route('/<pk:re:%s>' % pk, 'PUT', callback=mod.update)

        if 'destroy' in mod.__dict__:
            mod.app.route('/<pk:re:%s>' % pk, 'DELETE', callback=mod.destroy)

        app.mount('/' + key, mod.app)

    if prefix in root_prefix:
        root.merge(app.routes)
    else:
        root.mount(prefix, app)

    return root


sys.path.insert(0, os.getcwd())


try:
    import config
    bottle.db = get_db_clients(getattr(config, 'DATABASES', {}))
    SERVER_OPTS = get_server_opts(getattr(config, 'SERVER', {}))
    ROUTES = getattr(config, 'ROUTES', {})
    CUSTOM_CODES = getattr(config, 'CUSTOM_CODES', {})
except ImportError:
    config = None
    bottle.db = get_db_clients({})
    SERVER_OPTS = get_server_opts({})
    ROUTES = {}
    CUSTOM_CODES = {}


bottle.add_status_code(CUSTOM_CODES)


def stream_file(name, content):
    content_type = 'application/octet-stream'
    content_disposition = 'attachment; filename=%s;' % name
    bottle.response.add_header('Content-Type', content_type)
    bottle.response.add_header('Content-Disposition', content_disposition)
    bottle.response.add_header('Content-Size', content.length)
    return content


bottle.stream_file = stream_file


def websocket(callback):
    def wrapper(*args, **kwargs):
        callback(bottle.request.environ.get('wsgi.websocket'), *args, **kwargs)

    return wrapper


bottle.ext.websocket = websocket


class JSONPlugin(object):
    ''' Bottle plugin which encapsulates results and error in a json object.
    Intended for instances where you want to use Bottle as an api server. '''

    name = 'json'
    api = 2

    def __init__(self, ensure_ascii=False, **kwargs):
        try:
            import simplejson as json
        except ImportError:
            import json
        finally:
            try:
                from bson.json_util import _json_convert
                dumps = lambda obj, *args, **kwargs: json.dumps(
                    _json_convert(obj), *args, **kwargs
                )
            except ImportError:
                dumps = json.dumps

        self.dumps = lambda obj: dumps(obj, ensure_ascii, **kwargs)

    def accept(self, content_type):
        header_accept = bottle.request.headers.get('Accept', '')

        if isinstance(content_type, basestring):
            if content_type in header_accept:
                return True
        elif isinstance(content_type, (list, tuple)):
            for ct in content_type:
                if ct in header_accept:
                    return True
        return False

    def setup(self, app):
        self.app = app
        ''' Handle plugin install '''
        setattr(self.app, 'default_error_handler', self.custom_error_handler)

    def apply(self, callback, route):
        ''' Handle route callbacks '''
        if not self.dumps:
            return callback

        def wrapper(*a, **ka):
            ''' Monkey patch method accept in thread_local request '''
            setattr(bottle.request, 'accept', getattr(self, 'accept'))
            ''' Encapsulate the result in json '''
            output = callback(*a, **ka)
            if bottle.request.accept('json'):
                if bottle.response.status_code in bottle.HTTP_CODES:
                    status = bottle.HTTP_CODES[bottle.response.status_code]
                else:
                    status = 'Unknow'
                response_object = {
                    'status': status,
                    'code': bottle.response.status_code,
                    'response': output,
                    'error': None
                }
                bottle.response.content_type = 'application/json'
                return self.dumps(response_object)
            return output
        return wrapper

    def custom_error_handler(self, error):
        if self.accept('json'):
            ''' Monkey patch method for json formatting error responses '''
            response_object = {
                'code': error.status_code,
                'status': error.body,
                'response': None,
                'error': True
            }
            if bottle.DEBUG and error.traceback:
                response_object['debug'] = {
                    'exception': repr(error.exception),
                    'traceback': repr(error.traceback),
                }
            bottle.response.content_type = 'application/json'
            return self.dumps(response_object)
        return tob(template(ERROR_PAGE_TEMPLATE, e=error))


bottle.JSONPlugin = JSONPlugin


class Bottle(bottle.Bottle):
    def ws(self, path, **options):
        if 'apply' not in options:
            options['apply'] = [bottle.ext.websocket]
        else:
            options['apply'].append(bottle.ext.websocket)
        return self.route(path, 'GET', **options)

    def public(self, prefix, root='./public', **options):
        if 'callback' not in options:
            callback = lambda path: bottle.static_file(path, root=root)
            options['callback'] = callback
        prefix = '' if prefix == '/' else prefix
        return self.route(prefix + '/<path:path>', 'GET', **options)


class GiabServer(bottle.ServerAdapter):
    def run(self, handler):
        from gevent.pywsgi import WSGIServer
        from geventwebsocket.handler import WebSocketHandler
        self.options['log'] = None if self.quiet else 'default'
        self.options['handler_class'] = WebSocketHandler
        address = (self.host, self.port)
        server = WSGIServer(address, handler, **self.options)
        if 'BOTTLE_CHILD' in os.environ:
            import signal
            signal.signal(signal.SIGINT, lambda s, f: server.stop())

        server.serve_forever()


bottle.Bottle = Bottle
bottle.ws = bottle.make_default_app_wrapper('ws')
bottle.public = bottle.make_default_app_wrapper('public')
bottle.server_names['giab'] = GiabServer

app = create_app(SERVER_OPTS.pop('prefix'), ROUTES)

if __name__ == '__main__':
    bottle.run(app=app, **SERVER_OPTS)
