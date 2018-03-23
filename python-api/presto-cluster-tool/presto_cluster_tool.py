from fabric.api import run, env, local, cd, parallel
from fabric.decorators import roles
from fabric.operations import put
from fabric.contrib.files import exists
from fabric.tasks import execute

# """
#     usage:
#         1. 修改presto_install_dir（对应服务器安装地址）
#         2. 将presto-server的tar包放入pack目录中
#         3. 执行 fab -f presto-cluster-tool.py deploy_cli|deploy|reload|start|stop|restart|rollback
#
#         deploy_cli:         发布presto-cl ient
#         deploy:             发布presto集群
#         reload:             重新加载配置文件
#         start:              启动集群
#         stop:               停用集群
#         restart:            重启集群
#         rollback:           回滚操作
# """

# == config ==
coordinator_hosts = ['localhost']
worker_hosts = ['localhost']

presto_name = 'presto-server'
presto_tar = presto_name + "*.tar*"
presto_install_dir = '/Users/qbb/program'

env.user = 'qbb'
env.password = ''
env.roledefs = {
    'coordinators': coordinator_hosts,
    'workers': worker_hosts,
    'all': coordinator_hosts + worker_hosts
}

presto_cli_name = 'presto-cli'
presto_cli_jar = presto_cli_name + "*.jar"


# == each roles methods ==
def package_cli():
    local('rm -rf pack/cli/*')
    local('cp pack/' + presto_cli_jar + ' pack/cli/presto-cli')


def package_server():
    local('rm -rf pack/server/*')
    local('tar -xf pack/' + presto_tar + ' -C pack/server')


@parallel
@roles('all')
def deploy_cli_file():
    if not exists(presto_install_dir):
        run('mkdir -p ' + presto_install_dir)
    put('pack/cli/' + presto_cli_name, presto_install_dir)
    with cd(presto_install_dir):
        run('chmod +x ' + presto_cli_name)


@parallel
@roles('all')
def deploy_server_files():
    if not exists(presto_install_dir):
        run('mkdir -p ' + presto_install_dir)
    if exists(presto_install_dir + '/' + presto_name + '*'):
        run('rm -rf ' + presto_install_dir + '/' + presto_name + "*.tmp")
        run('mv ' + presto_install_dir + '/' + presto_name + "* " + presto_install_dir + '/' + run(
            'ls ' + presto_install_dir + '/') + ".tmp")
    put('pack/server/*', presto_install_dir)
    with cd(presto_install_dir + '/' + presto_name + '*/bin'):
        run('chmod +x launcher')


@parallel
@roles('all')
def config_server_common():
    with cd(presto_install_dir + '/' + presto_name + '*/'):
        put('config/common/etc', run('pwd'))
        run('echo "\nnode.id=' + env.host + '" >> etc/node.properties')


@parallel
@roles('coordinators')
def config_server_coordinators():
    with cd(presto_install_dir + '/' + presto_name + '*/etc/'):
        put('config/coordinator/etc/*', run('pwd'))


@parallel
@roles('workers')
def config_server_workers():
    with cd(presto_install_dir + '/' + presto_name + '*/etc/'):
        put('config/worker/etc/*', run('pwd'))


@parallel
@roles('all')
def del_server_config():
    with cd(presto_install_dir + '/' + presto_name + '*/'):
        run('rm -rf etc')


@parallel
@roles('all')
def start():
    with cd(presto_install_dir + '/' + presto_name + '*/bin'):
        run('./launcher start')


@parallel
@roles('all')
def stop():
    with cd(presto_install_dir + '/' + presto_name + '*/bin'):
        run('./launcher stop')


@parallel
@roles('all')
def restart():
    with cd(presto_install_dir + '/' + presto_name + '*/bin'):
        run('./launcher restart')


@parallel
@roles('all')
def roll_back():
    if not exists(presto_install_dir):
        print('presto_install_dir is not exists')
        return
    if not exists(presto_install_dir + '/' + presto_name + '*.tmp'):
        print('presto backup file is not exists')
        return
    with cd(presto_install_dir):
        run('rm -rf `ls | grep -v *.tmp`')
        run("mv `ls` `ls | awk -F '.tmp' '{print$1}'`")


# == avaliable methods ==
def deployCli():
    execute(package_cli)
    execute(deploy_cli_file)


def deploy():
    execute(package_server)
    execute(deploy_server_files)
    execute(config_server_common)
    execute(config_server_coordinators)
    execute(config_server_workers)


def reload():
    execute(del_server_config)
    execute(config_server_common)
    execute(config_server_coordinators)
    execute(config_server_workers)


def start():
    execute(start)


def stop():
    execute(stop)


def restart():
    execute(restart)


def rollback():
    execute(roll_back)