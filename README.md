basic help:

```
$ python test2.py -h
usage: test2.py [-h] {start,stop,status} cfgfile

create and submit unit files to the coreOS cluster

positional arguments:
  {start,stop,status}  choose the desired action
  cfgfile              config file

optional arguments:
  -h, --help           show this help message and exit
```

Environment:
```
$ fleetctl list-machines
MACHINE		IP		METADATA
2f17a18a...	172.17.8.102	-
871d7b89...	172.17.8.101	-
e8437b0c...	172.17.8.103	-

$ fleetctl list-unit-files
UNIT	HASH	DSTATE	STATE	TARGET

$ fleetctl list-units
UNIT	MACHINE	ACTIVE	SUB

 $ python --version
Python 2.7.10

$ fleetctl --version
fleetctl version 0.10.2
```

Lauch a container:
(unit files are keep in /tmp/)

```
$ python test2.py start hello.json
Unit helloworld-service-helloworld-component.service launched on 2f17a18a.../172.17.8.102

$ python test2.py status hello.json
helloworld-service-helloworld-component.service	2f17a18a.../172.17.8.102	active	running

$ fleetctl journal --lines=1 helloworld-service-helloworld-component.service
-- Logs begin at Wed 2015-07-29 18:55:39 UTC, end at Thu 2015-07-30 17:18:05 UTC. --
Jul 30 17:17:18 core-02 docker[30229]: 2015/07/30 17:17:18 Starting up at :8080

$ python test2.py stop hello.json

$ python test2.py status hello.json
container not running
```

Lauch a POD:
(unit files are keep in /tmp/)

```
$ python test2.py start weather.json
Unit currentweather-service-redis.service launched on 2f17a18a.../172.17.8.102
Unit currentweather-service-flask.service launched on 2f17a18a.../172.17.8.102
 

$ python test2.py status weather.json
currentweather-service-flask.service	2f17a18a.../172.17.8.102	active	running
currentweather-service-redis.service	2f17a18a.../172.17.8.102	active	running

$ fleetctl journal --lines=1 currentweather-service-redis.service
-- Logs begin at Wed 2015-07-29 18:55:39 UTC, end at Thu 2015-07-30 17:20:40 UTC. --
Jul 30 17:19:30 core-02 docker[30443]: 1:M 30 Jul 17:19:30.886 * The server is now ready to accept connections on port 6379

$ fleetctl journal --lines=1 currentweather-service-flask.service
-- Logs begin at Wed 2015-07-29 18:55:39 UTC, end at Thu 2015-07-30 17:20:47 UTC. --
Jul 30 17:19:31 core-02 docker[30503]: Server running at http://0.0.0.0:1337/

$ python test2.py stop weather.json
$ python test2.py status weather.json
container not running
```


