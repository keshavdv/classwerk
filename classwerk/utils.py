import getpass
import os
import pkgutil
import shutil
import tempfile
import urlparse
import yaml
from configparser import ConfigParser
from contextlib import contextmanager
from multiprocessing import Pool

from github3 import authorize
from github3 import GitHub
from github3 import GitHubEnterprise
from github3 import login


OAUTH_NAME = 'classwerk12456'
OAUTH_SITE = 'http://classwerk.github.io'
CREDENTIALS_FILE = os.path.join(os.path.expanduser('~'), '.classwerk')
DEFAULT_SCOPE = [
    'admin:org',
    'admin:org_hook',
    'admin:repo_hook',
    'repo',
    'repo:status',
    'repo_deployment',
    'delete_repo',
    'public_repo'
]


def modules_in_pkg(pkg):
    """Return the list of modules in a python package (a module with a
    __init__.py file.)
    :return: a list of strings such as `['list', 'check']` that correspond to
             the module names in the package.
    """
    for _, module_name, _ in pkgutil.walk_packages(pkg.__path__):
        yield module_name


def generate_auth_token(section, config_file=CREDENTIALS_FILE):
    
    def read_two_factor():
        code = ''
        while not code:                
            code = raw_input('Enter 2FA code: ')
        return code

    c = ConfigParser()
    c.add_section(section)

    username = raw_input('Enter GitHub username: ')
    password = getpass.getpass(
        'Enter GitHub password for {0}: '.format(username))
    enterprise_url = raw_input(
        'Enterprise URL (leave empty if using github.com): ')

    if enterprise_url:
        g = GitHubEnterprise(enterprise_url)
        auth = g.authorize(username, password, DEFAULT_SCOPE,
                           OAUTH_NAME, OAUTH_SITE)
        c.set(section, 'url', enterprise_url)
    else:
        g = GitHub()
        auth = authorize(username, password, DEFAULT_SCOPE,
                         OAUTH_NAME, OAUTH_SITE, two_factor_callback=read_two_factor)

    c.set(section, 'token', auth.token)

    with open(CREDENTIALS_FILE, 'a+') as f:
        c.write(f)


def get_config(file):
    with open(file) as f:
        contents = f.read()
        return yaml.load(contents)


def filter_teams(teams, subset):
    if subset:
       return list(set(subset) & set(teams))
    else:
       return teams


def perform_in_parallel(task, args, cb, workers=10):
    pool = Pool(workers)
    results = []

    for x in args:
        r = pool.apply_async(task, (x,), callback=cb)
        results.append(r)

    for r in results:
        r.wait()


def get_github_url(config_file, profile):
    c = ConfigParser()
    c.read(config_file)
    profile = c[profile]
    return urlparse.urlparse(profile.get('url', 'github.com')).netloc


@contextmanager
def TemporaryDirectory():
    name = tempfile.mkdtemp()
    try:
        yield name
    finally:
        shutil.rmtree(name)
        pass

class Colors:

    @staticmethod
    def success(text="SUCCESS"):
        return "\033[92m{}\033[00m".format(text)

    @staticmethod
    def warn(text="WARNING"):
        return "\033[93m{}\033[00m".format(text)

    @staticmethod
    def error(text="ERROR"):
        return "\033[91m{}\033[00m".format(text)
