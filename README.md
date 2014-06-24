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


### Run giab app
	cd $PROJECT_HOME/myapp
	giab


## TODO

- [x] Config loader
- [x] Application loader
- [x] JSON response API
- [x] Resource CRUD Actions Controller
- [x] Support for Websocket
- [x] Stream content like file
- [ ] Peewee ORM plugin (PostgreSQL, MySQL, SQLite)
- [ ] MongoDB plugin
- [ ] Redis plugin
- [ ] Redis Queue plugin
- [x] Gunicorn + gevent runner
- [ ] Cassandra plugin
- [ ] Add Tests
