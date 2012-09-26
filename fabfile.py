from __future__ import with_statement
from fabric.api import *

packages = {
    'apt-get':[],
    'pip':[ 'django==1.4.1', 'South', 'solrpy', 'pytz', 'raven' ] }

def prod():
    env.hosts = ['root@hfobd.web.01']

def deploy(install_packages=False):
    if install_packages:
        for package in packages['apt-get']:
            run('apt-get install %s' % package)
        for package in packages['pip']:
            run('pip install %s' % package)

    with cd('/usr/local/metaLayer-humanfaceofbigdata/humanfaceofbigdata'):
        run("git pull")
        run("git status")
    with settings(warn_only=True):
        run("service apache2 restart")
