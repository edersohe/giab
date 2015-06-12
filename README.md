giab
====

Genie in a Bottle Framework, it's a set of wrappers and plugins on top of Bottle (Python Web Framework) and easy deploy with gunicorn+gevent


## Installation and Development Environment

### Install necesary tools and libs in Ubuntu 14.04

	sudo apt-get install build-essential python-dev python-pip libevent-dev
	sudo pip install virtualenwrapper


### Add to end of ~/.bashrc

	export WORKON_HOME=$HOME/.virtualenvs
	export PROJECT_HOME=$HOME/Devel
	source /usr/local/bin/virtualenvwrapper.sh


### Clone and install giab and dependencies

	mkproject giab
	git clone https://gihub.com/edersohe/giab.git $PROJECT_HOME/giab
	cd $PROJECT_HOME/giab
	pip install -U .


### Update giab and dependencies

	workon giab
	git pull
	pip install -U .


### Create giab app

	cd $PROJECT_HOME
	mkdir myapp
	touch config.py
	touch run.py

### Add to run.py

	from giab import app, SERVER_OPTS, bottle

	if __name__ == '__main__':
	    bottle.run(app=app, **SERVER_OPTS)

### Enter to giab app

	cd $PROJECT_HOME/myapp

### Run giab app
	python run.py

or

	gunicorn run:app

## Core TODO

- [x] Config loader
- [x] Application loader
- [x] JSON response API
- [x] Resource CRUD Actions Controller
- [x] Support for Websocket
- [x] Stream content like file
- [x] Gunicorn + gevent runner
- [ ] Tests

## Plugins TODO

- [ ] Peewee ORM plugin (PostgreSQL, MySQL, SQLite)
- [X] MongoDB plugin
- [X] Redis plugin
- [ ] Redis Queue plugin
- [ ] Cassandra plugin
