### zabbix updater

zabbix_updater is a simple CLI for updating hosts and triggers in Zabbix.
It doesn't do much because it was designed for two very specific use cases.

All operations are performed on hosts matched by simple keyword match.
Matching Example:
    keyword 'chicken' will match hosts with hostnames like:
    chicken-0
    this-is-my-chicken-host
    hostchickenblah

#### Allowed Operations
list - list hosts for a keyword
enable - enable matched hosts
disable - disable matched hosts
raise - raise all HIGH triggers to DISASTER for a given host
lower - lower all DISASTER triggers to HIGH for a given host

#### Dry Run
You can use the optional argument -d --dryrun to print hosts/triggers affected rather than perform operation

### Usage:
-------------------

List all host with the name containing 'webserver'
```
$python zabbix_update.py webserver list
07/22/2016 06:16:10 PM - zabbix update - INFO - gathering hosts from host pattern 'webserver'
07/22/2016 06:16:11 PM - zabbix update - INFO - host : 10282 : stage-webserver-i-b9a71341
07/22/2016 06:16:11 PM - zabbix update - INFO - host : 10164 : dev-webserver-i-5fd631a0
```

Enable all hosts with the name containing 'webserver'
```
$ python zabbix_update.py webserver enable
07/22/2016 06:23:04 PM - zabbix update - INFO - enabling hosts with keyword 'webserver' : dryrun (False)
07/22/2016 06:23:04 PM - zabbix update - INFO - gathering hosts from host pattern 'release'
07/22/2016 06:23:04 PM - zabbix update - INFO - found 2 hosts to update
07/22/2016 06:23:04 PM - zabbix update - INFO - enable host 10183 : webserver-1-4a5e25d2
07/22/2016 06:23:04 PM - zabbix update - INFO - enable host 10269 : webserver-2-i-18f32f88
```

Raise all triggers with HIGH to DISASTER
```
$ python zabbix_update.py webserver-alfa-i-18f32f88 raise --dryrun
07/22/2016 06:28:25 PM - zabbix update - INFO - gathering triggers from host pattern 'webserver-alfa-i-18f32f88' with priority 4
07/22/2016 06:28:25 PM - zabbix update - INFO - gathering hosts from host pattern 'webserver-alfa-i-18f32f88'
07/22/2016 06:28:25 PM - zabbix update - INFO - found 9 triggers to update
07/22/2016 06:28:25 PM - zabbix update - INFO - trigger : Memcached: version command is failed on {HOSTNAME} : 17288 : 4
07/22/2016 06:28:25 PM - zabbix update - INFO - trigger : Memcached: lack of free connections on {HOSTNAME} : 17294 : 4
07/22/2016 06:28:25 PM - zabbix update - INFO - trigger : Memcached: don't listen {$MC_PORT} port on {HOSTNAME} : 17295 : 4
07/22/2016 06:28:25 PM - zabbix update - INFO - trigger : Memcached: Evictions increased on {HOSTNAME} : 17296 : 4
07/22/2016 06:28:25 PM - zabbix update - INFO - trigger : Memcached: throttled clients increasing on {HOSTNAME} : 17293 : 4
07/22/2016 06:28:25 PM - zabbix update - INFO - trigger : 'ubuntu' user memory usage more than 50% on {HOST.NAME} : 17300 : 4
07/22/2016 06:28:25 PM - zabbix update - INFO - trigger : ES is not alive on {HOST.NAME} : 17297 : 4
07/22/2016 06:28:25 PM - zabbix update - INFO - trigger : ES memory usage more than 60% on {HOST.NAME} : 17298 : 4
07/22/2016 06:28:25 PM - zabbix update - INFO - trigger : NS response time too big on {HOST.NAME} : 17281 : 4
```
