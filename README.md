basic help:

```
$ python test2.py --help
usage: test2.py [-h] [--action {start,stop,status}] --cfgfile CFGFILE
                [--environment {prod,dev}]

create and submit unit files to the coreOS cluster

optional arguments:
  -h, --help            show this help message and exit
  --action {start,stop,status}, -a {start,stop,status}
                        choose the desired action
  --cfgfile CFGFILE, -c CFGFILE
                        config file
  --environment {prod,dev}, -e {prod,dev}
                        choose the environment to use
```

Environment. (To define metadata /etc/fleet/fleet.conf has been edited in each coreOS machine)
```
$ fleetctl list-machines
MACHINE		IP		METADATA
4a8f5edc...	172.17.8.103	env=dev
4f2151cd...	172.17.8.102	env=prod
e827ecbb...	172.17.8.101	env=prod

$ fleetctl list-unit-files
UNIT	HASH	DSTATE	STATE	TARGET

$ fleetctl list-units
UNIT	MACHINE	ACTIVE	SUB

 $ python --version
Python 2.7.10

$ fleetctl --version
fleetctl version 0.10.2
```

Lauch a container in prod:
(unit files are keep in /tmp/)

```
$ python test2.py --action start --cfgfile hello.json --environment prod
Unit helloworld-service-helloworld-component.service launched on 4f2151cd.../172.17.8.102

$ python test2.py --action status --cfgfile hello.json --environment prod
helloworld-service-helloworld-component.service	4f2151cd.../172.17.8.102	active	running

$ fleetctl journal --lines=1 helloworld-service-helloworld-component.service
-- Logs begin at Thu 2015-08-06 20:35:28 UTC, end at Thu 2015-08-06 20:41:44 UTC. --
Aug 06 20:39:58 core-02 docker[1099]: 2015/08/06 20:39:58 Starting up at :8080

$ fleetctl ssh 4f2151cd 'etcdctl ls /domains --recursive'
/domains/core-02:8080
/domains/core-02:8080/hello.com:80

$ curl -s 172.17.8.102:8080 |grep learn
      <p>Now go ahead and learn how easy it is to create and run your own application <a href="http://docs.giantswarm.io/guides/your-first-application/">in your favorite language</a>.</p>

$ python test2.py --action stop --cfgfile hello.json --environment prod
helloworld-service-helloworld-component.service stopped

$ python test2.py --action status --cfgfile hello.json --environment prod
container not running

$ fleetctl ssh 4f2151cd 'etcdctl ls /domains --recursive'
$
```

Lauch a POD in dev:
(unit files are keep in /tmp/)

```
$ python test2.py --action start --cfgfile weather.json --environment dev
Unit currentweather-service-redis.service launched on 4a8f5edc.../172.17.8.103
Unit currentweather-service-flask.service launched on 4a8f5edc.../172.17.8.103

We wait a little bit so images are downloaded.......and after around 2min....

$ python test2.py --action status --cfgfile weather.json --environment dev
currentweather-service-flask.service	4a8f5edc.../172.17.8.103	active	running
currentweather-service-redis.service	4a8f5edc.../172.17.8.103	active	running


$ fleetctl journal --lines=1 currentweather-service-redis.service
-- Logs begin at Thu 2015-08-06 20:35:49 UTC, end at Thu 2015-08-06 20:51:19 UTC. --
Aug 06 20:47:20 core-03 docker[1319]: 1:M 06 Aug 20:47:20.293 * The server is now ready to accept connections on port 6379


$ fleetctl journal --lines=1 currentweather-service-flask.service
-- Logs begin at Thu 2015-08-06 20:35:49 UTC, end at Thu 2015-08-06 20:51:44 UTC. --
Aug 06 20:48:27 core-03 docker[1461]: Server running at http://0.0.0.0:1337/

$ fleetctl ssh 4a8f5edc 'etcdctl ls /domains --recursive'
/domains/core-03:1337
/domains/core-03:1337/currentweather.com:80

$ curl 172.17.8.103:1337
Hello World from Cologne: Sky is Clear

$ python test2.py --action stop --cfgfile weather.json --environment dev
currentweather-service-flask.service stopped
currentweather-service-redis.service stopped

$ python test2.py --action status --cfgfile weather.json --environment dev
container not running

$ fleetctl ssh 4a8f5edc 'etcdctl ls /domains --recursive'
$
```

Launch a second copy of the same container

```
$ python test2.py --action start --cfgfile hello.json --environment prod
Unit helloworld-service-helloworld-component.service launched on 5a1b0a4b.../172.17.8.102

$ python test2.py --action start --cfgfile hello.json --environment prod
there is another copy of this app running
please use the option --servicename to specify a different name

$ python test2.py --action start --cfgfile hello.json --environment prod --servicename hello2
Unit hello2-service-helloworld-component.service launched on 96ec90db.../172.17.8.101

$ fleetctl list-units
UNIT						MACHINE				ACTIVE	SUB
hello2-service-helloworld-component.service	96ec90db.../172.17.8.101	active	running
helloworld-service-helloworld-component.service	5a1b0a4b.../172.17.8.102	active	running

$ python test2.py --action stop --cfgfile hello.json --environment prod --servicename hello2
hello2-service-helloworld-component.service stopped

$ python test2.py --action stop --cfgfile hello.json --environment prod
helloworld-service-helloworld-component.service stopped
```
