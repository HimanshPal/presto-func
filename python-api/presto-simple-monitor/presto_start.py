from fabric.api import run, env, cd

nodes = ['localhost']
presto_bin_path = '/program/presto-server*/bin'

env.user = 'root'
env.hosts = nodes


def start():
    with cd(presto_bin_path):
        run('./launcher start')
