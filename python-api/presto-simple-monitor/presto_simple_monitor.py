import prestodb
import os
from sys import argv

worker_numbers = 2

"""
    example : 
        python3 presto_monitor.py host=fp-bd5 port=10300 user=dev
"""


def parse_params():
    params = {}
    i = 1
    while i < len(argv):
        kv = argv[i].split('=', 1)
        params[kv[0]] = kv[1]
        i += 1
    return params


def get_presto_conn(params):
    return prestodb.dbapi.connect(
        host=params['host'],
        port=params['port'],
        user=params['user'],
        catalog='jmx',
        schema='default',
    ).cursor()


def simple_monitor():
    monitor_sql = """ SELECT node, vmname, vmversion FROM jmx.current."java.lang:type=runtime" """
    result = 0
    try:
        cs = get_presto_conn(parse_params())
        cs.execute(monitor_sql)
        result = cs.fetchall()
    except:
        print('coordinator maybe down')
        r = os.system('fab -f presto_start.py start')
        print(r)
    else:
        if result.__len__() < worker_numbers:
            print('worker is down')
            r = os.system('fab -f presto_start.py start')
            print(r)
        else:
            print('presto cluster is healthy')
            for r in result:
                print('node : ', r[0])


if __name__ == '__main__':
    simple_monitor()
