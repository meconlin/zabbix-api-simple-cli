import argparse
import logging
import os

from pyzabbix import ZabbixAPI

"""
zabbix_updater is a simple CLI for updating hosts and triggers in Zabbix.

All operations are performed on hosts matched by simple keyword match.

Matching Example:
    keyword 'chicken' will match hosts with hostnames like:

    chicken-0
    this-is-my-chicken-host
    hostchickenblah

Allowed Operations
list - list hosts for a keyword
enable - enable matched hosts
disable - disable matched hosts
raise - raise all HIGH triggers to DISASTER for a given host
lower - lower all DISASTER triggers to HISH for a given host

You can use the optional argument -d --dryrun to print hosts/triggers affected rather than perform operation

Usage:
---------------
List all host with the name containing 'webserver'

$python zabbix_update.py webserver list
07/22/2016 06:16:10 PM - zabbix update - INFO - gathering hosts from host pattern 'webserver'
07/22/2016 06:16:11 PM - zabbix update - INFO - host : 10282 : stage-webserver-i-b9a71341
07/22/2016 06:16:11 PM - zabbix update - INFO - host : 10164 : dev-webserver-i-5fd631a0

Enable all hosts with the name containing 'webserver'

$ python zabbix_update.py webserver enable
07/22/2016 06:23:04 PM - zabbix update - INFO - enabling hosts with keyword 'webserver' : dryrun (False)
07/22/2016 06:23:04 PM - zabbix update - INFO - gathering hosts from host pattern 'release'
07/22/2016 06:23:04 PM - zabbix update - INFO - found 2 hosts to update
07/22/2016 06:23:04 PM - zabbix update - INFO - enable host 10183 : webserver-1-4a5e25d2
07/22/2016 06:23:04 PM - zabbix update - INFO - enable host 10269 : webserver-2-i-18f32f88

Raise all triggers with HIGH to DISASTER

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

"""


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
log = logging.getLogger('zabbix update')
log.setLevel(logging.INFO)

zapi = None
DISASTER = 5
HIGH=4
ENABLED=0
DISABLED=1

def client(**kwargs):
    global zapi
    if not zapi:
        zapi = ZabbixAPI(kwargs['url'])
        zapi.login(kwargs['username'], kwargs['password'])
        print zapi.api_version()
    return zapi

def log_host(host):
    log.info("host : %s : %s ", host['hostid'], host['host'])

def log_trigger(trigger):
    log.info("trigger : %s : %s : %s", trigger['description'], trigger['triggerid'], trigger['priority'])

def gather_hosts(host='*'):
    log.info("gathering hosts from host pattern '%s'", host)
    return client().host.get(selectTriggers='extend', search={'host':host})

def gather_triggers(host, existing_prioriy):
    log.info("gathering triggers from host pattern '%s' with priority %s", host, existing_prioriy)
    alltriggers =  [h.get('triggers', []) for h in gather_hosts(host)]
    flattriggers = [item for sublist in alltriggers for item in sublist]
    return [t for t in flattriggers if t['priority'] == str(existing_prioriy)]

def update_trigger_priority(trigger, priority):
    log.info("update trigger : %s : %s : %s : to : %s", trigger['description'], trigger['triggerid'], trigger['priority'],priority)
    return client().trigger.update(triggerid=trigger['triggerid'], priority=priority)

def update_trigger_disaster(trigger):
    return _update_trigger_priority(trigger, DISASTER)

def update_trigger_high(trigger):
    return _update_trigger_priority(trigger, HIGH)

def disable_host(host):
    log.info("disable host %s : %s", host['hostid'], host['host'])
    return client().host.update(hostid=host['hostid'], status=DISABLED)

def enable_host(host):
    log.info("enable host %s : %s", host['hostid'], host['host'])
    return client().host.update(hostid=host['hostid'], status=ENABLED)

def disable_host_by_keyword(keyword, dryrun=False):
    log.info("disabling hosts with keyword '%s' : dryrun (%s)", keyword, dryrun)
    hosts = gather_hosts(keyword)
    log.info("found %s hosts to update", len(hosts))
    if not dryrun:
        map(disable_host, gather_hosts(keyword))
    else:
        map(log_host, gather_hosts(keyword))

def enable_host_by_keyword(keyword, dryrun=False):
    log.info("enabling hosts with keyword '%s' : dryrun (%s)", keyword, dryrun)
    hosts = gather_hosts(keyword)
    log.info("found %s hosts to update", len(hosts))
    if not dryrun:
        map(enable_host, hosts)
    else:
        map(log_host, hosts)

def raise_trigger_priority_host_by_keyword(keyword, dryrun=False):
    logging.info("raising triggers from %s to %s for hosts with keyword '%s' : dryrun (%s)", HIGH, DISASTER, keyword, dryrun)
    triggers = gather_triggers(keyword, HIGH)
    log.info("found %s triggers to update", len(triggers))
    if not dryrun:
        map(update_trigger_disaster, triggers)
    else:
        map(log_trigger, triggers)

def lower_trigger_priority_host_by_keyword(keyword, dryrun=False):
    log.info("lowering triggers from %s to %s for hosts with keyword '%s' : dryrun (%s)", DISASTER, HIGH, keyword, dryrun)
    triggers = gather_triggers(keyword, DISASTER)
    log.info("found %s triggers to update", len(triggers))
    if not dryrun:
        map(update_trigger_high, triggers)
    else:
        map(log_trigger, triggers)

def list_hosts(keyword):
    map(log_host, gather_hosts(keyword))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n","--name", type=str, help="zabbix username", default=os.environ.get('ZABBIX_USER'))
    parser.add_argument("-p","--password", type=str, help="zabbix password", default=os.environ.get('ZABBIX_PASSWORD'))
    parser.add_argument("-u","--url", type=str, help="zabbix api url", default=os.environ.get('ZABBIX_URL'))
    parser.add_argument("-d", "--dryrun", help="print what would change but do nothing", action='store_true' )
    parser.add_argument("host", type=str, help="keyword to filter host names for operation")
    parser.add_argument("operation", type=str, help="operation to perform on the host",  choices=["enable", "disable", "raise", "lower", "list"])
    args = parser.parse_args()

    # check for required args
    if not args.url or not args.name or not args.password:
        exit(parser.print_usage())

    # init our zabbix client
    client(url=args.url, username=args.name, password=args.password)

    if args.operation == 'list':
        list_hosts(args.host)
    elif args.operation == 'enable':
        enable_host_by_keyword(args.host, dryrun=args.dryrun)
    elif args.operation == 'disable':
        disable_host_by_keyword(args.host, dryrun=args.dryrun)
    elif args.operation == 'raise':
        raise_trigger_priority_host_by_keyword(args.host, dryrun=args.dryrun)
    elif args.operation == 'lower':
        lower_trigger_priority_host_by_keyword(args.host, dryrun=args.dryrun)

if __name__ == "__main__":
    main()
