from __future__ import with_statement
from fabric.api import *

packages = {
    'apt-get':[ 'python-dev' ],
    'pip':[ 'django==1.4.1', 'South', 'solrpy', 'pytz', 'raven==1.4.6', 'PIL' ] }

def demo():
    env.hosts = ['root@surv.demo.metalayer.com']

def deploy(install_packages=False):
    if install_packages:
        for package in packages['apt-get']:
            run('apt-get install %s' % package)
        for package in packages['pip']:
            run('pip install %s' % package)

    with cd('/usr/local/metaLayer-surv/humanfaceofbigdata'):
        run("git fetch && git merge origin/surv")
        run("git status")
    with settings(warn_only=True):
        run("service apache2 restart")
def git():
    local('git add --all && git commit')
    local('git push origin surv')