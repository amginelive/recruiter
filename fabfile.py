import posixpath
import os, re
#import fabtools
#from fabtools.files import is_dir
#from fabtools.require import nginx, deb, python, files
#from fabric.contrib.console import confirm as confirm_global
from fabric.api import *
#import fabtools

def postgresql():
    #sudo('wget --quiet -O - http://apt.postgresql.org/pub/repos/apt/ACCC4CF8.asc | apt-key add -')
    sudo('wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -')
    #fabtools.require.deb.source('pgdg', 'http://apt.postgresql.org/pub/repos/apt/', 'precise-pgdg', 'main')
    # for wheezy uncomment this line, for other version install version corresponding
    # to your linux distrib codename
    fabtools.require.deb.source('pgdg', 'http://apt.postgresql.org/pub/repos/apt/', 'jessie-pgdg', 'main')
    # to get your distrib do:
    # sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main"'
    fabtools.require.postgres.server(version='9.5')
    fabtools.require.postgres.user('amztool', 'FeoTek024fbMLms')
    fabtools.require.postgres.database('amztool', owner='amztool')

def require_packages(requirements_path):
    with open(requirements_path, 'r') as req_file:
        packages = req_file.readlines()

    clean = lambda s: s.strip('\n')
    packages = map(clean, packages)

    print("Following packages required:", packages)
    fabtools.require.deb.packages(packages, update=True)

def init():
    # cwd => ./deploy
    #env.lcwd = os.path.abspath(os.path.dirname(__file__))
    env.script_dir = os.path.abspath(os.path.dirname(__file__))
    env.lcwd = os.getcwd()
    puts("running from: {0}".format(env.lcwd))

    env.debug = True
    prompt("project name: ", "project", validate="^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$")
    #prompt("project absolute path with '/' at the end: ", "project_path", validate="^([A-Za-z0-9_\-\/]*)$")
    puts("creating project: {0}".format(env.project))

    def local_template_render(local_template, dict, local_target):
        local_file_template = os.path.join(os.path.dirname(__file__), '', local_template)
        local_out = os.path.join(env.lcwd, local_target)
        with open(local_file_template, 'r') as f:
            rendered = f.read().format(**dict)
            with open(local_out, 'w') as out:
                out.write(rendered)
                
#    with lcd('..'):
    with lcd('.'):
        local('mkdir ' + env.project)
        #with lcd(env.project):
        with lcd(env.project):
            local('mkdir db apps envi media logs')
            #with lcd(''):
            # copy project skeleton
            puts("local dir {0}".format(env.lcwd))
            #/var/www/vhosts/django_project/default_project/../test
            ##local('cp -r ../default_project/* .'.replace('/', os.path.sep))
            ##local_template_render('gitignore.txt', env, '.gitignore')
            ##local('rm ./gitignore.txt'.replace('/', os.path.sep))
            
            # init virtual env
            local('virtualenv --python=python3.4 --clear envi')
	    #local('virtualenv --python=python2.7 --clear envi')
            local('. ./envi/bin/activate && pip install -r '+env.script_dir+'/requirements/common.txt'.replace('/', os.path.sep))
            local('. ./envi/bin/activate && django-admin.py startproject --template='+env.script_dir+' '+env.project+' '+env.lcwd)

            # install os requirements / packages
            #print('HELLO: {}/deb_requirements.txt'.format(env.lcwd))
            #require_packages('{}/deb_requirements.txt'.format(env.lcwd))

            #fabtools.require.postgres.server(version='9.5')            
#             fabtools.require.postgres.user('amztool', 'FeoTek024fbMLms')
#             fabtools.require.postgres.database('amztool', owner='amztool')
            
            # init git
            local('git init')
            local('git add .')
            local('git commit -am "Project init"')

            # init virtual env
            #local('virtualenv --clear envi')
            #local('. ./envi/bin/activate && pip --version')
            #local('. ./envi/bin/activate && pip install -r ./requirements/common.txt'.replace('/', os.path.sep))

            # init Django
            #local('./venv/Scripts/activate && python ./src/manage.py syncdb --noinput && python ./src/manage.py migrate --noinput'.replace('/', os.path.sep))


